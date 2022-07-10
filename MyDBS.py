from enum import unique
from flask_sqlalchemy import SQLAlchemy
from flask import *
from threaded_server import db
from flask_login import UserMixin

class Login(db.Model,UserMixin):
    __table_args__ = {'extend_existing': True} 
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(60),unique=True,nullable=False)
    username = db.Column(db.String(20),unique=True,nullable=False)
    password = db.Column(db.String(60),nullable=False)

    def __repr__(self):
        return "{}, {}, {}".format(self.id,self.username,self.password)

    def isauthenticated(self):
        return True

#db.create_all()

#test1 = Login(id=1,email="test1@mail.com",username="test1",password="test1")
#test2 = Login(id=2,email="test2@mail.com",username="test2",password="test2")

#db.session.add(test1)
#db.session.add(test2)
#db.session.commit()

print(Login.query.all())
