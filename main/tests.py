import json
import os
import requests
from rest_framework import status
from rest_framework.test import APITestCase


class ApiTests(APITestCase):
    base_url = 'http://127.0.0.1:8000/api'

    def test_now_playing(self):
        url = os.path.join(self.base_url, 'now_playing/')
        response = requests.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_upcoming(self):
        url = os.path.join(self.base_url, 'upcoming/')
        response = requests.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_popular(self):
        url = os.path.join(self.base_url, 'popular/')
        response = requests.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
