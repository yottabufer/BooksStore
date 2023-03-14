import json
from django.db.models import Count, Case, When, Avg
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer
from django.contrib.auth.models import User
from django.db import connection


class BookApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')

        self.book1 = Book.objects.create(name='Book1', price=11, author_name='author1', owner=self.user)
        self.book2 = Book.objects.create(name='Book2', price=22, author_name='author1')
        self.book3 = Book.objects.create(name='Book3', price=22, author_name='Book1 author2')

        UserBookRelation.objects.create(user=self.user, book=self.book1, like=True, rate=5)

    def test_get(self):
        url = reverse('book-list')
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            self.assertEqual(2, len(queries))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
        ).order_by('pk')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], '5.00')
        self.assertEqual(serializer_data[0]['annotated_likes'], 1)

    def test_get_filter(self):
        url = reverse('book-list')
        books = Book.objects.filter(pk__in=[self.book2.pk, self.book3.pk]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
        ).order_by('pk')
        response = self.client.get(url, data={'price': 22})
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        books = Book.objects.filter(pk__in=[self.book1.pk, self.book3.pk]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
        ).order_by('pk')
        response = self.client.get(url, data={'search': 'Book1'})
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-list')
        test_data = {
            'name': 'CreateBook1',
            'price': 11,
            'author_name': 'CreateAuthor1',
        }
        json_data = json.dumps(test_data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())

        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book1.id,))
        test_data = {
            'name': self.book1.name,
            'price': 123,
            'author_name': self.book1.name
        }
        json_data = json.dumps(test_data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # self.book1 = Book.objects.get(id=self.book1.id)
        self.book1.refresh_from_db()
        self.assertEqual(123, self.book1.price)

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test_username2')

        url = reverse('book-detail', args=(self.book1.id,))
        test_data = {
            'name': self.book1.name,
            'price': 123,
            'author_name': self.book1.name
        }
        json_data = json.dumps(test_data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.book1.refresh_from_db()
        self.assertEqual(11, self.book1.price)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_username2', is_staff=True)
        url = reverse('book-detail', args=(self.book1.id,))
        test_data = {
            'name': self.book1.name,
            'price': 123,
            'author_name': self.book1.name
        }
        json_data = json.dumps(test_data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book1.refresh_from_db()
        self.assertEqual(123, self.book1.price)

    def test_delete(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Book.objects.all().count())


class UserBookRelationViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username2')

        self.book1 = Book.objects.create(name='Book1', price=11, author_name='author1', owner=self.user)
        self.book2 = Book.objects.create(name='Book2', price=22, author_name='author1')

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))

        test_data = {
            'like': True,
        }
        json_data = json.dumps(test_data)
        self.client.force_login(self.user)

        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book1)
        self.assertTrue(relation.like)

    def test_in_bookmarks(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))

        test_data = {
            'in_bookmarks': True,
        }
        json_data = json.dumps(test_data)
        self.client.force_login(self.user)

        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))

        test_data = {
            'rate': 3,
        }
        json_data = json.dumps(test_data)
        self.client.force_login(self.user)

        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book1)
        self.assertEqual(3, relation.rate)

    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))

        test_data = {
            'rate': 123,
        }
        json_data = json.dumps(test_data)
        self.client.force_login(self.user)

        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
        relation = UserBookRelation.objects.get(user=self.user, book=self.book1)
        self.assertEqual(None, relation.rate)
