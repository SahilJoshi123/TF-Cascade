#!/usr/bin/python
from . import app, models
from .models import ExecutionHistory, ExecutionStatusMaster, MenuMaster
# from Bio import SeqIO
from flask import render_template, g, request, url_for
from multiprocessing import Process
import csv, sys, re, os, json, ConfigParser

sys.path.insert(0,app.config['LIBRARY_PATH'])

# import AGMSeqIO, AGMSwissIO

class GUIInputerror(Exception):
    pass

form_component_dict = {'file': "<input type='file' name='%s' id='%s' class='pull-left form-control'  data-toggle='tooltip' data-placement='top' title='%s' />",
                       'text': "<input type='text' name='%s' id='%s' value='%s' class='form-control pull-left' data-toggle='tooltip' data-placement='top' title='%s' />",
                       'text_rqd' : "<input type='text' name='%s' id='%s' value='%s' class='form-control pull-left' required data-toggle='tooltip' data-placement='top' title='%s' />",
                       'number': "<input type='number' name='%s' id='%s'  min='%s' max='%s' step='%s' value='%s' class='form-control pull-left' data-toggle='tooltip' data-placement='top' title='%s' />",
                       'textarea': "<textarea name='%s' id='%s' class='form-control pull-left' rows='7' cols='60' data-toggle='tooltip' data-placement='top' title='%s' ></textarea>",
                       'textarea_rd_only': "<textarea name='%s' id='%s' class='form-control pull-left' rows='7' cols='60' readonly data-toggle='tooltip' data-placement='top' title='%s' ></textarea>",
                       'select': "<select name='%s' id='%s' onchange='select_change(this);' class='pull-left form-control' data-toggle='tooltip' data-placement='top' title='%s' />%s</select>",                       
                       'checkbox' : "<input type='checkbox'  name='%s' id='%s' class='checkbox pull-left' %s />",
                       'label' : "<label id='%s'>%s</label>",
                       'div_start' : "<div id='%s' style='display:%s'>",
                       'div_end' : "</div> <!-- %s  display=%s-->",
                       'tupple2_rqd' : """<input type='text' name='%s' id='%s' value='%s' class='form-control pull-left readonly tupple_text' required data-toggle='tooltip' data-placement='top' title='%s'  />
                                    <input type='number' name='%s_1' id='%s_1'  min='%s' max='%s' step='%s' value='%s' class='form-control pull-left' data-toggle='tooltip' data-placement='top' title='%s' style='width: 60px;' />
                                    <input type='number' name='%s_2' id='%s_2'  min='%s' max='%s' step='%s' value='%s' class='form-control pull-left' data-toggle='tooltip' data-placement='top' title='%s' style='width: 60px;' />
                                    <button type='button' class='btn btn-default icon-btn  pull-left' onclick="add_tuple2('%s')"><span class='glyphicon btn-glyphicon glyphicon-plus img-circle text-primary'></span>Add</button>
                                    <button type='button' class='btn btn-default icon-btn  pull-left' onclick="remove_tuple2('%s')"><span class='glyphicon btn-glyphicon  glyphicon-minus  img-circle text-warning'></span>Remove</button>""",
                       'tupple2' : """<input type='text' name='%s' id='%s' value='%s' class='form-control pull-left readonly tupple_text'  data-toggle='tooltip' data-placement='top' title='%s' />
                                    <input type='number' name='%s_1' id='%s_1'  min='%s' max='%s' step='%s' value='%s' class='form-control pull-left' data-toggle='tooltip' data-placement='top' title='%s' style='width: 60px;' />
                                    <input type='number' name='%s_2' id='%s_2'  min='%s' max='%s' step='%s' value='%s' class='form-control pull-left' data-toggle='tooltip' data-placement='top' title='%s' style='width: 60px;' />
                                    <button type='button' class='btn btn-default icon-btn pull-left' onclick="add_tuple2('%s')"><span class='glyphicon btn-glyphicon glyphicon-plus img-circle text-primary'></span>Add</button>
                                    <button type='button' class='btn btn-default icon-btn  pull-left' onclick="remove_tuple2('%s')"><span class='glyphicon btn-glyphicon  glyphicon-minus  img-circle text-warning'></span>Remove</button>""",
                       'tupple1' : """<input type='text' name='%s' id='%s' value='%s' class='form-control pull-left readonly tupple_text'   data-toggle='tooltip' data-placement='top' title='%s'  />
                                    <input type='number' name='%s_1' id='%s_1'  min='%s' max='%s' step='%s' value='%s' class='form-control pull-left' data-toggle='tooltip' data-placement='top' title='%s' style='width: 60px;margin-right:60px' />
                                    <button type='button' class='btn btn-default icon-btn pull-left' onclick="add_tuple1('%s')"><span class='glyphicon btn-glyphicon glyphicon-plus img-circle text-primary'></span>Add</button>
                                    <button type='button' class='btn btn-default icon-btn pull-left' onclick="remove_tuple1('%s')"><span class='glyphicon btn-glyphicon  glyphicon-minus  img-circle text-warning'></span>Remove</button>"""
                                    
                       }

