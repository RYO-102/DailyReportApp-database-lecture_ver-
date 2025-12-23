"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include # includeを追加
from django.conf import settings             # 追加
from django.conf.urls.static import static   # 追加

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 【追加】Django標準の認証URL（accounts/login/ や accounts/logout/ が使えるようになります）
    path('accounts/', include('django.contrib.auth.urls')),
    
    # トップページへのアクセスを reports アプリに委譲する
    path('', include('reports.urls')),
]

# 【追加】画像ファイルへのアクセス許可
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)