from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, TemplateView, UpdateView, DeleteView, CreateView
from .forms import PostForm
from .filters import PostFilter
from .models import Post, Category, Subscriber, CategorySub, Author
from .secda import admail

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

class PostDelete(LoginRequiredMixin, DeleteView):
    template_name = 'news/delete.html'  # название шаблона
    queryset = Post.objects.all()
    success_url = 'news/'

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
        print (self.request)
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
    sbs = list(Subscriber.objects.all().values("user_id")) #вытаскиваем всех подписчиков из базы
    if user not in [d['user_id'] for d in sbs]: #проверяем есть-ли текущий юзер среди подписчиков
        Subscriber.objects.create(user_id=user) #если нет - добавляем
    casbs = list(CategorySub.objects.all().values("subscriber_id"))
    sbid = Subscriber.objects.get(user_id = user).id
    if sbid not in [d['subscriber_id'] for d in casbs]:
        Subscriber.objects.get(user_id = user).category.add(Category.objects.get(id=cat)) #подписываем юзера на текущую категорию
    #
    # отправляем письмо
    msg = EmailMultiAlternatives(
        subject=f'Вы подписались на категроию {Category.objects.get(id=cat)}',
        body='Спасибо за подписку на нашем сайте',  # сообщение с кратким описанием проблемы
        from_email=admail,  # здесь указываете почту, с которой будете отправлять (об этом попозже)
        to=[admail], # здесь список получателей. Например, секретарь, сам врач и т. д.
    )
    msg.send()
    return redirect("/news/subscribed/")
    #return HttpResponseRedirect("/news/subsribed")