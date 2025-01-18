from flask import Blueprint, current_app, jsonify
from flask_mail import Message
from flask_pydantic import validate
from flask_jwt_extended import jwt_required
from schemas.mailing import *
from models import db, Mailing, Log

mailing_bp = Blueprint('mailing', __name__)


@mailing_bp.route('/mailing', methods=['POST'])
@jwt_required()
@validate()
def create_mailing(body: MailingCreateSchema):
    mailing = Mailing(**body.model_dump())
    db.session.add(mailing)
    db.session.commit()

    msg = Message(
        subject=mailing.subject,
        body=mailing.body,
        recipients=[mailing.recipient_email]
    )
    mail = current_app.extensions['mail']
    mail.send(msg)
    mailing.status = "sent"
    db.session.commit()

    # send_time = mailing.send_at.replace(tzinfo=timezone.utc)
    # countdown = (send_time - datetime.now(timezone.utc)).total_seconds()
    # current_app.celery.send_task(
    #     'tasks.send_email', args=[mailing.id], countdown=10)

    Log.create_log(
        f"Создана рассылка с ID {mailing.id} на email {mailing.recipient_email}")
    return jsonify({"id": mailing.id}), 201


@mailing_bp.route('/mailing/<int:id>', methods=['GET'])
@jwt_required()
def get_mailing(id: int):
    mailing: Mailing = Mailing.query.get_or_404(id)
    Log.create_log(f"Получены данные о рассылке с ID {id}")
    return jsonify({
        "id": mailing.id,
        "subject": mailing.subject,
        "body": mailing.body,
        "recipient_email": mailing.recipient_email,
        "send_at": mailing.send_at,
        "status": mailing.status
    }), 200
