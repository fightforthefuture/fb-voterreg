fb-voterreg
===========

Facebook app for voter registration

## Instructions for developing locally

Want to develop locally? Easy! Here are the steps:

* Add this line to your hosts file:

        127.0.0.1       local.voterreg.org

* syncdb, migrate, runserver
* Start celeryd with `./manage.py celeryd --loglevel=INFO`
* Access https://apps.facebook.com/258722907563918/

## Other nice utilities for developing

* Want to clear one user's data? No problem:

        ./manage.py clearuser "Holmes Wilson"

  Username must match one from Facebook. From Heroku, this is:

        heroku run 'python manage.py clearuser "Holmes Wilson"'


## Heroku Deploy (staging)

    git remote add staging git@heroku.com:voterreg-facebook-staging.git


    git push staging master
    heroku run --app=voterreg-facebook-staging ./manage.py collectstatic