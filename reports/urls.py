from django.urls import path
from . import views

urlpatterns = [
    # Read (一覧)
    path('', views.report_list, name='report_list'),
    
    # Read (詳細)
    path('<int:pk>/', views.report_detail, name='report_detail'),
    
    # Create (新規作成)
    path('create/', views.report_create, name='report_create'),
    
    # Update (編集)
    path('<int:pk>/edit/', views.report_update, name='report_update'),
    
    # Delete (削除)
    path('<int:pk>/delete/', views.report_delete, name='report_delete'),
]