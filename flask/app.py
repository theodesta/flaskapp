from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow 

import os
# Init
app = Flask(__name__)


#@app.route('/', methods=['GET'])
#def get():
#    return jsonify({'msg' : 'Hello DX World!'})

#DB
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

#Init DB
db = SQLAlchemy(app)
ma = Marshmallow(app)


# SAM Class

class Sam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(100))
    #price = db.Column(db.Float)
    
    def __init__(self,code,description):
        self.code = code
        self.description = description

# Schema
class SamSchema(ma.Schema):
    class Meta:
        fields = ('id', 'code', 'description')

# init schema
sam_schema = SamSchema() # strict='True'

sams_schema = SamSchema(many=True)  #many=True, strict='True'

#Create a SAM
@app.route('/sam', methods=['POST'])
def add_sam():
    code = request.json['code']
    description = request.json['description']

    new_sam = Sam(code, description)

    db.session.add(new_sam)
    db.session.commit()

    return sam_schema.jsonify(new_sam)

#Get all SAMS
@app.route('/sam', methods=['GET'])
def get_sams():
    all_sams = Sam.query.all()
    result = sams_schema.dump(all_sams)

    return jsonify(result)

#Get single SAMS
@app.route('/sam/<id>', methods=['GET'])
def get_sam(id):
    sam = Sam.query.get(id)
    
    return sam_schema.jsonify(sam)

#Update SAM
@app.route('/sam/<id>', methods=['PUT'])
def update_sam(id):
    sam = Sam.query.get(id)
    
    code = request.json['code']
    description = request.json['description']

    sam.code = code
    sam.description = description

    db.session.commit()

    return sam_schema.jsonify(sam)

"""
#Delete SAM
@app.route('/sam/<id>', methods=['DELETE'])
def delete_sam(id):
    sam = Sam.query.get(id)
    db.session.delete(sam)
    db.session.commit()

    return sam_schema.jsonify(sam)
"""
#Run Server
if __name__ == '__main__':
    app.run(debug=True)


