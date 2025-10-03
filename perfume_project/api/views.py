from rest_framework import generics
from .models import Essence
from .serializers import EssenceSerializer

class EssenceListCreateView(generics.ListCreateAPIView):
    """
    API view to retrieve list of essences or create a new essence.
    """
    queryset = Essence.objects.all()
    serializer_class = EssenceSerializer