from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='movies.index'),
    path('<int:id>/', views.show, name='movies.show'),
     path('<int:id>/review/create/', views.create_review,
        name='movies.create_review'),
      path('<int:id>/review/<int:review_id>/edit/',
        views.edit_review, name='movies.edit_review'),
      path('<int:id>/review/<int:review_id>/delete/',
        views.delete_review, name='movies.delete_review'),
      path('review/<int:review_id>/like/', views.like_review, name='movies.like_review'),
      path('movies/<int:id>/like/', views.like_movie, name='movies.like_movie'),
      path('request_movie/', views.request_movie, name='movies.request_movie'),
      path('delete_request/<int:request_id>/', views.delete_request, name='movies.delete_request'),
      path('<int:id>/rate/', views.rate_movie, name='movies.rate_movie'),
        path('popularity-map/', views.popularity_map, name='movies.popularity_map'),
    path('map-data/', views.map_data, name='movies.map_data'),
    path('trending/<str:region>/', views.trending_by_region, name='movies.trending_region'),
    path('<int:id>/rating/delete/', views.delete_rating, name='movies.delete_rating'),





]

