from django.db import models
from django.db.models import Model
from django.urls import reverse_lazy
from django.contrib.auth.models import User
# Create your models here.

class Category(Model):
    category_name = models.CharField(max_length=200)
    category_created_at = models.DateTimeField(auto_now_add=True)
    category_updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.category_name

class Tag(Model):
    item_name = models.CharField(max_length=200)

class Item(Model):
    item_name = models.CharField(max_length=200)
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    item_desc = models.TextField()
    #item_image = models.ImageField(upload_to='menu_images/')
    item_image = models.URLField(max_length=200)
    item_created_at = models.DateTimeField(auto_now_add=True)
    item_updated_at = models.DateTimeField(auto_now=True)
    # One creator per item; many items per user
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_items')
    # Many users can favorite many items
    favorited_by = models.ManyToManyField(User, related_name='favorited_items', blank=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, 
        null=True, blank=True, related_name='items')

    is_available = models.BooleanField(default=True)
    
    tags = models.ManyToManyField(Tag, related_name='items', blank=True)

    def get_absolute_url(self):
        return reverse_lazy('menu:item_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.item_name

