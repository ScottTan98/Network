from sqlite3 import Timestamp
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass
 
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.CharField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)
    like = models.ManyToManyField(User, blank=True, related_name="liked_user")

    def __str__(self):
        return f"{self.user}: {self.content}"

class Follower(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower", default=None)
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following", default=None)

    def __str__(self):
        return f"{self.follower} --> {self.following}"






