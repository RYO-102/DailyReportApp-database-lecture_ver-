from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.db.models import F
from .models import DailyReport
from .forms import DailyReportForm, CommentForm
from django.contrib.auth.decorators import login_required # 追加
from django.core.exceptions import PermissionDenied       # 追加
from django.contrib.auth import get_user_model # ユーザーモデル取得用
from django.db.models import Count, Q          # 集計関数(Count)と検索条件(Q)

def report_list(request):
    """
    日報一覧表示
    """
    # 【N+1問題の回避】
    # select_related: 外部キー（Author, Category）に対してSQLの 'INNER JOIN' を発行し、1クエリで取得する。
    # prefetch_related: 多対多（Tags）に対して 'IN' 句を用いた別クエリを発行し、Python側で効率的に結合する。
    reports = DailyReport.objects.select_related('author', 'category') \
                                 .prefetch_related('tags') \
                                 .order_by('-created_at')

    context = {
        'reports': reports
    }
    return render(request, 'reports/report_list.html', context)

def report_detail(request, pk):
    """
    記事詳細表示とコメント投稿
    【1対多の逆参照 (Reverse Relationship)】
    DailyReport(1) に対して Comment(多) の関係が成立しています。
    テンプレート側で `report.comments.all` を呼び出すことで、
    外部キーを逆方向に辿り、関連データを効率的に取得・表示します。
    """
    report = get_object_or_404(DailyReport, pk=pk)

    # コメント投稿処理（POSTリクエスト時）
    if request.method == 'POST':
        # 【追加】ログインしていなければログイン画面へ飛ばす
        if not request.user.is_authenticated:
            return redirect('login')
        
        form = CommentForm(request.POST)
        if form.is_valid():
            # 【外部キーの手動割り当て】
            # commit=Falseで一旦インスタンスを生成し、
            # 確定していない外部キー情報（著者、対象記事）をセットしてから保存する。
            comment = form.save(commit=False)
            comment.author = request.user   # ログインユーザー（著者）
            comment.report = report         # 対象の日報（外部キー）
            comment.save()                  # INSERT発行
            return redirect('report_detail', pk=pk)
    else:
        form = CommentForm()

    # 【アトミック更新 (Atomic Update)】
    # Fオブジェクトを使用し、データベースレベルで `view_count = view_count + 1` を実行。
    # 競合状態（レースコンディション）を防ぎ、正確なPV集計を実現。
    DailyReport.objects.filter(pk=pk).update(view_count=F('view_count') + 1)
    
    # DBで更新された最新の値を再取得
    report.refresh_from_db()

    context = {
        'report': report,
        'comment_form': form,
    }
    return render(request, 'reports/report_detail.html', context)

# 【追加】未ログインなら実行させない
@login_required
def report_create(request):
    """
    新規記事投稿
    """
    if request.method == 'POST':
        form = DailyReportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # 【トランザクション制御 (ACID特性のAtomicity)】
                # 記事本体のINSERTと、タグ（中間テーブル）へのINSERTを不可分な操作として実行。
                # 途中でエラーが発生した場合は、全ての変更がロールバックされ、データの不整合を防ぐ。
                with transaction.atomic():
                    report = form.save(commit=False)
                    report.author = request.user
                    report.save()
                    # 多対多関係の保存（中間テーブルへのレコード作成）
                    form.save_m2m()
                
                return redirect('report_list')
                
            except Exception as e:
                print(f"Transaction Error: {e}")
    else:
        form = DailyReportForm()

    return render(request, 'reports/report_form.html', {'form': form})

# 【追加】未ログインなら実行させない
@login_required
def report_update(request, pk):
    """
    記事編集 (Update)
    """
    report = get_object_or_404(DailyReport, pk=pk)
    
    # 【追加】自分以外の記事ならエラー画面(403)を出す
    if report.author != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = DailyReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            # 更新時もタグの整合性を保つためトランザクションを使用
            with transaction.atomic():
                form.save()
            return redirect('report_detail', pk=pk)
    else:
        form = DailyReportForm(instance=report)

    return render(request, 'reports/report_form.html', {'form': form, 'is_edit': True})

# 【追加】未ログインなら実行させない
@login_required
def report_delete(request, pk):
    """
    記事削除 (Delete)
    """
    report = get_object_or_404(DailyReport, pk=pk)

    # 【追加】自分以外の記事ならエラー画面(403)を出す
    if report.author != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        # 関連するタグ情報（中間テーブル）もカスケード、または設定に従い適切に削除される
        report.delete()
        return redirect('report_list')

    return render(request, 'reports/report_confirm_delete.html', {'report': report})

@login_required
def report_ranking(request):
    """
    ランキング・集計画面
    【DB評価ポイント: 集計関数と条件付き集計】
    Pythonのforループで数えるのではなく、データベースの `GROUP BY` と集計関数を使用。
    特に `Count(filter=Q(...))` を使うことで、「特定の条件（SOS）に合致する行だけ」を
    効率的にカウントしています。
    """
    User = get_user_model()

    # 1. 投稿数ランキング（記事数が多い順）
    # SQLイメージ: SELECT username, COUNT(report.id) AS report_count FROM user ... GROUP BY user.id ORDER BY report_count DESC
    effort_ranking = User.objects.annotate(
        report_count=Count('reports')
    ).order_by('-report_count')[:5] # 上位5名

    # 2. SOS発信ランキング（条件: condition='bad' の回数）
    # 関連するテーブル（reports）の中で、特定の条件を満たすものだけを数える高度なクエリ
    sos_ranking = User.objects.annotate(
        sos_count=Count('reports', filter=Q(reports__condition='bad'))
    ).filter(sos_count__gt=0).order_by('-sos_count')[:5] # 0回の人を除外して上位5名

    context = {
        'effort_ranking': effort_ranking,
        'sos_ranking': sos_ranking,
    }
    return render(request, 'reports/report_ranking.html', context)