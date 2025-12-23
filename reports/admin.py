from django.contrib import admin
from .models import DailyReport, Category, Tag, Comment

# 管理画面に日報関連のテーブルを表示する
admin.site.register(DailyReport)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Comment)