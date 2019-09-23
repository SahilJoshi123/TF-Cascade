#!/usr/bin/python\
from datetime import datetime
import re, csv, os, json, time
import scipy.stats as ss
from werkzeug.routing import Rule
from flask import Flask, render_template, url_for, request, jsonify, \
	send_from_directory, send_file, redirect, g, make_response, flash, \
	session, redirect, abort, g
from flask_paginate import Pagination, get_page_parameter, get_page_args

from flask import request

from sqlalchemy import desc, or_

from . import app, db
from .models import ExecutionHistory, ExecutionStatusMaster, MenuMaster, TFChains , TFKnowledgeExperiment, TFGeneChains



import sys
sys.setrecursionlimit(8000)

PER_PAGE = 50

@app.route("/")
def app_index():
	try:
		g.status=session['g_status']
		g.msg=session['g_msg']
	except Exception:
		pass    
	session['g_status']=None
	session['g_msg']=None
		
	return render_template('index.html',
						   page_title='')


#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/chains/<query>", methods=['GET','POST'])
@app.route("/chains/<query>/<int:page>", methods=['GET','POST'])
def browse(query=None,page=1):
	if not query:
		query = ''
	else:
		g.key = query
	g.page = request.args.get(get_page_parameter(), type=int, default=1)

	#g.mpm = TFKnowledgeExperiment.query.order_by(TFKnowledgeExperiment.kkt_id).paginate(page,app.config['PAGINATION_ITEMS'],error_out=False)
	
	# To check if query is gene name or protein name
	if 'ENSP' in query:
		g.mpm = TFChains.query.filter(TFChains.CHAIN.like('%{}%'.format(g.key))).order_by(TFChains.CHAIN_ID.desc()).paginate(page,app.config['PAGINATION_ITEMS'],error_out=False)

	else:
		g.mpm = TFGeneChains.query.filter(TFGeneChains.CHAIN.like('%{}%'.format(g.key))).order_by(TFGeneChains.CHAIN_ID.desc()).paginate(page,app.config['PAGINATION_ITEMS'],error_out=False)
	
	# g.pagination = Pagination(page=g.page, total=len(g.GeneFeatures), search=search, record_name='genefeature')
	
	g.res_dict = {'page_title': 'Gene Exp. Diff. Data',
						'msg': 'Looks OK'}
	
	g.template = 'browse.html'
	return 'OK'



@app.route("/tissuechains/<query>", methods=['GET','POST'])
@app.route("/tissuechains/<query>/<int:page>", methods=['GET','POST'])
def tissue(query=None,page=1):

	if not query:
		query = ''
	else:
		g.key = query
	g.page = request.args.get(get_page_parameter(), type=int, default=1)


	cwd = os.getcwd()
	with open(cwd+'/tfcascade_app/data/TissueCount.json', 'r') as fp:
		g.cascadeind = json.load(fp)

	g.filters = g.cascadeind[g.key]

	g.res_dict = {'page_title': 'Gene Exp. Diff. Data',
						'msg': 'Looks OK'}

	g.template = 'tissue.html'
	return 'OK'

@app.route("/chains")
@app.route("/chains/<int:page>", methods=['GET'])
def chain(page = 1):

	global searchPath
	searchPath[:] = []
	
	search = False
	q = request.args.get('q')
	if q:
		search = True


	g.page = request.args.get(get_page_parameter(), type=int, default=1)
	
	#g.mpm = TFKnowledgeExperiment.query.order_by(TFKnowledgeExperiment.kkt_id).paginate(page,app.config['PAGINATION_ITEMS'],error_out=False)
	
	g.mpm = TFChains.query.order_by(TFChains.CHAIN_ID.desc()).paginate(page,app.config['PAGINATION_ITEMS'],error_out=False)
	
	# g.pagination = Pagination(page=g.page, total=len(g.GeneFeatures), search=search, record_name='genefeature')
	
	g.res_dict = {'page_title': 'Gene Exp. Diff. Data',
						'msg': 'Looks OK'}
	
	g.template = 'chains.html'
	return 'OK'





#-----------------------------------------------------------------------------------------------------------------------------------------------------------------


@app.route("/tissues")
@app.route("/tissues/<int:page>", methods=['GET'])
def knowledge(page=1):

	cwd = os.getcwd()

	with open(cwd+'/tfcascade_app/data/TissueCount.json', 'r') as fp:
		g.cascadeind = json.load(fp)

	global searchPath
	searchPath[:] = []

	
	search = False
	q = request.args.get('q')
	if q:
		search = True

	g.page = request.args.get(get_page_parameter(), type=int, default=1)
	
	
	
	#g.mpm = TFCHAINS.query.order_by(TFCHAINS.CHAIN_ID).paginate(page,app.config['PAGINATION_ITEMS'],error_out=False)
	
	# g.pagination = Pagination(page=g.page, total=len(g.GeneFeatures), search=search, record_name='genefeature')
	
	g.res_dict = {'page_title': 'Gene Exp. Diff. Data',
						'msg': 'Looks OK'}
	
	g.template = 'knowledge.html'
	return 'OK'


