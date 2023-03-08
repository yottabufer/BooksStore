from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    author_name = models.CharField(max_length=255)
    objects = models.Manager()

    def __str__(self):
        return f'id {self.pk}: {self.name}'
