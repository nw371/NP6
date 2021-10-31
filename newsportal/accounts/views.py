from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView


class Profile(TemplateView):
    template_name = 'accounts/profile.html'