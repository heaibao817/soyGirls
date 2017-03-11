from flask import current_app
from itsdangerous import TimestampSigner
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    passwd = db.Column(db.String(120))

    def __init__(self, username, passwd):
        self.username = username
        self.passwd = passwd

    def __repr__(self):
        return '<User %r>' % self.username

    def check_passwd(self, passwd):
        if not self.passwd:
            return False
        print self.passwd
        print passwd
        return self.passwd == passwd

    def generate_auth_token(self,expiration=60):
        s = TimestampSigner(current_app.config['SECRET_KEY'],salt = current_app.config['SALT'])
        return s.sign(self.username)

    @staticmethod
    def verify_auth_token(token):
        s = TimestampSigner(current_app.config['SECRET_KEY'],salt = current_app.config['SALT'])
        try:
            isValidate = s.validate(token,current_app.config['EXPIRE'])
            print "isValidate:",isValidate
        except:
            return None
        if isValidate:
            username = s.unsign(token)
            print "username",username
            return User.get_user(username)
        else:
            return None

    @staticmethod
    def get_user(username):
        if not username:
            return None
        return User.query.filter_by(username = username).first()