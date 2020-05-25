#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/final-project-beep-beep-boop-boop/")

from FlaskApp import app as application
application.secret_key = 'beepbeepboopboop2020beerflu'