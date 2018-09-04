from django.contrib.auth.models import User
from rest_framework import serializers

from main.models import Movie


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('id', 'tmdb_id', 'tmdb_data')

