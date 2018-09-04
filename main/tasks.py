import os
import requests
from django.core.cache import cache

from main.models import Movie
from watching_hollywood import celery_app
from watching_hollywood.app_static_variables import NOW_PLAYING, UPCOMING, POPULAR, TMDB_BASE_URL, TMDB_API_KEY


class BaseTask(celery_app.Task):

    abstract = True
    autoretry_for = (Exception,)
    max_retries = 3
    trail = True
    # worker_state_db
    retry_backoff = 180
    retry_backoff_max = 720
    # ignore_result = True

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        super(BaseTask, self).on_retry(exc, task_id, args, kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super(BaseTask, self).on_failure(exc, task_id, args, kwargs, einfo)


@celery_app.task(bind=True, base=BaseTask)
def data_builder(self):

    for page in range(1, 6):
        pull_page.apply_async([NOW_PLAYING, page])
    for page in range(1, 6):
        pull_page.apply_async([UPCOMING, page])
    for page in range(1, 6):
        pull_page.apply_async([POPULAR, page])


@celery_app.task(bind=True, base=BaseTask, rate_limit='30/m')
def pull_page(self, type, page):

    url = os.path.join(TMDB_BASE_URL, type)
    payload = {'api_key': TMDB_API_KEY, 'page': page}
    r = requests.get(url, params=payload)
    response = r.json()
    movies = []
    for item in response['results']:
        try:
            movie = Movie.objects.get(tmdb_id=item['id'])
            movie.tmdb_data = item
            movie.save()
        except Movie.DoesNotExist:
            movie = Movie.objects.create(tmdb_id=item['id'], tmdb_data=item)
        movies.append(movie)

    cache.set(type+'_'+str(page), movies, None)

