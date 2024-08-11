from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from django.shortcuts import get_object_or_404, redirect

from .forms import BirthdayForm, CongratulationForm
from .models import Birthday, Congratulation
from .utils import calculate_birthday_countdown

from django.core.exceptions import PermissionDenied
from django.shortcuts import render

class OnlyAuthorMixin(UserPassesTestMixin):

    # Определяем метод test_func() для миксина UserPassesTestMixin:
    def test_func(self):
        # Получаем текущий объект.
        object = self.get_object()
        # Метод вернёт True или False. 
        # Если пользователь - автор объекта, то тест будет пройден.
        # Если нет, то будет вызвана ошибка 403.
        return object.author == self.request.user

    def handle_no_permission(self):
        # Здесь вы можете вызвать свой кастомный шаблон для 403 ошибки
        return render(self.request, 'core/403csrf.html', status=403)

        
class BirthdayListView(ListView):
    model = Birthday
    # По умолчанию этот класс 
    # выполняет запрос queryset = Birthday.objects.all(),
    # но мы его переопределим:
    queryset = Birthday.objects.prefetch_related(
        'tags'
    ).select_related('author')
    ordering = 'id'
    paginate_by = 10


class BirthdayCreateView(LoginRequiredMixin, CreateView):
    model = Birthday
    form_class = BirthdayForm

    def form_valid(self, form):
        # Присвоить полю author объект пользователя из запроса.
        form.instance.author = self.request.user
        # Продолжить валидацию, описанную в форме.
        return super().form_valid(form) 


class BirthdayUpdateView(OnlyAuthorMixin, UpdateView):
    model = Birthday
    form_class = BirthdayForm


class BirthdayDeleteView(OnlyAuthorMixin, DeleteView):
    model = Birthday
    success_url = reverse_lazy('birthday:list')


class BirthdayDetailView(DetailView):
    model = Birthday

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['birthday_countdown'] = calculate_birthday_countdown(
            self.object.birthday
        )
        # Записываем в переменную form пустой объект формы.
        context['form'] = CongratulationForm()
        # Запрашиваем все поздравления для выбранного дня рождения.
        context['congratulations'] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            self.object.congratulations.select_related('author')
        )
        return context

        
@login_required
def simple_view(request):
    return HttpResponse('Страница для залогиненных пользователей!')


@login_required
def add_comment(request, pk):
    # Получаем объект дня рождения или выбрасываем 404 ошибку.
    birthday = get_object_or_404(Birthday, pk=pk)
    # Функция должна обрабатывать только POST-запросы.
    form = CongratulationForm(request.POST)
    if form.is_valid():
        # Создаём объект поздравления, но не сохраняем его в БД.
        congratulation = form.save(commit=False)
        # В поле author передаём объект автора поздравления.
        congratulation.author = request.user
        # В поле birthday передаём объект дня рождения.
        congratulation.birthday = birthday
        # Сохраняем объект в БД.
        congratulation.save()
    # Перенаправляем пользователя назад, на страницу дня рождения.
    return redirect('birthday:detail', pk=pk)


# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.shortcuts import get_object_or_404
# from django.urls import reverse
# from django.views.generic import CreateView

# from .forms import CongratulationForm
# from .models import Birthday, Congratulation


# class CongratulationCreateView(LoginRequiredMixin, CreateView):
#     birthday = None
#     model = Congratulation
#     form_class = CongratulationForm

#     # Переопределяем dispatch()
#     def dispatch(self, request, *args, **kwargs):
#         self.birthday = get_object_or_404(Birthday, pk=kwargs['pk'])
#         return super().dispatch(request, *args, **kwargs)

#     # Переопределяем form_valid()
#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         form.instance.birthday = self.birthday
#         return super().form_valid(form)

#     # Переопределяем get_success_url()
#     def get_success_url(self):
#         return reverse('birthday:detail', kwargs={'pk': self.birthday.pk})