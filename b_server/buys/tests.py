from rest_framework import status
from rest_framework.test import APITestCase
from .models import Buy


class BuyTests(APITestCase):

    def setUp(self):
        buy = Buy.objects.create(number=1, user_id=1, products_id=[1])
        self.id = buy.id

    def test_create_buy(self):
        response = self.client.post('/buys/', {'number': 2, 'user_id': 2, 'products_id': [2]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Buy.objects.count(), 2)

    def test_create_existing(self):
        response = self.client.post('/buys/', {'number': 1, 'user_id': 1, 'products_id': [1]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_buy_not_exist(self):
        response = self.client.get('/buys/' + str(self.id+1) + "/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_buy(self):
        response = self.client.get('/buys/'+str(self.id)+"/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 1)
        self.assertContains(response, [1])

    def test_get_buys(self):
        response = self.client.get('/buys/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_existing(self):
        response = self.client.patch('/buys/'+str(self.id)+"/", {'products_id': [2]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Buy.objects.count(), 1)
        self.assertEqual(Buy.objects.get().products_id, [2])

    def test_patch_not_exist(self):
        response = self.client.patch('/buys/' + str(self.id+1) + "/", {'number':1, 'products_id': [2]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_delete_buy(self):
        response = self.client.delete('/buys/'+str(self.id)+"/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(not response.data)

