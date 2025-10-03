from django.urls import path
from .views import EssenceListCreateView

urlpatterns = [
    path('essences/', EssenceListCreateView.as_view(), name='essence-list-create'),
]