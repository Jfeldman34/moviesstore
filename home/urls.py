from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name='home.index'),
    path('about', views.about, name='home.about'),
    ##You can add pages to individual apps. You needn't change the whole app
    path('dog', views.dog, name='home.dog'),
    
]