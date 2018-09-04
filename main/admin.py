from django.contrib import admin

from main.models import UserProfile, Movie, Watchlist

admin.site.register(UserProfile)
admin.site.register(Movie)
admin.site.register(Watchlist)
