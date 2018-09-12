from django.contrib import admin

from main.models import UserProfile, Movie, Watchlist


class MovieAdmin(admin.ModelAdmin):

    list_display = ['id', 'tmdb_id',]
    readonly_fields = ['id']
    list_display_links = ['tmdb_id']
    ordering = ['-created',]


admin.site.register(UserProfile)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Watchlist)
