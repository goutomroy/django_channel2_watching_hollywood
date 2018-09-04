from rest_framework import serializers
from main.models import Movie, Watchlist


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('id', 'tmdb_id', 'tmdb_data')


class WatchlistSerializer(serializers.ModelSerializer):
    movie = MovieSerializer()

    class Meta:
        model = Watchlist
        fields = ('movie',)

