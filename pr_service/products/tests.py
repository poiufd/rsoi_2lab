from rest_framework import status
from rest_framework.test import APITestCase
from .models import Product


class ProductTests(APITestCase):

    def setUp(self):
        product = Product.objects.create(model='m1', year=1, country='c1', count=1)
        self.id = product.id

    def test_get_product_not_exist(self):

        response = self.client.get('/products/'+str(self.id+1)+"/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_product(self):

        response = self.client.get('/products/'+str(self.id)+"/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'm1')
        self.assertContains(response, '1')
        self.assertContains(response, 'c1')
        self.assertContains(response, 1)

    def test_get_products(self):

        response = self.client.get('/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_existing(self):
        response = self.client.patch('/products/'+str(self.id)+"/", {'count': 0}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get().count, 0)

    def test_patch_not_exist(self):
        response = self.client.patch('/products/' + str(self.id+1) + "/", {'count': 0}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