def db_file_parse(repo_filename, file_format):
    """Parse details from already fetched file and do appropriate formatting"""
    if file_format == 'swiss':
        record = AGMSeqIO.parse(repo_filename, file_format)
        fields = app.config['ANNOTFIELDSUP']
        fieldsgo = app.config['ANNOTFIELDSGO']
    else:
        record = SeqIO.parse(repo_filename, file_format)
        fields = app.config['ANNOTFIELDSNR']
        fieldsgo = []
    db_res=None
    cur_raw = []
    for rec in record:
        for key in fields:
            if key.has_key('type'):
                if key['type'] == 'dict':
                    for terms in key['terms']:
                        if getattr(rec, key['key']).has_key(terms):
                            cur_raw.append(getattr(rec, key['key'])[terms])
                        else:
                            cur_raw.append('')
                elif key['type'] == 'list':
                    for terms in key['terms']:
                        dbrfs={db_name:[] for db_name in key['terms']}
                        dbrfsgo={db_name:[] for db_name in fieldsgo}
                        for terms in getattr(rec, key['key']):
                            db_flds = terms.split(';')
                            if dbrfs.has_key(db_flds[0]):
                                dbrfs[db_flds[0]].append(db_flds[1])
                            if db_flds[0] == 'GO':
                                dbgo_flds = db_flds[2].split(':')
                                if dbrfsgo.has_key(dbgo_flds[0]):
                                    dbrfsgo[dbgo_flds[0]].append('%s [%s]'%(dbgo_flds[1],db_flds[1]))
                    db_res = []
                    for db_name in key['terms']:
                        db_res.append(';'.join(dbrfs[db_name]))
                    cur_raw.extend(db_res)
                    dbgo_res = []
                    for db_name in fieldsgo:
                        dbgo_res.append(';'.join(dbrfsgo[db_name]))
                    cur_raw.extend(dbgo_res)
            else:
                cur_raw.append(getattr(rec, key['key']))
    return cur_raw

def csv_headers_up():
    cur_raw=[]
    for key in app.config['ANNOTFIELDSUP']:
        if key.has_key('type'):
            cur_raw.extend(key['terms'])
        else:
            cur_raw.append(key['key'])
    for key in app.config['ANNOTFIELDSNAMEGO']:
        cur_raw.append(key)
    return cur_raw

def csv_headers_nr():
    cur_raw=[]
    for key in app.config['ANNOTFIELDSNR']:
        if key.has_key('type'):
            cur_raw.extend(key['terms'])
        else:
            cur_raw.append(key['key'])
    return cur_raw

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
                      'cur_wd':g.current_wd}
        template = 'csv_to_html.html'
    except Exception as e:
        g.res_dict['status'] = 1
        g.res_dict['errormessage'] = e.message
    return render_template(template, res_dict=res_dict)

