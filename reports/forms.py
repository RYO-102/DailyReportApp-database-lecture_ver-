from django import forms
from .models import DailyReport, Comment

class DailyReportForm(forms.ModelForm):
    class Meta:
        model = DailyReport
        fields = ['category', 'tags', 'condition', 'title', 'content', 'image']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '今日のタイトル'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': '業務内容や雑談など...'}),
            'tags': forms.CheckboxSelectMultiple(),
            'condition': forms.RadioSelect(),
        }
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'ねぎらいの言葉やアドバイスを送りましょう...'
            }),
        }