from django_filters import FilterSet, DateFilter  # импортируем filterset, чем-то напоминающий знакомые дженерики
from django_filters.rest_framework import filters

from .models import Post


# создаём фильтр
class PostFilter(FilterSet):
    name = filters.CharFilter(label='Название',field_name='name', lookup_expr='icontains')
    date = DateFilter(label='Дата',field_name="date", lookup_expr='gt')
    author__user__username = filters.CharFilter(label='Автор',field_name='author__user__username', lookup_expr='icontains')
    category__name = filters.CharFilter(label='Категория',field_name='category__name', lookup_expr='icontains')
    # Здесь в мета классе надо предоставить модель и указать поля, по которым будет фильтроваться (т. е. подбираться) информация о товарах
    class Meta:
        model = Post
        fields = {'name',
                  'date',
                  'author__user__username',
                  'category__name'}  # поля, которые мы будем фильтровать (т. е. отбирать по каким-то критериям, имена берутся из моделей)
        # fields = {'name': ['icontains'],
        #           'date': ['gt'],
        #           'author__user__username': ['icontains'],
        #           'category__name': [
        #               'icontains']}  # поля, которые мы будем фильтровать (т. е. отбирать по каким-то критериям, имена берутся из моделей)

