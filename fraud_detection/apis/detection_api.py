from flask import Blueprint, request, jsonify
from fraud_detection.services.gpt_service import GPTService
from fraud_detection.services.clova_service import ClovaService
from fraud_detection.services.model_service import ModelService

detection_api = Blueprint('detection_api', __name__)

gpt_service = GPTService()
clova_service = ClovaService()
model_service = ModelService()

@detection_api.route('/detect', methods=['POST'])
def detect():
    data = request.json
    # API 호출 및 데이터 처리
    gpt_response = gpt_service.call_gpt(data['gpt_input'])
    ocr_response = clova_service.call_clova_ocr(data['ocr_input'])
    model_response = model_service.run_fine_tuned_model(data['model_input'])

    return jsonify({
        'gpt_response': gpt_response,
        'ocr_response': ocr_response,
        'model_response': model_response
    })