def go_count(diamond_file, columns, count, csv_header):
    go_bp_dict = {}
    go_mf_dict = {}
    go_cc_dict = {}
    with open(diamond_file) as IFH:
        reader = csv.reader(IFH, delimiter='\t')
        if int(csv_header):
            reader.next()
        for row in reader:
            go_bp = row[columns[0]-1].split(';')
            go_mf = row[columns[1]-1].split(';')
            go_cc = row[columns[2]-1].split(';')
            for bp in go_bp:
                if bp != '':
                    if bp in go_bp_dict:
                        go_bp_dict[bp]+=1
                    else:
                        go_bp_dict[bp]=1
            for mf in go_mf:
                if mf != '':
                    if mf in go_mf_dict:
                        go_mf_dict[mf]+=1
                    else:
                        go_mf_dict[mf]=1
            for cc in go_cc:
                if cc != '':
                    if cc in go_cc_dict:
                        go_cc_dict[cc]+=1
                    else:
                        go_cc_dict[cc]=1
    go_bp_dict = sorted(go_bp_dict.iteritems(), key=lambda (k,v): (v,k), reverse=True)
    go_mf_dict = sorted(go_mf_dict.iteritems(), key=lambda (k,v): (v,k), reverse=True)
    go_cc_dict = sorted(go_cc_dict.iteritems(), key=lambda (k,v): (v,k), reverse=True)
    g.bpfile = '%s/%s' % (g.current_wd_full_path, app.config['GOANNOTBPFILE'])
    g.mffile = '%s/%s' % (g.current_wd_full_path, app.config['GOANNOTMFFILE'])
    g.ccfile = '%s/%s' % (g.current_wd_full_path, app.config['GOANNOTCCFILE'])
    with open(g.bpfile, 'w') as csvfile:
        csvfile.write('%s\t%s\t%s\n' % ('GO ID','GO Term (Biological Processes)','Number of ORF'))
        for bp in go_bp_dict:
            if len(bp[0].split(' [')) >=2:
                goid = bp[0].split(' [')[1][:-1]
            else:
                goid = ''
            csvfile.write('%s\t%s\t%s\n' % (goid,bp[0],bp[1]))
    
    with open(g.mffile, 'w') as csvfile:
        csvfile.write('%s\t%s\t%s\n' % ('GO ID','GO Term (Molecular Functions)','Number of ORF'))
        for mf in go_mf_dict:
            if len(mf[0].split(' [')) >=2:
                goid = mf[0].split(' [')[1][:-1]
            else:
                goid = ''
            csvfile.write('%s\t%s\t%s\n' % (goid,mf[0],mf[1]))
    
    with open(g.ccfile, 'w') as csvfile:
        csvfile.write('%s\t%s\t%s\n' % ('GO ID','GO Term (Cellular Components)','Number of ORF'))
        for cc in go_cc_dict:
            if len(cc[0].split(' [')) >=2:
                goid = cc[0].split(' [')[1][:-1]
            else:
                goid = ''
            csvfile.write('%s\t%s\t%s\n' % (goid,cc[0],cc[1]))
        
    return go_bp_dict[:count], go_mf_dict[:count], go_cc_dict[:count]

def mainmenu():
    menu_array = '<ul class="nav navbar-nav navbar-right">'
    for menu in MenuMaster.query.filter_by(mnm_parent=0).order_by(MenuMaster.mnm_order.asc()).all():
        sub_menu = MenuMaster.query.filter_by(mnm_parent=menu.mnm_id).order_by(MenuMaster.mnm_order.asc()).all()
        if sub_menu!=[]:
            menu_array += """<li class="dropdown">
            <a class="dropdown-toggle" data-toggle="dropdown" href="#">%s<span class="caret"></span></a>
            <ul class="dropdown-menu">""" % (menu.mnm_desc)
            for sub_menu_item in sub_menu:
                active = ''
                if hasattr(request.url_rule, 'rule'):
                    if sub_menu_item.mnm_url in request.url_rule.rule:
                        active = ' class="active"'
                menu_array+="""<li%s><a href="/%s">%s</a></li>""" % (active,sub_menu_item.mnm_url, sub_menu_item.mnm_desc)
            menu_array += """</ul>
            </li>"""
        else:
            active = ''
            if hasattr(request.url_rule, 'rule'):
                if menu.mnm_url in request.url_rule.rule:
                    active = ' class="active"'
            menu_array += """<li%s><a href="/%s">%s</a></li>""" % (active, menu.mnm_url, menu.mnm_desc)
    # print menu_array
    menu_array += '</ul>'
    return menu_array

def format_integer(value):
    if value == None:
        return value
    return "{:,}".format(value)

