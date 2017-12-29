from rest_framework import status
from rest_framework.test import APITestCase
from .models import Product


class ProductTests(APITestCase):

    def test_get_product_not_exist(self):

        response = self.client.get('/products/1/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_product(self):

        Product.objects.create(model='m1', year='1', country='c1')
        response = self.client.get('/products/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'm1')
        self.assertContains(response, '1')
        self.assertContains(response, 'c1')

    def test_get_products(self):

        Product.objects.create(model='m1', year='1', country='c1')
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

