from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_mail import Mail
from models import db, bcrypt
from routes import *


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    mail = Mail(app)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = TokenBlacklist.query.filter_by(token=jti).first()
        return token is not None

    db.init_app(app)
    bcrypt.init_app(app)

    Migrate(app, db)
    app.register_blueprint(auth_bp)
    app.register_blueprint(sms_bp)
    app.register_blueprint(mailing_bp)
    app.register_blueprint(logs_bp)

    return app
