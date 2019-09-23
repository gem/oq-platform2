from django.conf.urls import patterns, url
# from django.views.generic import TemplateView
from django.contrib import admin 
from . import views

urlpatterns = [
    url(r'^$',
        views.monitoring, name='monitoring'),
]
