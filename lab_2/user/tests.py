from rest_framework import status
from rest_framework.test import APITestCase
from .models import User


class UserTests(APITestCase):

    def setUp(self):
        user = User.objects.create(login='l1', password='p1', name='n1')
        self.id = user.id

    def test_create_user(self):
        response = self.client.post('/user/', {'login': 'l2', 'password': 'p2', 'name': 'n2'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_create_existing(self):
        response = self.client.post('/user/', {'login': 'l1', 'password': 'p1', 'name': 'n1'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_not_exist(self):

        response = self.client.get('/user/' + str(self.id+1) + "/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user(self):

        response = self.client.get('/user/' + str(self.id) + "/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'l1')
        self.assertContains(response, 'p1')
        self.assertContains(response, 'n1')

    def test_get_users(self):
        response = self.client.get('/user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)



