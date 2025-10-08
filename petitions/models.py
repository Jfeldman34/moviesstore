from django.db import models
from django.contrib.auth.models import User

class Petition(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def yes_votes(self):
        return self.votes.filter(value=True).count()

    def no_votes(self):
        return self.votes.filter(value=False).count()

    def __str__(self):
        return f"{self.id} - {self.title}"


class PetitionVote(models.Model):
    petition = models.ForeignKey(Petition, related_name="votes", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.BooleanField()  # True = Yes, False = No
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('petition', 'user')
