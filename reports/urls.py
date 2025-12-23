from django.urls import path
from . import views

urlpatterns = [
    # 一覧ページ
    path('', views.report_list, name='report_list'),
    
    # 詳細ページ
    path('<int:pk>/', views.report_detail, name='report_detail'),
    
    # 新規作成ページ
    path('create/', views.report_create, name='report_create'),
    
    # 【ここが抜けている可能性が高いです】
    # 編集ページ
    path('<int:pk>/edit/', views.report_update, name='report_update'),
    
    # 削除機能
    path('<int:pk>/delete/', views.report_delete, name='report_delete'),
]