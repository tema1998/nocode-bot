from django.contrib.auth.models import User
from django.db import models


class Bot(models.Model):
    bot_username = models.CharField(max_length=255)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bots"
    )
    bot_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.bot_username
