from datetime import timedelta
from twilio.rest import Client
from flask import Blueprint, current_app, jsonify
from flask_mail import Message
from flask_pydantic import validate
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from schemas.auth import *
from config import Config
from models import Log, MessageSMS, TokenBlacklist, db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@validate()
def register(body: UserCreateSchema):
    data = body.model_dump()
    password = data.pop("password")

    user = User.query.filter_by(email=data["email"]).first()
    if user:
        return jsonify({"error": "Email already exists"}), 400

    user = User.query.filter_by(phone=data["phone"]).first()
    if user:
        return jsonify({"error": "Phone already exists"}), 400

    user = User(**data)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    Log.create_log(f"Пользователь с email {user.email} зарегистрирован")
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 201


@auth_bp.route('/login', methods=['POST'])
@validate()
def login(body: UserLoginSchema):
    user: User = User.query.filter(
        (User.email == body.login) | (User.phone == body.login)
    ).first()

    if not user:
        Log.create_log(f"Попытка входа с неверным логином {body.login}")
        return jsonify({"error": "User doesn't exist"}), 401

    if not user.check_password(body.password):
        Log.create_log(
            f"Попытка входа с неверным паролем для пользователя {body.login}")
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    Log.create_log(f"Пользователь с email {user.email} вошел в систему")
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200


@auth_bp.route('/refresh', methods=['GET'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=str(current_user))
    return jsonify({"access_token": new_access_token}), 200


@auth_bp.route('/logout', methods=['GET'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    blacklist_token = TokenBlacklist(token=jti)
    db.session.add(blacklist_token)
    db.session.commit()

    Log.create_log(f"Пользователь с ID {get_jwt_identity()} вышел из системы")
    return jsonify({"message": "Successfully logged out"}), 200


@auth_bp.route('/update', methods=['PUT'])
@jwt_required()
@validate()
def update_profile(body: UserUpdateSchema):
    current_user_id = get_jwt_identity()
    user: User = User.query.get_or_404(current_user_id)

    if body.full_name:
        user.full_name = body.full_name

    if body.email:
        users = User.query.filter(User.email == body.email, User.id != user.id)
        if users.first():
            return jsonify({"error": "Email already exists"}), 400

        user.email = body.email

    if body.phone:
        users = User.query.filter(User.phone == body.phone, User.id != user.id)
        if users.first():
            return jsonify({"error": "Phone already exists"}), 400

        user.phone = body.phone

    db.session.commit()
    Log.create_log(f"Пользователь с ID {current_user_id} обновил профиль")
    return jsonify({"message": "Profile updated successfully", }), 200


def send_reset_email(user: User, token: str):
    reset_link = f"http://yourapp.com/reset/{token}"
    msg = Message(
        subject='Password Reset Request',
        body=f"Нажмите на ссылку, чтобы сбросить пароль: {reset_link}",
        recipients=[user.email]
    )
    mail = current_app.extensions['mail']
    mail.send(msg)


def send_reset_sms(user: User, token: str):
    reset_link = f"http://yourapp.com/reset/{token}"
    client = Client(Config.TWILLIO_ACCOUNT_SID, Config.TWILLIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"Нажмите на ссылку, чтобы сбросить пароль: {reset_link}",
        from_=Config.TWILLIO_PHONE_NUMBER,
        to=user.phone
    )
    MessageSMS.create_from_twilio_message(message)
    return message


@auth_bp.route('/password/reset', methods=['POST'])
@validate()
def reset_password_request(body: UserPasswordResetSchema):
    user = User.query.filter(
        (User.email == body.login) | (User.phone == body.login)
    ).first()

    if not user:
        Log.create_log(
            f"Попытка сброса пароля для несуществующего пользователя {body.login}")
        return jsonify({"error": "User doesn't exist"}), 404

    reset_token = create_access_token(
        identity=str(user.id), expires_delta=timedelta(hours=1))

    if '@' in body.login:
        send_reset_email(user, reset_token)
    else:
        send_reset_sms(user, reset_token)

    Log.create_log(
        f"Запрос на сброс пароля для пользователя с email/телефоном {body.login}")
    return jsonify({"message": "Password reset link sent."}), 200


@auth_bp.route('/password/reset/confirm', methods=['POST'])
@jwt_required()
@validate()
def reset_password_confirm(body: UserPasswordResetConfirmSchema):
    user_id = get_jwt_identity()
    user: User = User.query.get_or_404(user_id)
    user.set_password(body.new_password)
    db.session.commit()

    Log.create_log(f"Пользователь с ID {user_id} сбросил свой пароль")
    return jsonify({"message": "Password has been reset successfully"}), 200
