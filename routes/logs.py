from flask import Blueprint, jsonify
from models import Log


logs_bp = Blueprint('logs', __name__)


@logs_bp.route('/logs', methods=['GET'])
def get_logs():
    logs: list[Log] = Log.query.all()
    log_list = [{"id": log.id, "message": log.message,
                 "timestamp": log.timestamp} for log in logs]
    return jsonify(log_list), 200
