import json
import datetime
import time
from flask import Flask,make_response,request
from firebase_admin import messaging
import mysql.connector
from math import ceil
from task import send_notification

from flask_sqlalchemy import SQLAlchemy
# import pymysql
from flask import jsonify
# pymysql.install_as_MySQLdb()

#生成app执行flask
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

##连接数据库配置
#db = mysql.connector.connect(
#    host="localhost",
#    user="xiaohao",
#    passwd="123456",
#    database="iems5722"
#)

#cursor = db.cursor()

@app.route('/hello')
def hello_world():  # put application's code here
    return 'Hello World!'

##获取聊天室
@app.route('/api/a3/get_chatrooms', methods=['GET'])
def get_chatrooms():
    # rooms = Chatrooms.query.all()
    db = mysql.connector.connect(
        host="localhost",
        user="xiaohao",
        passwd="123456",
        database="iems5722"
    )
    cursor = db.cursor()
    sql = "select * from chatrooms"
    cursor.execute(sql)
    rooms = cursor.fetchall()
    carry = []
    if len(rooms) != 0:
        for row in rooms:
            id = row[0]
            name = row[1]
            jsonObj = {"id": id, "name": name}
            carry.append(jsonObj)


    data = {'data':carry,'status':'OK'}
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.mimetype = 'application/json'
    cursor.close()
    db.close();
    return response

##获取对应聊天室的内容
@app.route('/api/a3/get_messages', methods=['GET'])
def get_messages():
    # db1 = pymysql.connect(host='localhost',
    #                       user='xiaohao',
    #                       password='123456',
    #                       database='iems5722')
    # cursor = db1.cursor()
    db = mysql.connector.connect(
        host="localhost",
        user="xiaohao",
        passwd="123456",
        database="iems5722"
    )
    cursor = db.cursor()
    chatroom_id = request.args.get("chatroom_id")
    page = request.args.get("page")
    print(chatroom_id)
    print(page)
    #如果参数存在错误返回错误信息提示
    if chatroom_id is None or page is None:
        data = {
            "message": "<error message>",
            "status": "ERROR"
        }
        response = make_response(json.dumps(data, ensure_ascii=False))
        response.mimetype = 'application/json'
        cursor.close()
        db.close()
        return response

    # lit = Messages.query.filter(Messages.chatroom_id == int(args1)).order_by(Messages.message_time.desc()).all()
    sql = 'SELECT messages.id AS messages_id, messages.chatroom_id AS messages_chatroom_id, messages.user_id AS messages_user_id, messages.name AS messages_name, messages.message AS messages_message, messages.message_time AS ' \
          'messages_message_time FROM messages WHERE messages.chatroom_id = ' + str(chatroom_id) + " ORDER BY messages.message_time DESC"

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
    print(total_pages)
    messages = []
    #确保请求的页面比总页面小
    if total_pages >= int(page):
        #假设每个page有5条信息
        length = int(page) * 5
        if len(results) < length:
            length = len(results)

        if length - 5 < 0:
            start = 0
        else:
            start = int(page) * 5 - 5

        for i in range(start, length):
            message = results[i][4]
            name = results[i][3]
            message_time = results[i][5]
            user_id = results[i][2]
            jsonObj = {"message": message, "name": name, "message_time": str(message_time), "user_id": user_id}
            messages.append(jsonObj)

    data = {
        "current_page": int(page),
        "messages": messages,
        "total_pages": ceil(len(results) / 5)
    }
    data1 = {"data": data, "status": "OK"}
    response = make_response(json.dumps(data1, ensure_ascii=False))
    response.mimetype = 'application/json'
    cursor.close()
    db.close()
    return response

##给对应聊天室发信息
@app.route('/api/a3/send_message', methods=['POST'])
def send_message():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="xiaohao",
            passwd="123456",
            database="iems5722"
        )
        cursor = db.cursor()
        postParam = request.form
        chatroom_id = postParam.get("chatroom_id")
        user_id = postParam.get("user_id")
        name = postParam.get("name")
        message = postParam.get("message")
        message_time = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        print(chatroom_id+user_id+name+message)
        sql = "INSERT INTO messages (chatroom_id,user_id,name,message,message_time) VALUES (%s, %s, %s, %s, %s)"
        val = (chatroom_id, user_id, name, message, message_time)
        cursor.execute(sql, val)
        db.commit()
        print("insert successfully", cursor.lastrowid)

        sql = "select * from push_tokens"
        cursor.execute(sql)
        #db.commit()
        user_tokens = cursor.fetchall()
        print('99999999999999999999999999')
        print(user_tokens)
        print('88888888888888888888888888')
        carry = []
        if len(user_tokens) != 0:
            for row in user_tokens:
                tokens = row[2]
                carry.append(str(tokens))

        sql = "select chatrooms.name from chatrooms where chatrooms.id = " + str(chatroom_id)
        cursor.execute(sql)
        result_names = cursor.fetchall()

        chatroom_name = ''
        if len(result_names) != 0:
            for row in result_names:
                chatroom_name = row[0]


        cursor.close()
        db.close()

        send_notification.delay(carry, chatroom_name, message)


    except:
        data = {
            "message": "<error message>",
            "status": "ERROR"
        }
        response = make_response(json.dumps(data, ensure_ascii=False))
        response.mimetype = 'application/json'
        return response

    data = {"status": "OK"}
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.mimetype = 'application/json'
    return response

@app.route('/api/a4/submit_push_token', methods=['POST'])
def get_token():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="xiaohao",
            passwd="123456",
            database="iems5722"
        )
        cursor = db.cursor()
        postParam = request.form
        user_id = postParam.get("user_id")
        token = postParam.get("token")
        sql = "INSERT INTO push_tokens (user_id, token) VALUES (%s, %s)"
        val = (user_id, token)
        cursor.execute(sql, val)
        db.commit()
        print("insert successfully", cursor.lastrowid)
        cursor.close()
        db.close()
    except:
        data = {
            "message": "<error message>",
            "status": "ERROR"
        }
        response = make_response(json.dumps(data, ensure_ascii=False))
        response.mimetype = 'application/json'
        return response

    data = {"status": "OK"}
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.mimetype = 'application/json'
    return response



if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
