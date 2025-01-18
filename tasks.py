from celery import shared_task
from flask_mail import Message
from datetime import datetime, timedelta, timezone
from models import Mailing, db, TokenBlacklist
from run import celery, app
from config import Config

import logging

logger = logging.getLogger(__name__)


@shared_task
def send_email(mailing_id: int):
    with app.app_context():
        try:
            mailing: Mailing = Mailing.query.get_or_404(mailing_id)
            msg = Message(
                subject=mailing.subject,
                recipients=[mailing.recipient_email],
                body=mailing.body
            )
            mail = app.extensions['mail']
            mail.send(msg)

            mailing.status = "sent"
            db.session.commit()
            return f"Отправлена рассылка на email: {mailing.recipient_email}"
        except Exception as e:
            return str(e)


@celery.task
def delete_expired_tokens():
    expiration_time = datetime.now(
        timezone.utc) - timedelta(seconds=Config.JWT_REFRESH_TOKEN_EXPIRES)
    expired_tokens = TokenBlacklist.query.filter(
        TokenBlacklist.created_at < expiration_time).all()

    for token in expired_tokens:
        db.session.delete(token)
    db.session.commit()
