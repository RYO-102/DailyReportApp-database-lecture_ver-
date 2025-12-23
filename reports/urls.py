from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_list, name='report_list'),
    
    # 【追加】詳細ページ用のURL (例: reports/1/)
    # <int:pk> は「整数のIDが入るよ」という意味です
    path('<int:pk>/', views.report_detail, name='report_detail'),
]