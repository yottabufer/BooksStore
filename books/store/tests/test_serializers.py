from django.test import TestCase
from store.serializers import BooksSerializer
from store.models import Book
from django.contrib.auth.models import User


class BookSerializersTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book1 = Book.objects.create(name='Book1', price=11, author_name='author1', owner=self.user)


    def test_ok(self):
        serializer_data = BooksSerializer(self.book1).data
        expected_data = {
            'id': self.book1.id,
            'name': 'Book1',
            'price': 11,
            'author_name': 'author1',
            'owner': self.user.pk,
        }
        self.assertEqual(expected_data, serializer_data)  # TODO
