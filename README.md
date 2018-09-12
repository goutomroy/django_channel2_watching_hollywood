# watching_hollywood

This server pulls now playing, upcoming and popular movies from [TMDB](https://themoviedb.org) everyday at 5:00am UTC time using [celery](http://celeryproject.org).
I am pulling and caching 5 pages of every category and every page has 20 movies.Now playing, upcoming and popular apis are serving from cache.
For authentication I found [firebase authentication](https://firebase.google.com/docs/auth/) interesting.
Firebase has plug & play authentication library for android, ios and javascript.
All http apis are serving asynchronously using [Django Channel 2](https://channels.readthedocs.io/en/latest/) with `AsyncHttpConsumer`.
I have two version of this project synchronous and asynchronous approach. Check branch `synchronous_version` for synchronous approach.

#### Apis available
1. http://127.0.0.1:8000/api/now_playing/
2. http://127.0.0.1:8000/api/upcoming/
3. http://127.0.0.1:8000/api/popular/
4. http://127.0.0.1:8000/api/sign_in/
5. http://127.0.0.1:8000/api/watchlist_action/
6. http://127.0.0.1:8000/api/watchlist/?page=1

#### Technology Used
1. celery==4.2.1
2. channels==2.1.3
4. Django==2.1.1
5. django-celery-beat==1.1.1
6. django-celery-results==1.0.1
7. djangorestframework==3.8.2
8. firebase-admin==2.13.0
9. psycopg2-binary==2.7.5

#### My experience on Celery
For scheduling task I am using `django-celery-beat`, it has admin interface to add/remove scheduling tasks. Just try to make beat checking loop `beat_max_loop_interval` to maximum you can to reduce db interactions, my one is 600 seconds.
For task result using `django-celery-results`. I used [flower](https://flower.readthedocs.io/en/latest/) before but found difficulties when using it in production.

#### Android app consuming these apis
Coming Soon!

#### Start development server
```
python3.6 manage.py runserver
```

#### Start development Celery
```
celery -A watching_hollywood worker -B  -l info
```
