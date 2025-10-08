from django.db import models
from django.contrib.auth.models import User
from cart.models import Order
from cart.models import Item
from django.conf import settings

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    date = models.DateTimeField(auto_now_add=True)
    day = models.DateField(auto_now_add=True)
    liked_users = models.ManyToManyField(User, related_name="liked_movies", blank=True)

class RequestedMovie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()  
    requested_at = models.DateTimeField(auto_now_add=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.title

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    rating = models.IntegerField(default=0)
    popularity = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    liked_users = models.ManyToManyField(User, blank=True, related_name='liked_reviews')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name
    
    @property
    def likes(self):
        return self.liked_users.count()

# NEW MODEL: Separate ratings from reviews
class Rating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1-10
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('movie', 'user')  # One rating per user per movie
    
    def __str__(self):
        return f"{self.user.username} - {self.movie.name}: {self.rating}/10"