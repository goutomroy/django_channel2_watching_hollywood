# watching_hollywood

This server pulling now playing, upcoming and popular movies from TMDB everyday 5:00 am UTC time using [celery](http://celeryproject.org).
I am pulling 5 pages for every category and every page has 20 movies.
For authentication I found [firebase authentication](https://firebase.google.com/docs/auth/) interesting.
Firebase has plug & play authentication library for android, ios and javascript.
All http apis are serving asynchronously using [Django Channel 2](https://channels.readthedocs.io/en/latest/) with **AsyncHttpConsumer**.
I have two version of this project synchronous and asynchronous approach. Check branch **synchronous_version**.

#### Technology Used
1. celery==4.2.1
2. channels==2.1.3
3. daphne==2.2.2
4. Django==2.1.1
5. django-celery-beat==1.1.1
6. django-celery-results==1.0.1
7. djangorestframework==3.8.2
8. firebase-admin==2.13.0

#### Apis available
1. http://127.0.0.1:8000/api/now_playing/
2. http://127.0.0.1:8000/api/upcoming/
3. http://127.0.0.1:8000/api/popular/
4. http://127.0.0.1:8000/api/sign_in/
5. http://127.0.0.1:8000/api/watchlist_action/
6. http://127.0.0.1:8000/api/watchlist/?page=1

#### Start development server
```
python3.6 manage.py runserver
```

#### Start development Celery
```
celery -A watching_hollywood worker -B  -l info
```
