#!/usr/bin/python
activate_this = '/var/www/html/eessapp/eess_app/eess_ve_test/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
from wsgiref.handlers import CGIHandler
from eess_wa_2017_11_27 import app

CGIHandler().run(app)
