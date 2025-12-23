from django.shortcuts import render, get_object_or_404
from django.db.models import F # 【追加】データベースレベルでの演算用
from .models import DailyReport

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