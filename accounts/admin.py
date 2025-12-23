from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # 一覧画面で表示する項目
    list_display = ['username', 'employee_id', 'department', 'position', 'is_staff']
    
    # 詳細（編集）画面で表示する項目設定
    # Django標準の項目(UserAdmin.fieldsets)に、今回のカスタム項目を追加します
    fieldsets = UserAdmin.fieldsets + (
        ('社員情報', {'fields': ('employee_id', 'department', 'position', 'bio')}),
    )
    
    # 新規作成画面での設定
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('社員情報', {'fields': ('employee_id', 'department', 'position', 'bio')}),
    )

# カスタマイズした設定で登録
admin.site.register(CustomUser, CustomUserAdmin)