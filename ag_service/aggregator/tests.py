from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse


class AggregatorTests(APITestCase):

    def test_get_exist_buys(self):
        response = self.client.get(reverse('agg1', args=[3, 4]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_not_exist_buys_by_buy(self):
        response = self.client.get(reverse('agg1', args=[3, 10]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_not_exist_buys_by_user(self):
        response = self.client.get(reverse('agg1', args=[10, 4]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_ok(self):
        response = self.client.patch(reverse('agg1', args=[3, 4]), {'products_id': [1]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_order_wrong_userid(self):
        response = self.client.patch(reverse('agg1', args=[10, 4]), {'products_id': [2]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_not_exist(self):
        response = self.client.patch(reverse('agg1', args=[3, 10]), {'products_id': [2]}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order_ok(self):
        response = self.client.patch(reverse('agg3', args=[3, 4, 3]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_order_wrong_userid(self):
        response = self.client.patch(reverse('agg3', args=[10, 4, 3]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order_not_exist(self):
        response = self.client.patch(reverse('agg3', args=[3, 10, 3]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_order_product_not_exist(self):
        response = self.client.patch(reverse('agg3', args=[3, 4, 10]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)