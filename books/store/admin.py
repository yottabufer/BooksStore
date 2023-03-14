from django.contrib import admin
from store.models import Book, UserBookRelation


@admin.register(Book)
class AdminBooks(admin.ModelAdmin):
    pass


@admin.register(UserBookRelation)
class AdminUserBookRelation(admin.ModelAdmin):
    pass
