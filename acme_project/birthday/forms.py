from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

from .models import Birthday, Congratulation

# class BirthdayForm(forms.Form):
#     first_name = forms.CharField(label='Имя', max_length=20)
#     last_name = forms.CharField(
#         label='Фамилия', required=False, help_text='Необязательное поле'
#     )
#     birthday = forms.DateField(
#         label='Дата рождения',
#         widget=forms.DateInput(attrs={'type': 'date'}),
#     ) 

BEATLES = {'Джон Леннон', 'Пол Маккартни', 'Джордж Харрисон', 'Ринго Старр'}


class BirthdayForm(forms.ModelForm):

    class Meta:
        model = Birthday
        exclude = ('author',)
        
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'})
        }

    def clean_first_name(self):
        # Получаем значение имени из словаря очищенных данных.
        first_name = self.cleaned_data['first_name']
        # Разбиваем полученную строку по пробелам 
        # и возвращаем только первое имя.
        return first_name.split()[0]
    
    def clean(self):
        # Вызов родительского метода clean.
        super().clean()
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        if f'{first_name} {last_name}' in BEATLES:
            # Отправляем письмо, если кто-то представляется 
            # именем одного из участников Beatles.
            send_mail(
                subject='Another Beatles member',
                message=f'{first_name} {last_name} пытался опубликовать запись!',
                from_email='birthday_form@acme.not',
                recipient_list=['admin@acme.not'],
                fail_silently=True,
            )
            raise ValidationError(
                'Мы тоже любим Битлз, но введите, пожалуйста, настоящее имя!'
            )


class CongratulationForm(forms.ModelForm):
    
    class Meta:
        model = Congratulation
        fields = ('text',)


# class BirthdayForm(forms.Form):
#     title = forms.CharField(label='Название', max_length=20)
#     description = forms.CharField(label='Описание', widget=forms.Textarea(attrs={'cols': '20', 'rows': '5'}))
#     price = forms.IntegerField(label='Цена', min_value=10, max_value=100, help_text='Рекомендованная розничная цена')
#     comment = forms.CharField(label='Комментарий', required=False, widget=forms.Textarea(attrs={'cols': '20', 'rows': '5'}))