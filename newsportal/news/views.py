from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, TemplateView, UpdateView, DeleteView, CreateView
from .forms import PostForm
from .filters import PostFilter
from .models import Post, Category, Subscriber, CategorySub, Author
from .secda import admail
import django.dispatch

my_post_signal = django.dispatch.Signal()
class IndexPage(TemplateView):
    template_name = 'default.html'

class News(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'news/news.html'  # указываем имя шаблона, в котором будет лежать HTML, в котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'news'  # это имя списка, в котором будут лежать все объекты, его надо указать, чтобы обратиться к самому списку объектов через HTML-шаблон
    queryset = Post.objects.order_by('-date')
    paginate_by = 10

class SearchNews(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'news/search.html'  # указываем имя шаблона, в котором будет лежать HTML, в котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'search'  # это имя списка, в котором будут лежать все объекты, его надо указать, чтобы обратиться к самому списку объектов через HTML-шаблон
    queryset = Post.objects.order_by('-date')
    paginate_by = 5

    def get_context_data(self, **kwargs):  # забираем отфильтрованные объекты переопределяя метод get_context_data у наследуемого класса (привет, полиморфизм, мы скучали!!!)
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())  # вписываем наш фильтр в контекст
        return context

# создаём представление, в котором будут детали конкретного отдельного поста
class PostDetail(DetailView):
    model = Post  # модель всё та же, но мы хотим получать детали конкретно отдельного поста
    template_name = 'news/post.html'  # название шаблона будет post.html
    context_object_name = 'post'  # название объекта. в нём будет

class AddPub(CreateView): #(PermissionRequiredMixin,CreateView):
    template_name = 'news/add.html'
    form_class = PostForm
    #permission_required = ('post.add_post',)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not Author.objects.filter(user_id=self.request.user.id).exists()
        context['author'] = Author.objects.filter(user_id=self.request.user.id)
        return context

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display members that belong to a given user"""

        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

class PostEdit(UpdateView): #(PermissionRequiredMixin, UpdateView):
    template_name = 'news/edit.html'  # название шаблона будет edit.html
    form_class = PostForm
    #permission_required = ('news.edit_post',)

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not Author.objects.filter(user_id=self.request.user.id).exists()
        return context

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display members that belong to a given user"""

        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

class PostDelete(LoginRequiredMixin, DeleteView):
    template_name = 'news/delete.html'  # название шаблона    template_name = 'news/delete.html'  # название шаблона
    queryset = Post.objects.all()
    success_url = '/news/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not Author.objects.filter(user_id=self.request.user.id).exists()
        return context

class CategoryList(ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'news/categories.html'
    queryset=Category.objects.all()

class CategoryView(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'news/category.html'  # указываем имя шаблона, в котором будет лежать HTML, в котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    paginate_by = 5

    def get_context_data(self, **kwargs):  # забираем отфильтрованные объекты переопределяя метод get_context_data у наследуемого класса (привет, полиморфизм, мы скучали!!!)
        context = super().get_context_data(**kwargs)
        id = self.kwargs.get('pk')
        context['categoryview'] = Post.objects.filter(category=id).order_by('-date')  # вписываем наш фильтр в контекст
        usr = self.request.user.id
        context['not_subscriber'] = not Subscriber.objects.filter(user_id = usr, category=id).exists()
        context['category'] = Category.objects.get(id=id)
        return context

class SubscribeCategory(TemplateView):
    template_name = 'news/subscribed.html'

def add_me_to_authors(request):
    user = request.user.id
    if not Author.objects.filter(user_id=user).exists():
        Author.objects.create(user_id=user)
    return redirect('/')

@login_required
def send_email(request):
    cat = request.META.get('HTTP_REFERER')[-1] #получаем id категории из request
    user = request.user.id #получаем id залогиненого юзера

    # отправляем письмо
    msg = EmailMultiAlternatives(
        subject=f'Вы подписались на категроию {Category.objects.get(id=cat)}',
        body=f'Уважаемый {User.objects.get(id=user)}, Спасибо за подписку на нашем сайте',  # сообщение с кратким описанием проблемы
        from_email=admail,  # здесь указываете почту, с которой будете отправлять (об этом попозже)
        to=[admail], # здесь список получателей. Например, секретарь, сам врач и т. д.
    )
    msg.send()
    return redirect("/news/subscribed/")

def add_to_subscribers(request):
    user = request.user.id
    cat = request.META.get('HTTP_REFERER')[-1]
    if not Subscriber.objects.filter(user_id = user).exists():
        Subscriber.objects.create(user_id=user)
    if not Subscriber.objects.filter(user_id = user, category=cat).exists():
        Subscriber.objects.get(user_id=user).category.add(Category.objects.get(id=cat))
        send_email(request)
    return redirect('/news/subscribed/')