import json

from flask import Flask,make_response,request
from flask_sqlalchemy import SQLAlchemy
import pymysql
from flask import jsonify
pymysql.install_as_MySQLdb()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://xiaohao:123456@127.0.0.1/iems5722'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Chatrooms(db.Model):
    __tablename__ = 'chatrooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

    def __repr__(self):
        return 'chatroom:%s' %self.name

class Messages(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    chatroom_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(100))
    message = db.Column(db.String(200))
    message_time = db.Column(db.String(100))


@app.route('/hello')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/api/a3/get_chatrooms', methods=['GET'])
def get_chatrooms():
    rooms = Chatrooms.query.all()
    data = {'data':str(rooms),'status':'OK'}
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.mimetype = 'application/json'
    return response

@app.route('/api/a3/get_messages', methods=['GET'])
def get_messages():
    args1 = request.args.get("chatroom_id")
    args2 = request.args.get("page")
    if args1 is None or args2 is None:
        data = {
            "message": "<error message>",
            "status": "ERROR"
        }
        response = make_response(json.dumps(data, ensure_ascii=False))
        response.mimetype = 'application/json'
        return response

    return str(args1) + str(args2)

@app.route('/api/a3/send_message', methods=['POST'])
def send_message():
    return ''

if __name__ == '__main__':
    app.run(host='0.0.0.0',port='5000',debug=True)
