from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма поста для блога"""
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        """Валидация текста поста"""
        new_post_text = self.cleaned_data['text']
        if len(new_post_text) < 10:
            raise forms.ValidationError('Пост слишком короткий')
        elif 'кг/ам' in new_post_text:
            raise forms.ValidationError('Слишком грубо!')
        return new_post_text


class CommentForm(forms.ModelForm):
    """Форма комментария к посту"""
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'cols': 20, 'rows': 5}),
        }

    def clean_text(self):
        """Валидация текста комментария"""
        comment_text = self.cleaned_data['text']
        if len(comment_text) > 1000:
            raise forms.ValidationError('Многабукаф')
        elif 'кг/ам' in comment_text:
            raise forms.ValidationError('Слишком грубо!')
        return comment_text
