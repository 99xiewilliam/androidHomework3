import json
import datetime
from flask import Flask,make_response,request
import mysql.connector
from math import ceil

from flask_sqlalchemy import SQLAlchemy
# import pymysql
from flask import jsonify
# pymysql.install_as_MySQLdb()

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://xiaohao:123456@127.0.0.1/iems5722'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
# db = SQLAlchemy(app)


# class Chatrooms(db.Model):
#     __tablename__ = 'chatrooms'
#
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), unique=True)
#
#     def __repr__(self):
#         return 'chatroom:%s' %self.name
#
# class Messages(db.Model):
#     __tablename__ = 'messages'
#     id = db.Column(db.Integer, primary_key=True)
#     chatroom_id = db.Column(db.Integer)
#     user_id = db.Column(db.Integer)
#     name = db.Column(db.String(100))
#     message = db.Column(db.String(200))
#     message_time = db.Column(db.String(100))

db = mysql.connector.connect(
    host="localhost",
    user="xiaohao",
    passwd="123456",
    database="iems5722"
)

cursor = db.cursor()

@app.route('/hello')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/api/a3/get_chatrooms', methods=['GET'])
def get_chatrooms():
    # rooms = Chatrooms.query.all()
    sql = "select * from chatrooms"
    cursor.execute(sql)
    rooms = cursor.fetchall()
    carry = []
    if len(rooms) != 0:
        for row in rooms:
            id = row[0]
            name = row[1]
            jsonObj = {"id" : id, "name": name}
            carry.append(jsonObj)


    data = {'data':str(carry),'status':'OK'}
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.mimetype = 'application/json'
    return response

@app.route('/api/a3/get_messages', methods=['GET'])
def get_messages():
    # db1 = pymysql.connect(host='localhost',
    #                       user='xiaohao',
    #                       password='123456',
    #                       database='iems5722')
    # cursor = db1.cursor()
    args1 = request.args.get("chatroom_id")
    args2 = request.args.get("page")
    print(args1)
    print(args2)
    if args1 is None or args2 is None:
        data = {
            "message": "<error message>",
            "status": "ERROR"
        }
        response = make_response(json.dumps(data, ensure_ascii=False))
        response.mimetype = 'application/json'
        return response

    # lit = Messages.query.filter(Messages.chatroom_id == int(args1)).order_by(Messages.message_time.desc()).all()
    sql = 'SELECT messages.id AS messages_id, messages.chatroom_id AS messages_chatroom_id, messages.user_id AS messages_user_id, messages.name AS messages_name, messages.message AS messages_message, messages.message_time AS ' \
          'messages_message_time FROM messages WHERE messages.chatroom_id = ' + str(args1) + " ORDER BY messages.message_time DESC"

    # try:
    #     cursor.execute(sql)
    #     results = cursor.fetchall()
    #     print(results)
    # except:
    #     print("wrong")
    #
    # db1.close()
    cursor.execute(sql)
    results = cursor.fetchall()
    total_pages = ceil(len(results) / 5)
    messages = []
    if total_pages >= int(args1):
        length = int(args2) * 5
        if len(results) < length:
            length = len(results)

        if length - 5 < 0:
            start = 0
        else:
            start = int(args1) * 5 - 5

        for i in range(start, length):
            message = results[i][4]
            name = results[i][3]
            message_time = results[i][5]
            user_id = results[i][2]
            jsonObj = {"message": message, "name": name, "message_time": str(message_time), "user_id": user_id}
            messages.append(jsonObj)

    data = {
        "current_page": int(args2),
        "messages": messages,
        "total_pages": ceil(len(results) / 5)
    }
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.mimetype = 'application/json'
    return response

@app.route('/api/a3/send_message', methods=['POST'])
def send_message():
    return ''

if __name__ == '__main__':
    app.run(host='0.0.0.0',port='5000',debug=True)
