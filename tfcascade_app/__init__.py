#!/usr/bin/python
from datetime import datetime
from werkzeug.routing import Rule
from flask import Flask, render_template, url_for, request, jsonify, \
    send_from_directory, send_file, redirect, g, make_response, flash, \
    session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('app_conf.cfg')
db = SQLAlchemy(app)
from tfcascade_app import models

app.debug=app.config['DEBUG']
app.secret_key=app.config['SECRETKEY']

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

from . import views, models

@app.before_request
def before_start():
    g.res_dict = {'page_title': 'ERROR',
                  'msg': 'Not Available'}
    g.pagination = None
    g.template = 'index.html'
    g.input_values ={}
    with open(app.root_path+'/tmp2.txt', 'a') as FH:
            FH.write("before_start:--%s\n" % str(request))
    if request.user_agent.browser == None :
        for arg_key in request.args.keys():
            g.input_values[arg_key] = request.args[arg_key]
    else:
        for frm_key in request.form.keys():
            g.input_values[frm_key] = request.form[frm_key]
    with open(app.root_path+'/tmp2.txt', 'a') as FH:
            FH.write("before_start: ARGS--%s\n" % str(g.input_values))
    views.__log_activity()

        
@app.after_request
def prepare_results(response):
    redirection_codes = [302, 303, 304]
    if response.status_code in redirection_codes:
        return response
    if request.user_agent.browser == None :
        # g.res_dict['msg'] += " Identified as API"
        return jsonify(g.res_dict)
    if hasattr(g, 'res_dict'):
        # g.res_dict['msg'] += " Identified as %s " % (request.user_agent.browser)
        pass
    else:
        g.res_dict={'msg': 'Page requested not available'}
    if hasattr(request.url_rule, 'rule'):
        if 'static' not in request.url_rule.rule:
            if not hasattr(g, 'template'):
                g.template = 'results.html'
            response = make_response(render_template(g.template,
                                                     res_dict=g.res_dict,
                                                     pagination=g.pagination))    
    return response
    
    
def test_run(port=5000):
    app.run(host='0.0.0.0', port=port, threaded=True)
    
if __name__ == "__main__":
    app.run(host='0.0.0.0')
