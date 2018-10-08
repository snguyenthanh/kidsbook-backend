from django.db import models

# Create your models here.

class Post(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=False)
    content = models.TextField(blank=False)

    class Meta:
        ordering = ('created',)

class Comment(models.Model):
    text = models.CharField(max_length=100, blank=False)
    post = models.ForeignKey(Post, on_delete=models.DO_NOTHING)
