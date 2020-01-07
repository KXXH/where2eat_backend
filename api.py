# coding=utf8
from flask import Flask,abort,request,g
from flask_cors import CORS
import secrets
import json
import sqlite3
from functools import wraps
app=Flask(__name__)
CORS(app, supports_credentials=True)

tokenDict={

}

@app.route('/restaurants')
def restaurants():
    db=get_db()
    c=db.cursor()
    sql="""
    SELECT 
        a.id as id,
        b.name as parent_name,
        a.name as name 
    FROM restaurants a 
    JOIN restaurants b 
        ON a.parent=b.id 
    UNION 
        SELECT 
            id,
            name AS parent_name,
            name 
        FROM restaurants c 
        WHERE 
            parent IS NULL AND 
            NOT EXISTS (
                SELECT * FROM restaurants WHERE parent=c.id
            )
    """
    c.execute(sql)
    d={}
    for item in c.fetchall():
        d.setdefault(item[1],{"name":item[1],"children":[]})
        d[item[1]]['children'].append(item[2])
    print(d.values())
    return json.dumps(list(d.values()))

@app.route('/login',methods=["POST"])
def login():
    data=request.get_json()
    ans=login(**data)
    if ans:
        return json.dumps({'token':ans})
    else:
        abort(401)

@app.route('/logout')
def logout():
    token=request.headers['Authorization']
    if not token or token not in tokenDict:
        abort(401)
    else:
        del tokenDict[token]
        return "ok"

def login_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        print(request.headers)
        token = request.headers['Authorization']
        if not token or token not in tokenDict:
            abort(401)
        else:
            g.user=tokenDict[token]
            return func(*args,**kwargs)
    return wrapper

@app.route('/record',methods=['POST','GET'])
@login_required
def record():
    user=g.user
    print(user)
    assert user is not None
    if request.method=="POST":
        data=request.get_json()
        db=get_db()
        sql="INSERT INTO record (place,time,user) VALUES(?,?,?)"
        c=db.cursor()
        c.execute(sql,(data['restaurant'],data['date'],user))
        db.commit()
        return "ok"
    elif request.method=="GET":
        sql="SELECT place,time FROM record WHERE user=? ORDER BY time DESC"
        db=get_db()
        c=db.cursor()
        c.execute(sql,(user,))
        ans=c.fetchall()
        print(ans)
        return json.dumps(ans)


def login(username,password):
    db=get_db()
    sql="SELECT * FROM user WHERE username=? AND password=?"
    c=db.cursor()
    ans=c.execute(sql,(username,password)).fetchall()
    if len(ans):
        token=tokenGen()
        while token in tokenDict:
            token=tokenGen()
        tokenDict[token]=username
        print(tokenDict)
        return token
    else:
        return None

def tokenGen():
    return secrets.token_hex(16)

def get_db(flag=False):
    db=sqlite3.connect(
            "where2eatdb",
            detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row
    if flag:
        return db
    else:
        if 'db' not in g:
            g.db = sqlite3.connect(
                "where2eatdb",
                detect_types=sqlite3.PARSE_DECLTYPES
            )
        return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db=get_db(True)
    sql='''
    CREATE TABLE IF NOT EXISTS "record" (
        "id"	INTEGER PRIMARY KEY AUTOINCREMENT,
        "place"	TEXT,
        "time"	TEXT,
        "user"	INTEGER
    );
    '''
    c=db.cursor()
    c.execute(sql)
    sql='''
    CREATE TABLE IF NOT EXISTS "user" (
        "username"	TEXT,
        "password"	TEXT NOT NULL,
        PRIMARY KEY("username")
    );
    '''
    c.execute(sql)
    sql='''
    CREATE TABLE IF NOT EXISTS "restaurants" (
        "id"	INTEGER PRIMARY KEY AUTOINCREMENT,
        "name"	TEXT,
        "parent"	INTEGER
    );
    '''
    db.commit()
    db.close()

def init_app(app):
    init_db()
    app.teardown_appcontext(close_db)



init_app(app)
app.run()
