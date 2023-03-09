from rest_framework.serializers import ModelSerializer
from store.models import Book, UserBookRelation


class BooksSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class UserBookRelationSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = '__all__'
