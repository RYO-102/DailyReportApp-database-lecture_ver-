from django import forms
from .models import DailyReport

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