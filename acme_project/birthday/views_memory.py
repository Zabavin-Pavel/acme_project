# birthday/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy

from .forms import BirthdayForm
from .utils import calculate_birthday_countdown
from .models import Birthday


# Создаём миксин.
class BirthdayMixin:
    model = Birthday
    success_url = reverse_lazy('birthday:list')


class BirthdayFormMixin:
    form_class = BirthdayForm


# Наследуем класс от встроенного ListView:
class BirthdayListView(ListView):
    # Указываем модель, с которой работает CBV...
    model = Birthday
    # ...сортировку, которая будет применена при выводе списка объектов:
    ordering = 'id'
    # ...и даже настройки пагинации:
    paginate_by = 1 


class BirthdayCreateView(BirthdayMixin, BirthdayFormMixin, CreateView):
    pass


class BirthdayUpdateView(BirthdayMixin, BirthdayFormMixin, UpdateView):
    pass


class BirthdayDeleteView(BirthdayMixin, DeleteView):
    pass 


class BirthdayDetailView(DetailView):
    model = Birthday

    def get_context_data(self, **kwargs):
        # Получаем словарь контекста:
        context = super().get_context_data(**kwargs)
        # Добавляем в словарь новый ключ:
        context['birthday_countdown'] = calculate_birthday_countdown(
            # Дату рождения берём из объекта в словаре context:
            self.object.birthday
        )
        # Возвращаем словарь контекста.
        return context 


# class BirthdayCreateView(CreateView):
#     # Указываем модель, с которой работает CBV...
#     model = Birthday
#     # Этот класс сам может создать форму на основе модели!
#     # Нет необходимости отдельно создавать форму через ModelForm.
#     # Указываем поля, которые должны быть в форме:
#     # fields = '__all__'
#     form_class = BirthdayForm
#     # Явным образом указываем шаблон:
#     template_name = 'birthday/birthday.html'
#     # Указываем namespace:name страницы, куда будет перенаправлен пользователь
#     # после создания объекта:
#     success_url = reverse_lazy('birthday:list') 


# class BirthdayUpdateView(UpdateView):
#     model = Birthday
#     form_class = BirthdayForm
#     template_name = 'birthday/birthday.html'
#     success_url = reverse_lazy('birthday:list') 


def birthday(request, pk=None):
    if pk is not None:
        instance = get_object_or_404(Birthday, pk=pk)
    else:
        instance = None
    form = BirthdayForm(request.POST or None, files=request.FILES or None, instance=instance) 
    context = {'form': form}
    if form.is_valid():
        form.save()
        birthday_countdown = calculate_birthday_countdown(
            form.cleaned_data['birthday']
        )
        context.update({'birthday_countdown': birthday_countdown})
    return render(request, 'birthday/birthday.html', context)


def birthday_list(request):
    # Получаем список всех объектов с сортировкой по id.
    birthdays = Birthday.objects.order_by('id')
    # Создаём объект пагинатора с количеством 10 записей на страницу.
    paginator = Paginator(birthdays, 1)

    # Получаем из запроса значение параметра page.
    page_number = request.GET.get('page')
    # Получаем запрошенную страницу пагинатора. 
    # Если параметра page нет в запросе или его значение не приводится к числу,
    # вернётся первая страница.
    page_obj = paginator.get_page(page_number)
    # Вместо полного списка объектов передаём в контекст 
    # объект страницы пагинатора
    context = {'page_obj': page_obj}
    return render(request, 'birthday/birthday_list.html', context)


def delete_birthday(request, pk):
    instance = get_object_or_404(Birthday, pk=pk)
    form = BirthdayForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('birthday:list')
    return render(request, 'birthday/birthday.html', context)