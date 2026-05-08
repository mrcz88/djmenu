from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #  ImageField richiede il pacchetto Pillow
    image = models.ImageField(default='default.png', upload_to='profile_pics')
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username