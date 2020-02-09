import datetime
from web_api import app, db
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.security import UserMixin, RoleMixin
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import \
    ARRAY, BIGINT, BIT, BOOLEAN, BYTEA, CHAR, CIDR, DATE, \
    DOUBLE_PRECISION, ENUM, FLOAT, HSTORE, INET, INTEGER, \
    INTERVAL, JSON, JSONB, MACADDR, NUMERIC, OID, REAL, SMALLINT, TEXT, \
    TIME, TIMESTAMP, UUID, VARCHAR, INT4RANGE, INT8RANGE, NUMRANGE, \
    DATERANGE, TSRANGE, TSTZRANGE, TSVECTOR


class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(BIGINT, primary_key=True)
    facebook_id = db.Column(BIGINT, default = True, nullable = True)
    username = db.Column(VARCHAR(128), default = True, nullable = True)
    email = db.Column(VARCHAR(196), default = True, nullable = True)
    password = db.Column(VARCHAR(256), default = True, nullable = True)
    confirmed_at = db.Column(TIMESTAMP, default = func.current_timestamp())
    name_first = db.Column(VARCHAR(128), default = True, nullable = False)
    name_last = db.Column(VARCHAR(128), default = True, nullable = False)
    induction_completed = db.Column(INTEGER, default = 0)
    adminlevel = db.Column(INTEGER, default = 0)
    outbound_last_identify = db.Column(TIMESTAMP)
    serviceConsent = db.Column(INTEGER, default = True, nullable = True)
    sitever = db.Column(BIGINT, default = 0)
    firstrunwarning = db.Column(INTEGER, default = 0)
    displayname = db.Column(VARCHAR(64), default = True, nullable = True)
    consentonfile = db.Column(BOOLEAN, default = 0)
    mailinglist_invite = db.Column(TIMESTAMP)
    active = db.Column(BOOLEAN)
    kits = db.relationship('Kits', backref='users')

    def __init__(self, facebook_id, username, email, password, name_first, name_last, induction_completed,
                 adminlevel, outbound_last_identify, serviceConsent, sitever, firstrunwarning, displayname,
                 consentonfile, mailinglist_invite):
        self.facebook_id = facebook_id
        self.username = username
        self.email = email
        self.password = password
        self.name_first = name_first
        self.name_last = name_last
        self.induction_completed = induction_completed
        self.adminlevel = adminlevel
        self.outbound_last_identify = outbound_last_identify
        self.serviceConsent = serviceConsent
        self.sitever = sitever
        self.firstrunwarning = firstrunwarning
        self.displayname = displayname
        self.consentonfile = consentonfile
        self.mailinglist_invite = mailinglist_invite

    def __repr__(self):
        return '<id {}>'.format(self.id)

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(BIGINT, primary_key=True)
    name = db.Column(VARCHAR(128), unique=True)
    description = db.Column(TEXT)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(BIGINT, primary_key=True)
    email = db.Column(VARCHAR(255), unique=True)
    password = db.Column(VARCHAR(255))
    active = db.Column(BOOLEAN)
    confirmed_at = db.Column(TIMESTAMP, default = func.current_timestamp())
    #Optional/Additional fields for Registration
    first_name = db.Column(VARCHAR(255))
    last_name = db.Column(VARCHAR(255))
    admin = db.Column(BOOLEAN, default = False)

    last_login_at = db.Column(TIMESTAMP)
    current_login_at = db.Column(TIMESTAMP)
    last_login_ip = db.Column(TEXT)
    current_login_ip = db.Column(TEXT)
    login_count = db.Column(BIGINT)
    user_survey = db.relationship('UserSurvey', backref='users')   
    roles = db.relationship('Role', secondary=roles_users,
    backref=db.backref('users', lazy='dynamic'))


from flask.ext.wtf import Form
from flask_security.forms import RegisterForm, ConfirmRegisterForm

from wtforms.fields import TextField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Required, Email, EqualTo

#Extended Flask-Security RegisterForm fields
class ExtendedRegisterForm(RegisterForm):
    first_name = TextField('First Name', [Required()])
    last_name = TextField('Last Name', [Required()])
    admin = BooleanField('Admin')

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore, confirm_register_form=ExtendedRegisterForm)

