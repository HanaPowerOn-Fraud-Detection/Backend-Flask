from flask import Blueprint, request, jsonify

# 블루프린트 정의
api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/', methods=['GET'])
def home():
    return 'Server is running!'

# CCD
@api_bp.route('/example', methods=['POST'])
def d():
    data = request.json
    return jsonify({"message": "Example response", "data": data}), 200