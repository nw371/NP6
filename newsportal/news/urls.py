from django.urls import path
from .views import PostDetail, News, SearchNews, AddPub, PostEdit, PostDelete, \
    CategoryList, CategoryView, SubscribeCategory, send_email, IndexPage, \
    add_me_to_authors, add_to_subscribers  # импортируем наше представление

urlpatterns = [
    # path — означает путь. В данном случае путь ко всем постам у нас останется пустым, позже станет ясно, почему
    path('', IndexPage.as_view()),
    path('news/', News.as_view()),
    # т. к. сам по себе это класс, то нам надо представить этот класс в виде view. Для этого вызываем метод as_view
    path('<int:pk>', PostDetail.as_view()),
    # pk — это первичный ключ товара, который будет выводиться у нас в шаблон
    path('search/', SearchNews.as_view()),
    path('add/', AddPub.as_view(), name='pub_create'),
    path('<int:pk>/edit/', PostEdit.as_view(), name='post_edit'),
    path('<int:pk>/delete/', PostDelete.as_view(),name='post_delete'),
    path('categories/', CategoryList.as_view()),
    path('category/<int:pk>', CategoryView.as_view(), name='category_list'),
    path('subscribe/', add_to_subscribers),#, name = 'send_mail'),
    path('becomeauthor/', add_me_to_authors),
    path('subscribed/', SubscribeCategory.as_view()),

]