from django.conf.urls import url
# from recipe.views import RecipeListView

from . import views

urlpatterns = [
    url(r'add/$', views.RecipeCreateView.as_view(), name='recipe_add'),
    # url(r'^$', views.index, name='index'),
    # url(r'^specifics/(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^$', views.RecipeListView.as_view(), name='recipe-list'),
]
