from django.db.models import Count, Case, When, Avg
from django.test import TestCase
from store.serializers import BooksSerializer
from store.models import Book, UserBookRelation
from django.contrib.auth.models import User


class BookSerializersTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='user1', first_name='first_name1', last_name='last_name2')
        self.user2 = User.objects.create(username='user2', first_name='first111', last_name='last222')
        self.book1 = Book.objects.create(name='Book1', price=11, author_name='author1', owner=self.user1)
        self.book2 = Book.objects.create(name='Book2', price=22, author_name='author2')

        UserBookRelation.objects.create(user=self.user1, book=self.book1, like=True, rate=5)
        UserBookRelation.objects.create(user=self.user1, book=self.book2, like=False, rate=2)
        UserBookRelation.objects.create(user=self.user2, book=self.book1, like=False, rate=3)
        UserBookRelation.objects.create(user=self.user2, book=self.book2, like=False, rate=5)

    def test_ok(self):
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))).order_by('pk')
        data = BooksSerializer(books, many=True).data

        expected_data = [
            {
                'pk': self.book1.pk,
                'name': 'Book1',
                'price': 11,
                'author_name': 'author1',
                'annotated_likes': 1,
                'rating': '4.00',
                'owner_name': 'user1',
                'readers': [
                    {
                        'first_name': 'first_name1',
                        'last_name': 'last_name2'
                    },
                    {
                        'first_name': 'first111',
                        'last_name': 'last222'
                    }
                ]
            },
            {
                'pk': self.book2.pk,
                'name': 'Book2',
                'price': 22,
                'author_name': 'author2',
                'annotated_likes': 0,
                'rating': '3.50',
                'owner_name': '',
                'readers': [
                    {
                        'first_name': 'first_name1',
                        'last_name': 'last_name2'
                    },
                    {
                        'first_name': 'first111',
                        'last_name': 'last222'
                    }
                ]
            },

        ]
        self.assertEqual(expected_data, data)
