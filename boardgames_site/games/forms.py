from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author_name', 'rating', 'text']
        widgets = {
            'author_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ваше имя',
                'required': True
            }),
            'rating': forms.RadioSelect(choices=[(i, '⭐' * i) for i in range(1, 6)]),
            'text': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Ваш комментарий...',
                'rows': 4,
                'required': True
            }),
        }
        labels = {
            'author_name': 'Имя',
            'rating': 'Оценка',
            'text': 'Комментарий',
        }
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating not in [1, 2, 3, 4, 5]:
            raise forms.ValidationError('Выберите оценку от 1 до 5')
        return rating
