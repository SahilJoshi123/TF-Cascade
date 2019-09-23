#!/usr/bin/python

from flask import Flask, g, request, Blueprint
import sys, csv, os, re, json
from . import app

sys.path.insert(0,app.config['LIBRARY_PATH'])

submit = Blueprint('submit', __name__)


@submit.route("/success/<successid>", methods=['GET', 'POST'])
def success(successid):
    g.res_dict = {'page_title': 'Success',
                  'msg': 'Success',
                  'status':0,
                  'id':successid}
    g.template = 'success.html'
    return 'OK'