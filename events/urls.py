from django.urls import path, include # Add include to the import statement
from . import views # Add this line

urlpatterns = [
    path('',views.home,name='home'), # Add this line
    path('events',views.vision,name='vision'),
    path('blog',views.blog,name='blog'),
    path('firstblog',views.firstblog,name='firstblog'), 
]
