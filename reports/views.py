from django.shortcuts import render
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