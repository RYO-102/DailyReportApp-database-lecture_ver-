from django import forms
from .models import DailyReport

class DailyReportForm(forms.ModelForm):
    class Meta:
        model = DailyReport
        # フォームに入力させるフィールドを指定
        fields = ['category', 'tags', 'condition', 'title', 'content', 'image']
        
        # 見た目を整えるためのウィジェット設定（Bootstrap風のクラス付与など）
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '今日のタイトル'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': '業務内容や雑談など...'}),
            'tags': forms.CheckboxSelectMultiple(), # タグを複数チェックボックスで選ばせる
            'condition': forms.RadioSelect(),       # 調子はラジオボタンで選ばせる
        }