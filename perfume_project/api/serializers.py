from rest_framework import serializers
from .models import Essence, Perfume, UserProfile

class EssenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Essence
        fields = ['id', 'name', 'note_type', 'description']