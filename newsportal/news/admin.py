from django.contrib import admin

# Register your models here.
from .models import Category, Author, Post, Comment, Subscriber, CategorySub

admin.site.register(Category)
admin.site.register(Author)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Subscriber)
admin.site.register(CategorySub)