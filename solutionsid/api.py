from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, DateTime

import uuid
import os, json
import jwt
import datetime

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

port = int(os.getenv("PORT"))
# DB
#basedir = os.path.abspath(os.path.dirname(__file__))
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')

POSTGRES_URL=json.loads(os.getenv('VCAP_SERVICES'))['aws-rds'][0]['credentials']['host']
POSTGRES_USER=json.loads(os.getenv('VCAP_SERVICES'))['aws-rds'][0]['credentials']['username']
POSTGRES_PW=json.loads(os.getenv('VCAP_SERVICES'))['aws-rds'][0]['credentials']['password']
POSTGRES_DB=json.loads(os.getenv('VCAP_SERVICES'))['aws-rds'][0]['credentials']['db_name']


# app.config['SEC_KEY'] = 'U2FsdGVkX1+d+5iG'
DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init DB
db = SQLAlchemy(app)
ma = Marshmallow(app)

def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')  # http://loc:5000/route?token=xyz

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            data = jwt.decode(token, app.config['SEC_KEY'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated

@app.route('/')
def hello_dx():
    # environment_variables = { key: os.environ[key] for key in os.environ.keys() }
    # return jsonify({'message' : str(app.config['APP_ENV'])})
    # return json.loads(os.getenv('VCAP_SERVICES'))['aws-rds'][0]['credentials']['uri']
    return jsonify({'message' : 'Hello SolutionsID!'})

@app.route('/api/v1/unprotected')
def unprotected():
    return jsonify({'message': 'Free content'})


@app.route('/api/v1/protected')
@require_token
def protected():
    return jsonify({'message': 'Content with Token'})


@app.route('/login')
def login():
    auth = request.authorization

    if auth and auth.password == 'teddyted':
        token = jwt.encode(
            {'user': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1440)},
            app.config['SEC_KEY'])

        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify user!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


########
## Procurement Method Class
#######

class Prmthd(db.Model):
    code = db.Column(db.String(50), unique=True, primary_key=True)
    description = db.Column(db.String(100))

    def __init__(self, code, description):
        self.code = code
        self.description = description


# Schema
class PrmthdSchema(ma.Schema):
    class Meta:
        fields = ('code', 'description')


# init schema
prmthd_schema = PrmthdSchema()  # strict='True'

prmthds_schema = PrmthdSchema(many=True)  # many=True, strict='True'

# Create a Procurement Method
@app.route('/api/v1/prmthd', methods=['POST'])
@require_token
def add_prmthd():
    code = request.json['code']
    description = request.json['description']

    new_prmthd = Prmthd(code, description)

    db.session.add(new_prmthd)
    db.session.commit()

    return prmthd_schema.jsonify(new_prmthd)


# Get all Procurement Methods
@app.route('/api/v1/prmthd', methods=['GET'])
def get_prmthds():
    all_prmthds = Prmthd.query.all()
    result = prmthds_schema.dump(all_prmthds)

    return jsonify(result)


# Get single Procurement Method
@app.route('/api/v1/prmthd/<code>', methods=['GET'])
def get_prmthd(code):
    prmthd = Prmthd.query.get(code)

    return prmthd_schema.jsonify(prmthd)


# Update Procurement Method
@app.route('/api/v1/prmthd/<code>', methods=['PUT'])
def update_prmthd(code):
    prmthd = Prmthd.query.get(code)

    code = request.json['code']
    description = request.json['description']

    prmthd.code = code
    prmthd.description = description

    db.session.commit()

    return prmthd_schema.jsonify(prmthd)


# Delete Procurement Method
@app.route('/api/v1/prmthd/<id>', methods=['DELETE'])
def delete_prmthd(id):
    prmthd = Prmthd.query.get(id)
    db.session.delete(prmthd)
    db.session.commit()

    return prmthd_schema.jsonify(prmthd)

#######
## User Class
#######

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    admin = db.Column(db.Boolean)

@app.route('/user', methods=['GET'])
def get_all_users():
    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['token'] = user.token
        user_data['email'] = user.email
        user_data['password'] = user.password
        user_data['admin'] = user.admin
        output.append(user_data)

    return jsonify({'users' : output})

@app.route('/user/<user_id>', methods=['GET'])
def get_one_user(user_id):
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({'message' : 'No user with that id found!'})

    user_data = {}
    user_data['id'] = user.id
    user_data['token'] = user.token
    user_data['email'] = user.email
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify({'user' : user_data})

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(id=data['id'],token=str(uuid.uuid4()), email=data['email'], password=hashed_password, admin=True)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message' : 'New user created!'})

@app.route('/user/<user_id>', methods=['PUT'])
def promote_user():
    return ''

@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user():
    return ''

#######
## SAM Business Types
#######
class SamBusinessTypes(db.Model):
    businessTypeCode = db.Column(db.String(2), primary_key=True)
    businessTypeName = db.Column(db.String(100))

# Schema
class SamBustypesSchema(ma.Schema):
    class Meta:
        fields = ('businessTypeCode', 'businessTypeName')


# init schema
sambustype_schema = SamBustypesSchema()  # strict='True'

sambustypes_schema = SamBustypesSchema(many=True)  # many=True, strict='True'

# Get all SAM Business Types
@app.route('/api/v1/sambustypes', methods=['GET'])
@require_token
def get_sambustypes():
    all_sambustypes = SamBusinessTypes.query.all()
    result = sambustypes_schema.dump(all_sambustypes)

    return jsonify(result)

#######
## Report Offices
#######
class Rptoff(db.Model):
    fss_report_office = db.Column(db.String(2), primary_key=True)
    portfolio = db.Column(db.String(5))
    office = db.Column(db.String(50))
    aac = db.Column(db.String(7))
    program = db.Column(db.String(10))
    fss_description_contract_type = db.Column(db.String(255))
    notes = db.Column(db.String(255))
    created_dt = db.Column(DateTime, default=datetime.datetime.utcnow)
    updated_dt = db.Column(DateTime)

# Schema
class ReportOfficeSchema(ma.Schema):
    class Meta:
        fields = ('fss_report_office', 'portfolio', 'office', 'aac', 'program',
                  'fss_description_contract_type', 'notes', 'created_dt', 'updated_dt')
# init schema
rptoff_schema = ReportOfficeSchema()  # strict='True'

rptoffs_schema = ReportOfficeSchema(many=True)  # many=True, strict='True'

# Get all Report Offices
@app.route('/api/v1/rptoff', methods=['GET'])
@require_token
def get_reportoffices():
    all_reportoffices = Rptoff.query.all()
    result = rptoffs_schema.dump(all_reportoffices)

    return jsonify(result)

#######
## Types of Contract Codes - Typecont
#######
class Typecont(db.Model):
    code = db.Column(db.String(2), primary_key=True)
    description = db.Column(db.String(5))
    created_at = db.Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(DateTime)

# Schema
class TypeContSchema(ma.Schema):
    class Meta:
        fields = ('code', 'description', 'created_at', 'updated_at')
# init schema
typecont_schema = TypeContSchema()  # strict='True'

typeconts_schema = TypeContSchema(many=True)  # many=True, strict='True'

# Get all Contract Types
@app.route('/api/v1/typecont', methods=['GET'])
@require_token
def get_typeconts():
    all_typeconts = Typecont.query.all()
    result = typeconts_schema.dump(all_typeconts)

    return jsonify(result)
# Run Server
"""
if __name__ == '__main__':
    app.run(debug=True)
"""
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)


