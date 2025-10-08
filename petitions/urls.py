from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='petitions.index'),
    path('create/', views.create, name='petitions.create'),
    path('<int:petition_id>/', views.show, name='petitions.show'),
    path('my-petitions/', views.my_petitions, name='petitions.my_petitions'),
    path('<int:petition_id>/delete/', views.delete_petition, name='petitions.delete'),
]