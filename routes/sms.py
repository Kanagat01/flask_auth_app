from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from flask_pydantic import validate
from twilio.rest import Client
from config import Config
from models import Log, MessageSMS
from schemas import SMSRequest, BulkSMSRequest

sms_bp = Blueprint('sms', __name__)


@sms_bp.route('/send_sms', methods=['POST'])
@jwt_required()
@validate()
def send_sms(body: SMSRequest):
    try:
        client = Client(Config.TWILLIO_ACCOUNT_SID, Config.TWILLIO_AUTH_TOKEN)
        message = client.messages.create(
            from_=Config.TWILLIO_PHONE_NUMBER,
            body=body.body,
            to=body.to
        )
        MessageSMS.create_from_twilio_message(message)
        Log.create_log(
            f"SMS отправлено на номер {body.to} с ID сообщения {message.sid}")
        return jsonify({"message_id": message.sid, "status": message.status}), 201
    except Exception as e:
        Log.create_log(f"Ошибка при отправке SMS на номер {body.to}: {str(e)}")
        return jsonify({"error": str(e)}), 500


@sms_bp.route('/send_bulk_sms', methods=['POST'])
@jwt_required()
@validate()
def send_bulk_sms(body: BulkSMSRequest):
    try:
        client = Client(Config.TWILLIO_ACCOUNT_SID, Config.TWILLIO_AUTH_TOKEN)
        results = []
        for msg in body.messages:
            message = client.messages.create(
                from_=Config.TWILLIO_PHONE_NUMBER,
                body=msg.body,
                to=msg.to
            )
            MessageSMS.create_from_twilio_message(message)
            results.append({"status": message.status,
                           "message_id": message.sid})
            Log.create_log(
                f"SMS отправлено на номер {msg.to} с ID сообщения {message.sid}")
        return jsonify(results), 201
    except Exception as e:
        Log.create_log(f"Ошибка при массовой отправке SMS: {str(e)}")
        return jsonify({"error": str(e)}), 500


@sms_bp.route('/sms_status/<message_id>', methods=['GET'])
@jwt_required()
def sms_status(message_id):
    try:
        client = Client(Config.TWILLIO_ACCOUNT_SID, Config.TWILLIO_AUTH_TOKEN)
        message = client.messages(message_id).fetch()
        Log.create_log(f"Статус сообщения с ID {message_id}: {message.status}")
        return jsonify({
            "status": message.status,
            "to": message.to,
            "from": message.from_,
            "body": message.body
        }), 200
    except Exception as e:
        Log.create_log(
            f"Ошибка при получении статуса для сообщения с ID {message_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500