def background_process(function, args):
    p = Process(target=function, kwargs=args)
    p.start()
    # p.join()
    
    
def get_form(module_name, sample_run=0):
    # lnk = {'module_name': module_name}
    form_content = '<form class="form-horizontal" action="%s" enctype="multipart/form-data" method="post" >' % ( url_for('run_module', module_name=module_name))
    with open(app.config['FORMSDIR'] + module_name + ".form") as FFH:
        for ln in FFH:
            if re.match('#', ln):continue
            ln = re.sub('\r|\n', '', ln)
            flds = re.split('\t', ln)
            flds = list(flds)
            for i in range(len(flds), 8):
                flds.append('')
            if flds[0] == 'select':
                opt = ''
                for item in re.split(',', flds[3]):
                    (disp, val) = re.split(':', item)
                    opt += "<option value='%s'>%s</option>" % (val, disp)
                
                select_content = form_component_dict[flds[0]] % (flds[2], flds[2],flds[4], opt)
                form_content += """<div class="form-group">
                                    <label for="%s" class="col-sm-4 control-label">%s</label>
                                    <div class="col-sm-1">
                                      %s
                                    </div>
                                  </div>""" % (flds[2], flds[1], select_content)
            elif flds[0] == 'select_file':
                opt = ''
                with open(app.config['FORMSDIR'] + flds[3]) as SFH:
                     for disp in SFH:
                        disp = re.sub('\r|\n', '', disp)
                        opt += "<option value='%s'>%s</option>" % (disp, disp)
                
                select_content = form_component_dict['select'] % (flds[2], flds[2],flds[4], opt)
                form_content += """<div class="form-group">
                                    <label for="%s" class="col-sm-4 control-label">%s</label>
                                    <div class="col-sm-1">
                                      %s
                                    </div>
                                  </div>""" % (flds[2], flds[1], select_content)                                  
            elif flds[0] == 'checkbox':
                if flds[3] == 'checked':
                    check_str = 'checked="checked"'
                else:
                    check_str = ''
                comp_content = form_component_dict[flds[0]] % (flds[2], flds[2],check_str)
                form_content += """<div class="form-group">
                                    <label for="" class="col-md-4 control-label"></label>
                                    <div class="col-md-8 pull-left">
                                      <div class="checkbox pull-left">
                                        <label  data-toggle='tooltip' data-placement='top' title='%s'>%s %s</label>
                                      </div>
                                    </div>
                                  </div>"""  % (flds[4],comp_content, flds[1])
            elif flds[0] == 'file':
                if sample_run :
                    comp_content = """<input type='text' name='%s' id='%s' value='%s' class='form-control pull-left' readonly />""" % (flds[2], flds[2], flds[3])
                else :
                    comp_content = form_component_dict[flds[0]] % (flds[2], flds[2],flds[4])
                form_content += """<div class="form-group">
                                    <label for="%s" class="col-md-4 control-label">%s</label>
                                    <div class="col-md-8 pull-left" >
                                      %s
                                    </div>
                                  </div>""" % (flds[2], flds[1], comp_content)
            elif flds[0] == 'label':
                comp_content = form_component_dict[flds[0]] % (flds[2], flds[1])
                form_content += """<div class="form-group">
                                    <label for="" class="col-md-4 control-label"></label>
                                    <div class="col-md-8" style='float:left;text-align:left;'>
                                      %s
                                    </div>
                                  </div>""" % (comp_content)
            elif flds[0] == 'number':
                comp_content = form_component_dict[flds[0]] % (flds[2], flds[1], flds[3], flds[4], flds[5], flds[6],flds[7] )
                form_content += """<div class="form-group">
                                    <label for="%s" class="col-md-4 control-label">%s</label>
                                    <div class="col-md-8 pull-left">
                                      %s
                                    </div>
                                  </div>""" % (flds[2], flds[1], comp_content)
            elif flds[0] == 'tupple2_rqd' or flds[0] == 'tupple2':
                comp_content = form_component_dict[flds[0]] % (flds[2], flds[2], flds[4], flds[9],flds[2], flds[2], flds[5], flds[6], flds[7], flds[8],flds[9],flds[2], flds[2], flds[5], flds[6], flds[7], flds[8],flds[9],flds[2],flds[2] )
                form_content += """<div class="form-group">
                                    <label for="%s" class="col-md-4 control-label">%s</label>
                                    <div class="col-md-8 pull-left">
                                      %s
                                    </div>
                                  </div>""" % (flds[2], flds[1], comp_content)
            elif flds[0] == 'tupple1_rqd' or flds[0] == 'tupple1':
                comp_content = form_component_dict[flds[0]] % (flds[2], flds[2], flds[4], flds[9],flds[2], flds[2], flds[5], flds[6], flds[7], flds[8],flds[9],flds[2],flds[2] )
                form_content += """<div class="form-group">
                                    <label for="%s" class="col-md-4 control-label">%s</label>
                                    <div class="col-md-8 pull-left">
                                      %s
                                    </div>
                                  </div>""" % (flds[2], flds[1], comp_content)
                                  
            elif  flds[0] == 'textarea':
                if sample_run :
                    comp_content = form_component_dict['textarea_rd_only'] % (flds[2], flds[2],flds[3])
                else :                                                       
                    comp_content = form_component_dict[flds[0]] % (flds[2], flds[2],flds[3])                
                form_content += """<div class="form-group">
                                    <label for="%s" class="col-md-4 control-label">%s</label>
                                    <div class="col-md-8 pull-left">
                                      %s
                                    </div>
                                  </div>""" % (flds[2], flds[1], comp_content)
            elif  ((flds[0] == 'text') or (flds[0] == 'text_rqd')):
                if sample_run :
                    comp_content = form_component_dict[flds[0]] % (flds[2], flds[2], flds[4], flds[5])
                else :
                    comp_content = form_component_dict[flds[0]] % (flds[2], flds[2], flds[3],flds[5])
                form_content += """<div class="form-group">
                                    <label for="%s" class="col-md-4 control-label">%s</label>
                                    <div class="col-md-8 pull-left">
                                      %s
                                    </div>
                                  </div>""" % (flds[2], flds[1], comp_content)
            elif  ((flds[0] == 'div_start') or (flds[0] == 'div_end')):
                comp_content = form_component_dict[flds[0]] % (flds[1],flds[2])
                form_content += "%s" % (comp_content)                                                                     
            else:
                comp_content = form_component_dict[flds[0]] % (flds[2], flds[2],flds[3])
                form_content += """<div class="form-group">
                                    <label for="%s" class="col-md-4 control-label">%s</label>
                                    <div class="col-md-8 pull-left">
                                      %s
                                    </div>
                                  </div>""" % (flds[2], flds[1], comp_content)  
    form_content += "<button type'submit' class='btn btn-primary pull-right' >Submit</button>"
    form_content += "<input type='hidden' name='sample_run' id='sample_run' value='%s' />" % (sample_run)
    form_content += "</form>"
    
    jscript = None
    jscript_path = app.config['FORMSDIR'] + module_name + ".script"
    if os.path.isfile(jscript_path)  :
        with open(jscript_path) as FFH:
            jscript = FFH.read()
        if jscript :
            form_content += '<script  type="text/javascript">%s</script>'%(jscript)

    return form_content


