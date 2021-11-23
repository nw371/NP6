from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


class Author(models.Model):
    # cвязь «один к одному» с встроенной моделью пользователей User;
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    # рейтинг пользователя
    rating = models.SmallIntegerField(default=0, verbose_name='Рейтинг')

    def update_rating(self):
        # суммарный рейтинг каждой статьи автора
        poRe = self.post_set.aggregate(SumPostRating=Sum('rating'))
        pstrtng = 0
        pstrtng += poRe.get('SumPostRating')

        # суммарный рейтинг всех комментариев автора
        coRe = self.user.comment_set.aggregate(SumComsRating=Sum('rating'))
        cmmrtng = 0
        cmmrtng += coRe.get('SumComsRating')

        # суммарный рейтинг всех комментариев к статьям автора
        x = 0
        allPosts = Post.objects.filter(author_id=self.id).values('id')
        # сначала пробегаем через все посты автора, чтобы подцепить коменты
        for i in allPosts:
            globals()[f'p{i}'] = Comment.objects.filter(post_id=i['id']).values('rating')
            # и потом выдёргиваем рейтинги коментов
            for j in globals()[f'p{i}']:
                x = x + j['rating']

        self.rating = pstrtng * 3 + cmmrtng + x
        self.save()
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'

class Category(models.Model):
    # единственное поле: название категории. Поле должно быть уникальным
    name = models.CharField(max_length=128, unique=True, verbose_name='Название')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class Post(models.Model):
    news = 'NS'
    article = 'AL'
    TYPES = [
        (news, 'Новость'),
        (article, 'Статья')
    ]

    # поле с выбором — «статья» или «новость»
    type = models.CharField(max_length=2, choices=TYPES, default=news)
    # автоматически добавляемая дата и время создания
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    # заголовок статьи/новости
    name = models.CharField(max_length=255, verbose_name='Название')
    # текст статьи/новости
    body = models.TextField(verbose_name='Tекст')
    # рейтинг статьи/новости
    rating = models.SmallIntegerField(default=0, verbose_name='Рейтинг')

    # связь «один ко многим» с моделью Author
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Автор')
    # связь «многие ко многим» с моделью Category (с дополнительной моделью PostCategory)
    category = models.ManyToManyField(Category, through='PostCategory', verbose_name='Категория')

    def preview(self):
        preview = self.body[0:123]
        return f"{preview}..."

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'

    def get_absolute_url(self):  # добавим абсолютный путь, чтобы после создания нас перебрасывало на страницу с товаром
        return f'/news/{self.id}'


class PostCategory(models.Model):
    # связь «один ко многим» с моделью Post
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    # связь «один ко многим» с моделью Category
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    # связь «один ко многим» с моделью Post
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    # связь «один ко многим» с встроенной моделью User
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # текст комментария
    body = models.TextField()
    # дата и время создания комментария
    date = models.DateField(auto_now_add=True, verbose_name='Дата')
    # рейтинг комментария
    rating = models.SmallIntegerField(default=0, verbose_name='Рейтинг')

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

class Subscriber(models.Model):
    # связь «один ко многим» с моделью User
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Подписчик')
    category = models.ManyToManyField(Category, through='CategorySub')

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

class CategorySub(models.Model):
    category = models.ForeignKey(Category, on_delete = models.CASCADE)
    subscriber = models.ForeignKey(Subscriber, on_delete = models.CASCADE)