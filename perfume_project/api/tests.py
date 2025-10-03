from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Essence

class EssenceApiTests(APITestCase):
    def test_get_essence_list(self):
        """
        Ensure we can retrieve the list of essences.
        """
        # Create a sample essence
        Essence.objects.create(name='Bergamot', note_type='TOP', description='A fresh citrus scent.')

        url = reverse('essence-list-create')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Bergamot')