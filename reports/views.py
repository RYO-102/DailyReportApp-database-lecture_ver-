from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.db.models import F
from .models import DailyReport
from .forms import DailyReportForm

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
    記事詳細表示とPVカウント
    """
    report = get_object_or_404(DailyReport, pk=pk)

    # 【アトミックな更新と競合回避】
    # Pythonメモリ上での計算（report.view_count += 1）ではなく、
    # Fオブジェクトを使用してデータベース側で `UPDATE ... SET view_count = view_count + 1` を実行。
    # これにより、アクセス集中時のレースコンディション（読み書きの競合）によるカウント不整合を防ぐ。
    DailyReport.objects.filter(pk=pk).update(view_count=F('view_count') + 1)
    
    # DB側で更新された最新の値をインスタンスに再ロード
    report.refresh_from_db()

    context = {
        'report': report
    }
    return render(request, 'reports/report_detail.html', context)

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

def report_update(request, pk):
    """
    記事編集 (Update)
    """
    report = get_object_or_404(DailyReport, pk=pk)

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

def report_delete(request, pk):
    """
    記事削除 (Delete)
    """
    report = get_object_or_404(DailyReport, pk=pk)

    if request.method == 'POST':
        # 関連するタグ情報（中間テーブル）もカスケード、または設定に従い適切に削除される
        report.delete()
        return redirect('report_list')

    return render(request, 'reports/report_confirm_delete.html', {'report': report})