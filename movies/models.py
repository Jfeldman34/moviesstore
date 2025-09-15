from django.db import models
from django.contrib.auth.models import User
from cart.models import Order
from cart.models import Item

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    date = models.DateTimeField(auto_now_add=True)
    day = models.DateField(auto_now_add=True)
    def __str__(self):
        return str(self.id) + ' - ' + self.name
    
class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    rating =  models.IntegerField(default=0)
    popularity = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    liked_users = models.ManyToManyField(User, blank=True, related_name='liked_reviews')
    movie = models.ForeignKey(Movie,
        on_delete=models.CASCADE)
    user = models.ForeignKey(User,
        on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name
    @property
    def likes(self):
        return self.liked_users.count()


