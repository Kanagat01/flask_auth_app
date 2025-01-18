from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(
            password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Mailing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    recipient_email = db.Column(db.String(255), nullable=False)
    send_at = db.Column(db.DateTime, nullable=False,
                        default=datetime.now(timezone.utc))
    status = db.Column(db.String(50), default='pending')


class MessageSMS(db.Model):
    # тот же id, что и в twilio
    id = db.Column(db.String(255), primary_key=True)
    body = db.Column(db.Text, nullable=False)
    to = db.Column(db.String(20), nullable=False)
    from_ = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    @staticmethod
    def create_from_twilio_message(message):
        new_message = MessageSMS(
            id=message.sid, body=message.body, to=message.to, from_=message.from_)
        db.session.add(new_message)
        db.session.commit()


class TokenBlacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(
        timezone.utc), nullable=False)

    @staticmethod
    def create_log(message: str):
        log = Log(message=message)
        db.session.add(log)
        db.session.commit()