#-----------------------------------------------------------------------------------------------------------------------------------------------------------------


@app.route("/genes")
@app.route("/genes/<int:page>", methods=['GET'])
def genes(page=1):

	cwd = os.getcwd()

	with open(cwd+'/tfcascade_app/data/Count.json', 'r') as fp:
		g.cascadeind = json.load(fp)

	global searchPath
	searchPath[:] = []

	search = False
	q = request.args.get('q')
	if q:
		search = True

	g.page = request.args.get(get_page_parameter(), type=int, default=1)
	
	#g.mpm = TFKnowledgeExperiment.query.order_by(TFKnowledgeExperiment.kkt_id).paginate(page,app.config['PAGINATION_ITEMS'],error_out=False)
	
	# g.pagination = Pagination(page=g.page, total=len(g.GeneFeatures), search=search, record_name='genefeature')
	
	g.res_dict = {'page_title': 'Gene Exp. Diff. Data',
						'msg': 'Looks OK'}
	
	g.template = 'genes.html'

	return 'OK'


#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

searchPath = []

@app.route("/search", methods=['GET', 'POST'])
@app.route("/search/<query>", methods=['GET', 'POST'])
@app.route("/search/<query>/<int:page>", methods=['GET','POST'])
def search(query=None, page=1):
	cwd = os.getcwd()
	path1 = request.referrer.split("/")[-1]
	path2 = request.referrer.split("/")[-2]
	path3 = request.referrer.split("/")[-3]

	if not query:
		if 'search_key' in g.input_values:
			query = g.input_values['search_key'].strip()
		else:
			query = ""

	g.query = query

	if path1 == 'search' or path3 == 'search':
		path = searchPath
		
		if path[0] == 'chains' or path[1] == 'chains':
			g.TFChains = TFChains.query.filter(or_(TFChains.CHAIN.like('%%%s%%' % query), TFChains.CHAIN_LENGTH.like('%%%s%%' % query), TFChains.CHAIN_ID.like('%%%s%%' % query))).order_by(TFChains.CHAIN_ID).paginate(page,app.config['PAGINATION_ITEMS'],error_out=False)
			
		
			g.res_dict = {'page_title': 'Checking',
						  'msg': 'Looks OK'}
			g.template = 'searchChains.html'
			return 'OK'

		if path[0] == 'genes' or path[1] == 'genes':
			g.TFGeneChains = TFGeneChains.query.filter(or_(TFGeneChains.CHAIN.like('%%%s%%' % query), TFGeneChains.CHAIN_LENGTH.like('%%%s%%' % query), TFGeneChains.CHAIN_ID.like('%%%s%%' % query))).order_by(TFGeneChains.CHAIN_ID).paginate(page,app.config['PAGINATION_ITEMS'],error_out=False)
			
			g.res_dict = {'page_title': 'Checking',
						  'msg': 'Looks OK'}
			g.template = 'searchGenes.html'
			return 'OK'    

		if path[0] == 'tissues' or path[1] == 'tissues':
			with open(cwd+'/tfcascade_app/data/TissueCount.json', 'r') as fp:
				g.cascadeind = json.load(fp)
		
			g.res_dict = {'page_title': 'Checking',
						  'msg': 'Looks OK'}
			g.template = 'searchKnowledge.html'
			return 'OK'    

	else:
		global searchPath
		searchPath[:] = []
		searchPath.append(path1)
		searchPath.append(path2)

		if searchPath[0] == 'chains' or searchPath[1] == 'chains':
			g.TFChains = TFChains.query.filter(or_(TFChains.CHAIN.like('%%%s%%' % query), TFChains.CHAIN_LENGTH.like('%%%s%%' % query), TFChains.CHAIN_ID.like('%%%s%%' % query))).order_by(TFChains.CHAIN_ID).paginate(page,app.config['PAGINATION_ITEMS'],error_out=False)
		
			g.res_dict = {'page_title': 'Checking',
						  'msg': 'Looks OK'}
			g.template = 'searchChains.html'
			return 'OK'

		if searchPath[0] == 'genes' or searchPath[1] == 'genes':
			g.TFGeneChains = TFGeneChains.query.filter(or_(TFGeneChains.CHAIN.like('%%%s%%' % query), TFGeneChains.CHAIN_LENGTH.like('%%%s%%' % query), TFGeneChains.CHAIN_ID.like('%%%s%%' % query))).order_by(TFGeneChains.CHAIN_ID).paginate(page,app.config['PAGINATION_ITEMS'],error_out=False)

			g.res_dict = {'page_title': 'Checking',
						  'msg': 'Looks OK'}
			g.template = 'searchGenes.html'
			return 'OK'    

		if searchPath[0] == 'tissues' or searchPath[1] == 'tissues':
			with open(cwd+'/tfcascade_app/data/TissueCount.json', 'r') as fp:
				g.cascadeind = json.load(fp)
		
			g.res_dict = {'page_title': 'Checking',
						  'msg': 'Looks OK'}
			g.template = 'searchKnowledge.html'
			return 'OK'    


		if searchPath[0] == 'tissuechains' or searchPath[1] == 'tissuechains':
			print searchPath
			with open(cwd+'/tfcascade_app/data/TissueCount.json', 'r') as fp:
				g.filters = json.load(fp)

			key = ' '.join(searchPath[0].split('%20'))

			g.cascadeind = g.filters[key]
		
			g.res_dict = {'page_title': 'Checking',
						  'msg': 'Looks OK'}

			g.template = 'searchTissue.html'
			return 'OK'    



