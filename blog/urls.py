from django.urls import path
from . import views
urlpatterns = [
    path('blog', views.firstblog, name='firstblog'),
    path('blog1', views.blog1, name='blog1'),
    path('post_list', views.post_list, name='post_list'),
    ]
