from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow 
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

import uuid
import os
import jwt
import datetime

def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)

# get env vars OR ELSE
"""
POSTGRES_URL = get_env_variable("POSTGRES_URL")
POSTGRES_USER = get_env_variable("POSTGRES_USER")
POSTGRES_PW = get_env_variable("POSTGRES_PW")
POSTGRES_DB = get_env_variable("POSTGRES_DB")

POSTGRES_URL="localhost:5432"
POSTGRES_USER="uaynutb3lkpszwne"
POSTGRES_PW="aaw8nuqoofedynqohe1u9zhzq"
POSTGRES_DB="cgawsbrokerprodvcnj3rguxcvfhou"
"""
POSTGRES_URL="localhost:5432"
POSTGRES_USER="postgres"
POSTGRES_PW="NotP113!"
POSTGRES_DB="lookup_tables"

# Init
app = Flask(__name__)

port = 7880 #int(os.getenv("PORT"))


app.config['SEC_KEY'] = 'U2FsdGVkX1+d+5iG'
DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning


db = SQLAlchemy(app)


@app.route('/')
def hello_dx():
    return 'Hello DX! I am running on port ' + str(port)

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

@app.cli.command('resetdb')
def resetdb_command():
    """Destroys and creates the database + tables."""

    from sqlalchemy_utils import database_exists, create_database, drop_database
    """if database_exists(DB_URL):
        print('Deleting database.')
        drop_database(DB_URL)
    if not database_exists(DB_URL):
        print('Creating database.')
        create_database(DB_URL)
    """
    #db.drop_all()
    print('Creating tables.')
    db.create_all()
    print('Shiny!')

if __name__ == '__main__':
    app.run() #app.run(host='0.0.0.0', port=port)
