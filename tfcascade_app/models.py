from sqlalchemy.orm import relationship
from . import db
# from flask.ext.permissions.models import UserMixin


""" Basic models START """
# class Settings(db.Model):
# 
#     __tablename__ = "tbl_settings"
# 
#     stg_id              = db.Column(db.Integer, primary_key=True)
#     stg_key             = db.Column(db.String(30), unique=True)
#     stg_value           = db.Column(db.String(100))
#     stg_remarks         = db.Column(db.Text())
#     stg_edit_user_level = db.Column(db.Integer)
#     stg_value_type      = db.Column(db.String(50))
#     
class User(db.Model):

    __tablename__ = "tbl_usersMaster"

    usr_id              = db.Column(db.Integer, primary_key=True)
    usr_uname           = db.Column(db.String(100), unique=True)
    usr_psword          = db.Column(db.String(120))
    usr_namePrefix      = db.Column(db.String(10))
    usr_firstname       = db.Column(db.String(100))
    usr_lastname        = db.Column(db.String(100))
    usr_accounttype     = db.Column(db.Integer, db.ForeignKey('tbl_accountTypeMaster.act_id'))
    #usr_department     = db.Column(db.Integer, db.ForeignKey('tbl_departmentMaster.dpt_id'))
    usr_emailOfficial   = db.Column(db.String(255))
    usr_emailPersonal   = db.Column(db.String(255))
    usr_phoneOfficial   = db.Column(db.String(255))
    usr_phonePersonal   = db.Column(db.String(255))
    usr_status          = db.Column(db.Integer, db.ForeignKey('tbl_usrStatusMaster.usm_id'))

    activity = db.relationship('ActivityLog', backref='user', lazy='dynamic')
    # projects = db.relationship('Projects', backref='user', lazy='dynamic')
    # project_activity = db.relationship('ProjectActivities', backref='user', lazy='dynamic')

    def __repr__(self):
        return self.full_name
    
    @property
    def active(self):
        if self.usr_status > 2:
            return True
        else:
            return False
        
    @property
    def id(self):
        return self.usr_id
    
    @property
    def full_name(self):
        return "%s %s %s" % ((self.usr_namePrefix if self.usr_namePrefix else ''),
                             (self.usr_firstname if self.usr_firstname else ''),
                             (self.usr_lastname if self.usr_lastname else ''))
    
    @property
    def is_admin(self):
        if self.usr_accounttype < 3:
            return True
        return False
    
    @property
    def is_lead(self):
        if self.usr_accounttype == 3:
            return True
        return False
    
    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return unicode(self.id)


class Status(db.Model):

    __tablename__ = "tbl_usrStatusMaster"

    usm_id = db.Column(db.Integer(), primary_key=True)
    usm_name = db.Column(db.String(80), unique=True)
    usm_color = db.Column(db.String(80))
    
    users = db.relationship('User', backref='status', lazy='dynamic')
    
    def __repr__(self):
        return self.usm_name
    
class AccountType(db.Model):

    __tablename__ = "tbl_accountTypeMaster"

    act_id = db.Column(db.Integer(), primary_key=True)
    act_name = db.Column(db.String(80), unique=True)
    
    users = db.relationship('User', backref='ac_type', lazy='dynamic')
    
    def __repr__(self):
        return self.act_name 

    @property
    def id(self):
        return self.act_id 

class ActivityLog(db.Model):

    __tablename__ = "tbl_activityLog"

    acl_id              = db.Column(db.Integer(), primary_key=True)
    acl_usrId           = db.Column(db.Integer, db.ForeignKey('tbl_usersMaster.usr_id'))
    acl_params          = db.Column(db.Text)
    acl_url             = db.Column(db.Text)
    acl_performedAt     = db.Column(db.DateTime)
    acl_ActivityName    = db.Column(db.String(255))
    acl_remarks         = db.Column(db.Text)
        
    def __repr__(self):
        return "%s visited %s at %s with %s" % (self.user,
                                                self.acl_url,
                                                self.acl_performedAt,
                                                self.acl_params
                                                )

""" Basic models END """

""" Other models START """

class ExecutionHistory(db.Model):

    __tablename__ = "tbl_executionHistory"

    exh_id              = db.Column(db.Integer, primary_key=True)
    exh_execution_key   = db.Column(db.String(50))
    exh_menu_id         = db.Column(db.Integer, db.ForeignKey('tbl_menuMaster.mnm_id'))
    exh_working_dir     = db.Column(db.String(50))
    exh_params_file     = db.Column(db.String(100))
    exh_ip              = db.Column(db.String(50))
    exh_start           = db.Column(db.DateTime)
    exh_end             = db.Column(db.DateTime)
    exh_status          = db.Column(db.Integer, db.ForeignKey('tbl_executionStatusMaster.esm_id'))

class ExecutionStatusMaster(db.Model):

    __tablename__ = "tbl_executionStatusMaster"

    esm_id              = db.Column(db.Integer, primary_key=True)
    esm_name            = db.Column(db.String(50))
    esm_color           = db.Column(db.String(10))
    exec_history = db.relationship('ExecutionHistory', backref='status', lazy='dynamic')

class MenuMaster(db.Model):

    __tablename__ = "tbl_menuMaster"

    mnm_id              = db.Column(db.Integer, primary_key=True)
    mnm_url             = db.Column(db.String(50))
    mnm_desc            = db.Column(db.Text())
    mnm_permission      = db.Column(db.Integer)
    mnm_order           = db.Column(db.Integer)
    mnm_parent          = db.Column(db.Integer)
    exec_history = db.relationship('ExecutionHistory', backref='menu', lazy='dynamic')
    
class UniprotRecords(db.Model):

    __tablename__ = "tbl_uniprot_records"

    unr_id              = db.Column(db.Integer, primary_key=True)
    unr_accession       = db.Column(db.String(30))
    unr_file_path       = db.Column(db.Text())
    unr_recorded_date   = db.Column(db.DateTime)

class TFKnowledgeExperiment(db.Model):

    __tablename__ = "tbl_knowledge_experiment"
    
    kkt_id                          = db.Column(db.Integer, primary_key=True)
    kkt_ensemble_id             	= db.Column(db.String(25))
    kkt_genecard_id                	= db.Column(db.String(10))
    kkt_bto_id        		        = db.Column(db.String(10))
    kkt_location       		        = db.Column(db.String(100))
    kkt_source          		    = db.Column(db.String(10))
    kkt_expression     		        = db.Column(db.String(100))
    kkt_confidence          	    = db.Column(db.Float)
    kkt_record_type          	    = db.Column(db.String(5))
    
class TFChains(db.Model):
    __tablename__ = "tbl_chains"
    
    CHAIN_ID                        = db.Column(db.Integer, primary_key=True)
    CHAIN             			    = db.Column(db.String(25))
    CHAIN_LENGTH                	= db.Column(db.String(10)) 

class TFGeneChains(db.Model):
    __tablename__ = "tbl_genechains"
    
    CHAIN_ID                        = db.Column(db.Integer, primary_key=True)
    CHAIN                           = db.Column(db.String(25))
    CHAIN_LENGTH                    = db.Column(db.String(10))    
""" Other models END """