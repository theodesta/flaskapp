from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

import uuid
import os
import jwt
import datetime

app = Flask(__name__)
# DB
#basedir = os.path.abspath(os.path.dirname(__file__))
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')

POSTGRES_URL="localhost:5432"
POSTGRES_USER="postgres"
POSTGRES_PW="NotP113!"
POSTGRES_DB="lookup_tables"

app.config['SEC_KEY'] = 'U2FsdGVkX1+d+5iG'
DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init DB
db = SQLAlchemy(app)
ma = Marshmallow(app)
class SamBusinessTypes(db.Model):
    businessTypeCode = db.Column(db.String(2), primary_key=True)
    businessTypeName = db.Column(db.String(100))

# Schema
class SamBustypesSchema(ma.Schema):
    class Meta:
        fields = ('businessTypeCode', 'businessTypeName')


# init schema
sambustypes_schema = SamBustypesSchema()  # strict='True'

sambustypess_schema = SamBustypesSchema(many=True)  # many=True, strict='True'

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

# Get all SAMS
@app.route('/sambustypes', methods=['GET'])
@require_token
def get_sambustypes():
    all_sambustypes = SamBusinessTypes.query.all()
    result = sambustypess_schema.dump(all_sambustypes)

    return jsonify(result)

@app.route('/unprotected')
def unprotected():
    return jsonify({'message': 'Free content'})


@app.route('/protected')
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
    # return jsonify({'msg' : 'Hello DX World!'})



# SAM Class

class Sam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, primary_key=True)
    description = db.Column(db.String(100))

    # price = db.Column(db.Float)

    def __init__(self, code, description):
        self.code = code
        self.description = description


# Schema
class SamSchema(ma.Schema):
    class Meta:
        fields = ('id', 'code', 'description')


# init schema
sam_schema = SamSchema()  # strict='True'

sams_schema = SamSchema(many=True)  # many=True, strict='True'


# Create a SAM
@app.route('/sam', methods=['POST'])
def add_sam():
    code = request.json['code']
    description = request.json['description']

    new_sam = Sam(code, description)

    db.session.add(new_sam)
    db.session.commit()

    return sam_schema.jsonify(new_sam)


# Get all SAMS
@app.route('/sam', methods=['GET'])
def get_sams():
    all_sams = Sam.query.all()
    result = sams_schema.dump(all_sams)

    return jsonify(result)


# Get single SAMS
@app.route('/sam/<id>', methods=['GET'])
def get_sam(id):
    sam = Sam.query.get(id)

    return sam_schema.jsonify(sam)


# Update SAM
@app.route('/sam/<id>', methods=['PUT'])
def update_sam(id):
    sam = Sam.query.get(id)

    code = request.json['code']
    description = request.json['description']

    sam.code = code
    sam.description = description

    db.session.commit()

    return sam_schema.jsonify(sam)


# Delete SAM
@app.route('/sam/<id>', methods=['DELETE'])
def delete_sam(id):
    sam = Sam.query.get(id)
    db.session.delete(sam)
    db.session.commit()

    return sam_schema.jsonify(sam)


# Run Server
if __name__ == '__main__':
    app.run(debug=True)


