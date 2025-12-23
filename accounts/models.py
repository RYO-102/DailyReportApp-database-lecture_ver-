from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    【講義用ポイント】
    - employee_idに `unique=True` を設定することで、DBレベルでのユニーク制約を課しています。
    - インデックスが自動生成されるため、検索パフォーマンスの話題にも触れられます。
    """
    # 社員番号（必須・重複不可）
    employee_id = models.CharField("社員番号", max_length=20, unique=True)
    
    # 部署（分析用：部署ごとのSOS発生率などを出すため）
    department = models.CharField("所属部署", max_length=100, default="開発部")
    
    # 役職（PM, メンバーなど）
    position = models.CharField("役職", max_length=50, default="メンバー")
    
    # 「人となり」を知るための自己紹介（PDFのビジョン対応）
    bio = models.TextField("自己紹介", blank=True, help_text="趣味や最近ハマっていることなど")

    class Meta:
        db_table = 'custom_user'
        verbose_name = '社員'
        verbose_name_plural = '社員'

    def __str__(self):
        return f"{self.username} ({self.department})"