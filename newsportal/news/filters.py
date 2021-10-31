from django_filters import FilterSet, DateFilter  # импортируем filterset, чем-то напоминающий знакомые дженерики
from .models import Post


# создаём фильтр
class PostFilter(FilterSet):
    date = DateFilter
    # Здесь в мета классе надо предоставить модель и указать поля, по которым будет фильтроваться (т. е. подбираться) информация о товарах
    class Meta:
        model = Post
        fields = {'name': ['icontains'],
                  'date': ['gt'],
                  'author__user__username': ['icontains'],
                  'category__name': ['contains']}  # поля, которые мы будем фильтровать (т. е. отбирать по каким-то критериям, имена берутся из моделей)