#-----------------------------------------------------------------------------------------------------------------------------------------------------------------


@app.route("/check", methods=['POST', 'GET'])
def check():
	g.res_dict = {'page_title': 'Checking',
				  'msg': 'Looks OK'}
	g.template = 'results.html'
	return 'OK'




@app.route("/cascade_vis/<chain_id>", methods=['POST', 'GET'])
def cascade_vis(chain_id):
	ind = int(chain_id)
	cwd = os.getcwd()

	col1,col2,col3,col4,col5,col6 = [],[],[],[],[],[]

	with open(cwd+'/tfcascade_app/data/geneNetwork.json', 'r') as fp:
		g.genenetwork = json.load(fp)

	g.genechain = TFGeneChains.query.get(ind).CHAIN.split()
	g.proteinchain = TFChains.query.get(ind).CHAIN.split()

	with open(cwd+'/tfcascade_app/data/pantherGeneList.txt') as fp:
		lines = fp.readlines()

	lines = [x.strip().split('\t') for x in lines]

	for i in range(len(g.genechain)):
		data = [line[1:] for line in lines if g.genechain[i] in line ]
		print data
		if len(data)>0:
			col1.append(i+1)
			col2.append(g.proteinchain[i])
			col3.append(g.genechain[i])
			col4.append(data[0][1])
			col5.append(data[0][2])
			col6.append(data[0][3])
		else:
			col1.append(i+1)
			col2.append(g.proteinchain[i])
			col3.append(g.genechain[i])
			col4.append('N/A')
			col5.append('N/A')
			col6.append('N/A')


	g.table_rows = zip(col1,col2,col3,col4,col5,col6)



	node_prop = '''"group": "nodes",
					  "removed": false,
					  "selected": false,
					  "selectable": true,
					  "locked": false,
					  "grabbed": false,
					  "grabbable": true,'''
	edge_prop = '''"group": "edges",
					  "removed": false,
					  "selected": false,
					  "selectable": true,
					  "locked": false,
					  "grabbed": false,
					  "grabbable": true,
					  "classes": ""'''

	g.res_dict = {'page_title': 'Checking',
				  'msg': 'Looks OK'}
	g.template = 'cascade_vis.html'
	return 'OK'

@app.route("/enrichment")
def enrichment():
	
	g.res_dict = {'page_title': 'Pathway Enrichment Results',
						'msg': 'Looks OK'}
	
	g.files = os.listdir("web_app/data/KEGG")
	g.files.sort()
	g.csv_html = []
	for i in g.files:
		g.csv_html.append([i, csv_to_html("web_app/data/KEGG/%s"%i,1,i)])
	
	
	g.template = 'enrichment.html'
	return 'OK'

def csv_to_html(csv_file,csv_header,unique_id=1):
	try:
		with open(csv_file, 'rb') as FH:
			reader = csv.reader(FH, delimiter='\t')
			
			csv_content = list(reader)
			
			if not int(csv_header):
				csv_content.insert(0, ['']*len(csv_content[0]))
		
		res_dict = {'page_title': 'CSV Parse',
					  'status':0,
					  'result':csv_content[:100],
					  'unique_id':unique_id,
					  'cur_wd':""}
		template = 'csv_to_html.html'
	except Exception as e:
		g.res_dict['status'] = 1
		g.res_dict['errormessage'] = e.message
	return render_template(template, res_dict=res_dict)

@app.route("/aboutus", methods=['POST', 'GET'])
def aboutus():
	g.res_dict = {'page_title': 'Checking',
				  'msg': 'Looks OK'}
	g.template = 'aboutus.html'
	return 'OK'

@app.route("/help")
def help():
	g.res_dict = {'page_title': 'Help',
				  'msg': 'Will be Available Soon'}
	# g.template = 'help.html'
	g.template = 'help.html'
	return 'OK'

@app.route("/invalid")
def invalid():
	g.res_dict = {'page_title': 'Invalid Access',
				  'msg': 'Not Available'}
	g.template = 'invalid.html'
	return 'OK'

def __log_activity():
	return True
	
def __debug(msg):
	with open(app.root_path+'/tmp2.txt', 'a') as FH:
		FH.write("%s\t\t%s\n" % (datetime.now().strftime("%Y-%m-%d %H:%M:%s"), msg))
	return True

if __name__ == "__main__":
	app.run(host='0.0.0.0')

@app.context_processor
def utility_functions():
    def print_in_console(message):
        print str(message)

    return dict(mdebug=print_in_console)