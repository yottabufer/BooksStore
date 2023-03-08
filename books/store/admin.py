from django.contrib import admin
from store.models import Book


@admin.register(Book)
class AdminBooks(admin.ModelAdmin):
    fields = ('name', 'price', 'author_name')
