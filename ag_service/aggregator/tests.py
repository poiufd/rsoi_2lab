from rest_framework import status
from rest_framework.test import APITestCase
import unittest
from django.test import RequestFactory
from .views import *
from django.test import TestCase
from django.urls import reverse


class AggregatorTests(TestCase):
    #
    # def test_get(self):
    #     request = RequestFactory().get('http://127.0.0.1:8000/order/' + str(2) + "/")

        def setUp(self):
            #self.user = UserFactory()
            self.factory = RequestFactory()

        def test_get(self):
            """
            Test GET requests
            """
            request = self.factory.get(reverse('agg1',args=[2]))
            #request.user = self.user
            response = AggUserBuysView.as_view()(request,2)
            self.assertEqual(response.status_code, 200)
