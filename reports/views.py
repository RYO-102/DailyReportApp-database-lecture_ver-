from django.shortcuts import render, get_object_or_404
from django.db.models import F # 【追加】データベースレベルでの演算用
from .models import DailyReport
from django.db import transaction # 【追加】トランザクション用
from .forms import DailyReportForm # 【追加】作成したフォーム

def report_list(request):
    """
    トップページ：日報の一覧を表示する
    【講義アピールポイント】
    N+1問題を回避するため、select_related（外部キー）とprefetch_related（多対多）を使用し、
    SQLの発行回数を劇的に減らしています。
    """
    reports = DailyReport.objects.select_related('author', 'category') \
                                 .prefetch_related('tags') \
                                 .order_by('-created_at')

    context = {
        'reports': reports
    }
    return render(request, 'reports/report_list.html', context)

def report_detail(request, pk):
    """
    記事詳細ページ
    【講義アピールポイント】
    Fオブジェクトを使用することで、Python側ではなくDB側で計算を行う
    「アトミックな更新（Atomic Update）」を実装。
    レースコンディション（競合状態）を防ぎ、正確なPVカウントを実現しています。
    発行されるSQL: UPDATE reports_dailyreport SET view_count = view_count + 1 WHERE id = ...
    """
    # 記事を取得（存在しない場合は404エラーを出す）
    report = get_object_or_404(DailyReport, pk=pk)

    # PVカウントの更新 (Fオブジェクトを使用)
    DailyReport.objects.filter(pk=pk).update(view_count=F('view_count') + 1)
    
    # 更新された最新の値をDBから読み込み直す（これをしないと画面上の数字が古いままになる）
    report.refresh_from_db()

    context = {
        'report': report
    }
    return render(request, 'reports/report_detail.html', context)

def report_create(request):
    """
    記事投稿ページ
    【講義アピールポイント】
    transaction.atomic() を使用して、データの整合性を保証しています。
    もし記事の保存後にタグの保存でエラーが起きても、記事の保存ごとロールバック（取り消し）され、
    「タグのない中途半端な記事」が残ることを防ぎます。
    """
    if request.method == 'POST':
        form = DailyReportForm(request.POST, request.FILES) # 画像を含むのでFILESも渡す
        if form.is_valid():
            try:
                # トランザクション開始
                with transaction.atomic():
                    # 1. 記事本体を保存（まだDBにはコミットしない設定 commit=False）
                    report = form.save(commit=False)
                    report.author = request.user # ログイン中のユーザーを著者に設定
                    report.save() # ここで記事のIDが確定する
                    
                    # 2. 多対多のタグ情報を保存（これをやらないとタグが消える）
                    # DjangoのModelFormは、commit=Falseの場合、save_m2m()を手動で呼ぶ必要がある
                    form.save_m2m()
                    
                # 全部成功したらトップページへ
                return redirect('report_list')
                
            except Exception as e:
                # エラー時の処理（ログ出しなど）
                print(f"エラーが発生しました: {e}")
    else:
        # GETリクエストなら空のフォームを表示
        form = DailyReportForm()

    return render(request, 'reports/report_form.html', {'form': form})