from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_books')
    readers = models.ManyToManyField(User, through='UserBookRelation', related_name='books')
    objects = models.Manager()

    def __str__(self):
        return f'id {self.pk}: {self.name}'


class UserBookRelation(models.Model):
    RATE_CHOICES = [
        (1, 'Ok'),
        (2, 'Fine'),
        (3, 'Good'),
        (4, 'Amazing'),
        (5, 'Incredible'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES)
    objects = models.Manager()

    def __str__(self):
        return f'{self.user.username} -- {self.book.name} -- {self.rate}'