def create_cmdline(form,cmd_args,cfg_file,work_dir) :
    cmd_line = ""
    
    config = ConfigParser.ConfigParser()
    if os.path.isfile(cfg_file):
        config.read(cfg_file)

    #prepare cmd line options
    try :
        for key,specs in sorted(cmd_args.iteritems()):            
            param = specs[0]
            #print "param=",param
            typeStr = specs[1]
            cmdLineStr = specs[4]
            if (specs[2] == True) : #User Exposed
                try :
                    # value = form[param].value
                    value = form[param]
                except Exception, e:
                    value = None
            else : #Try to get from  config file
                try :
                    value = config.get('DEFAULT',param)
                except Exception, e:
                    value = None
            if(value == None) :
                if (specs[5] == False) : #Defaults need not be included if not provided by client or config file
                    continue
                value = str(specs[3])                
            if(value == None) : continue
            if isinstance(typeStr, list):
                choiceFound = False
                for choice in typeStr :                        
                    if (isinstance(choice,int)) : value = int(value)
                    elif (isinstance(choice,float)) : value = float(value)
                    if(value == choice):
                        cmd_line += ' ' + cmdLineStr + ' ' + str(value)
                        choiceFound = True
                        break;
                if (not choiceFound ) :
                    raise Exception("Given value not within allowed choices/range")
            elif(typeStr == 'bool') :
                if (value == 'on' or value == True or value == 'True') :
                    cmd_line += ' ' + cmdLineStr
            elif(typeStr == 'int') :
                cmd_line += ' ' + cmdLineStr + ' ' + str(int(value))
            elif(typeStr == 'float') :
                cmd_line += ' ' + cmdLineStr + ' ' + str(float(value))
            elif(typeStr == 'str') :
                if (specs[5] == False and value == "") : #Defaults need not be included if not provided by client or config file
                    continue
                if len(specs) > 6 and specs[6] :
                    specs[6](value)
                cmd_line += ' ' + cmdLineStr + ' "' + value + '"'
            elif(typeStr == 'environment') :
                    cmd_line += ' export ' + param + '=' + value + ';'
            elif(typeStr == 'lookup') :
                try :
                    lookup_val = config.get('DEFAULT',value)
                    cmd_line += ' ' + cmdLineStr + ' ' + lookup_val
                except Exception, e:
                    cmd_line += ' ' + cmdLineStr
            elif(typeStr == 'pgm') :
                try :
                    pgmPath = config.get('DEFAULT',param+"_PATH")
                    cmd_line += pgmPath + '/' + cmdLineStr
                except Exception, e:
                    cmd_line += cmdLineStr+' ' 
            elif(typeStr == 'file') :
                #if (form[param].value != "") :
                    #cur_in_file_path = work_dir + "/" + specs[3]
                    cur_in_file_path = specs[3]
                    if os.path.isfile(work_dir + "/" + specs[3]) :
                        cmd_line += ' ' + cmdLineStr + ' ' + cur_in_file_path
            elif(typeStr == 'stdout') :
                cmd_line += ' > '  + str(value)
            elif(typeStr == 'stderr') :
                cmd_line += ' 2> '  + str(value)
            elif(typeStr == 'stdouterr') :
                cmd_line += ' > '  + str(value) + ' 2>&1 '
            else :
                cmd_line += ' ' + cmdLineStr + ' ' + str(value)
    except GUIInputerror, e:
            raise
    except Exception, e:
            e.message = "Invalid Parameter :'" + param + "'-" + e.message
            raise
    
    cmd_line = '(cd ' + work_dir + '; ' + cmd_line + ';touch COMPLETED) > /dev/null 2>&1 &'
    #print cmd_line
    return cmd_line

