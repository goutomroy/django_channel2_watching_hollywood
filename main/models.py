from django.contrib.postgres.fields import JSONField
from django.db import models
from django.contrib.auth.models import User
from watching_hollywood.app_static_variables import MEDIUM_CHAR_LENGTH


class UserProfile(models.Model):
    user = models.OneToOneField(User, unique=True, related_name='user_profile', on_delete=models.CASCADE, db_index=True)
    firebase_uid = models.CharField(max_length=MEDIUM_CHAR_LENGTH, unique=True, db_index=True, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        unique_together = ('user', 'firebase_uid')
        ordering = ('-created',)

    def __str__(self):
        return self.user.email


class Movie(models.Model):

    tmdb_id = models.IntegerField(unique=True, blank=False, null=False)
    tmdb_data = JSONField(blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        ordering = ('-created',)

    def __str__(self):
        return str(self.tmdb_id)


class Watchlist(models.Model):

    user_profile = models.ForeignKey(UserProfile, related_name='watchlist', on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, related_name='movie_in_watchlist', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user_profile', 'movie')
        ordering = ('-created',)

    def __str__(self):
        return self.movie