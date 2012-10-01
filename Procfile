web: newrelic-admin run-program hellodjango/manage.py run_gunicorn -b "0.0.0.0:$PORT" -w 3
celeryd: python manage.py celeryd -E -B --loglevel=INFO
