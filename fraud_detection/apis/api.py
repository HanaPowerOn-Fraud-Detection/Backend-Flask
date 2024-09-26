from flask import Blueprint, request, jsonify

# 블루프린트 정의
api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/', methods=['GET'])
def home():
    return 'Server is running!'

# 다른 API 엔드포인트들도 여기에 추가
@api_bp.route('/example', methods=['POST'])
def example():
    data = request.json
    return jsonify({"message": "Example response", "data": data}), 200
