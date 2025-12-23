from django.db import models
from django.conf import settings  # CustomUserを参照するため

class Category(models.Model):
    """
    【正規化（第3正規形）】
    繰り返し発生する日報の種別（業務報告、技術共有など）を別テーブルに切り出し、
    データの冗長性を排除しています。
    """
    name = models.CharField("カテゴリー名", max_length=50)
    slug = models.SlugField(unique=True, help_text="URLで使われる識別子")

    class Meta:
        verbose_name = 'カテゴリー'
        verbose_name_plural = 'カテゴリー'

    def __str__(self):
        return self.name

class Tag(models.Model):
    """
    【多対多（Many-to-Many）】
    「ゲーム」や「Python」などのタグ。
    Djangoにより裏側で中間テーブルが自動生成され、複雑な結合クエリ（JOIN）の対象になります。
    """
    name = models.CharField("タグ名", max_length=50)

    class Meta:
        verbose_name = 'タグ'
        verbose_name_plural = 'タグ'

    def __str__(self):
        return self.name

class DailyReport(models.Model):
    """
    日報データ（トランザクションテーブル）
    """
    # 【外部キー制約 (Referential Integrity)】
    # ユーザー（著者）との紐づけ。CASCADEによりユーザー削除時に日報も削除される設定。
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    
    # カテゴリー（外部キー）
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="カテゴリー")
    
    # 【多対多関係】
    # blank=True により、タグなしの投稿も許容する柔軟な設計。
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="タグ")

    # 日報の中身
    title = models.CharField("タイトル", max_length=200)
    content = models.TextField("本文")
    image = models.ImageField("画像", upload_to='uploads/', blank=True, null=True)
    
    # 【SOS検知機能】
    # 集計関数で「部署ごとの平均コンディション」などを出すのに使用
    CONDITION_CHOICES = [
        ('excellent', '絶好調！'),
        ('good', '良い'),
        ('normal', '通常通り'),
        ('tired', '少し疲れ気味'),
        ('bad', '不調/SOS'),
    ]
    condition = models.CharField(
        "本日の調子", 
        max_length=10, 
        choices=CONDITION_CHOICES, 
        default='normal'
    )
    
    # PVカウント（副問合せ・アトミック更新課題用）
    view_count = models.PositiveIntegerField("PV数", default=0)
    
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = '日報'
        verbose_name_plural = '日報'

    def __str__(self):
        return self.title

class Comment(models.Model):
    """
    【コミュニケーション機能】
    記事に対する1対多のリレーションを持つコメント機能。
    """
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField("コメント内容")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} -> {self.report.title}"