def run_generic_cmd(form,mod_name,cmd_args,config_file,result_dict):
        print form, 'wwwwwwww'
    # cmd_line = ""
    # res = "UNSUCCESSFUL"
    # cur_date_dir = "0"
    # # accession_id = "0"
    # try:
        # cfg_file =   apps_settings.config_dir + config_file
        # accession_id = generate_unique_accession_id(mod_name)
        # cur_working_dir = create_work_dir(accession_id)   
        # #print cur_working_dir
        # save_input(cur_working_dir,form,cmd_args,cfg_file,result_dict['sample_run'])
        cfg_file = '%s/%s' % (app.config['CFGDIR'],config_file)
        cmd_line = create_cmdline(form,cmd_args,cfg_file,g.current_wd_full_path)
        
        print "cmd_line=",cmd_line, 'kkk'

        retCode = os.system(cmd_line)
        print 'done', retCode
        if (retCode > 0) :
            result_dict['STATUS'] = 'Failed'
            result_dict['MSG'] = "ERROR: Program execution Failed"
        else :
            result_dict['STATUS'] = 'Successful'
    # except GUIInputerror, e:
    #     result_dict['STATUS'] = 'Failed'
    #     result_dict['MSG'] = e.message    
    # except Exception, e:
    #     result_dict['STATUS'] = 'Failed'
    #     result_dict['MSG'] = "ERROR: " + e.message
    # return True

def cmd_args_parse(module_name):
        ga = {}
        la = {}
        execfile('%s/%s.args' % (app.config['ARGSDIR'], module_name), ga, la)
        return la['cmd_args']
