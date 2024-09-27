from flask import Blueprint, request, jsonify, current_app
import requests
import sys
import os
# Now you should be able to import db and RealEstate
from main.models.models import db, RealEstate

# 블루프린트 정의
api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/', methods=['GET'])
def home():
    return 'Server is running!'

@api_bp.route('/example', methods=['POST'])
def call_real_estate():
    data = request.json
    
    auth_key = current_app.config['APICK_CLIENT_API_KEY']
    
    # API 인증 키가 설정되지 않았을 때의 오류 처리
    if not auth_key:
        return jsonify({"error": "API 인증 키가 설정되지 않았습니다."}), 500

    # unique_num이 요청 데이터에 포함되어 있는지 확인
    unique_num = data.get('unique_num')
    
    if not unique_num:
        return jsonify({"error": "unique_num parameter is missing"}), 400

    # 데이터베이스에서 unique_num을 검색
    existing_record = RealEstate.query.filter_by(unique_num=unique_num).first()

    if existing_record:
        # unique_num이 데이터베이스에 이미 존재하는 경우 ic_id 사용
        ic_id = existing_record.ic_id
        
        # 두 번째 API 요청 URL
        download_url = 'https://apick.app/rest/iros_download/1'
        
        # 두 번째 API 요청
        download_response = requests.post(download_url, headers={"CL_AUTH_KEY": auth_key}, data={"ic_id": int(ic_id)})

        print("ic_id 출력값 : ", ic_id)
        print("request body 출력값 : ", download_response.request.body)

    #     # 두 번째 API 요청 결과 처리
    #     if download_response.status_code == 200:
    #         # PDF 형식의 바이너리 데이터를 변수에 저장
    #         pdf_data = download_response.content  # 바이너리 데이터
    #         pdf_path = 'result.pdf'
            
    #         # PDF 데이터를 파일로 저장
    #         with open(pdf_path, "wb") as f:
    #             f.write(pdf_data)
    #         print(f"PDF saved at {pdf_path}")
            
    #         return jsonify({"message": "PDF successfully saved", "pdf_path": pdf_path}), 200
    #     else:
    #         return jsonify({
    #             "error": "Failed to download PDF",
    #             "status": download_response.status_code,
    #             "message": download_response.text
    #         }), download_response.status_code
    # else:
    #     # unique_num이 데이터베이스에 존재하지 않는 경우 첫 번째 API 요청
    #     # 첫 번째 API 요청 URL
    #     url = 'https://apick.app/rest/iros/1'
        
    #     # 첫 번째 API 요청
    #     response = requests.post(url, headers={"CL_AUTH_KEY": auth_key}, data={"unique_num": unique_num})

    #     # 요청 정보 출력 (디버깅 용도)
    #     print(response.request.body)

    #     # 첫 번째 API 요청 결과 처리
    #     if response.status_code == 200:
    #         response_data = response.json()
    #         # ic_id 값을 추출
    #         ic_id = response_data['data'].get('ic_id')
            
    #         # ic_id가 없는 경우의 오류 처리
    #         if not ic_id:
    #             return jsonify({"error": "ic_id not found in response"}), 400
            
    #         # 새로운 레코드를 데이터베이스에 저장
    #         new_record = RealEstate(unique_num=unique_num, ic_id=ic_id)
    #         db.session.add(new_record)
    #         db.session.commit()

    #         # 두 번째 API 요청 URL
    #         download_url = 'https://apick.app/rest/iros_download/1'
            
    #         # 두 번째 API 요청
    #         download_response = requests.post(download_url, headers={"CL_AUTH_KEY": auth_key}, data={"ic_id": int(ic_id)})

    #         print("ic_id 출력값 : ", ic_id)
    #         print("request body 출력값 : ", download_response.request.body)

    #         # 두 번째 API 요청 결과 처리
    #         if download_response.status_code == 200:
    #             # PDF 형식의 바이너리 데이터를 변수에 저장
    #             pdf_data = download_response.content  # 바이너리 데이터
    #             pdf_path = 'result.pdf'
                
    #             # PDF 데이터를 파일로 저장
    #             with open(pdf_path, "wb") as f:
    #                 f.write(pdf_data)
    #             print(f"PDF saved at {pdf_path}")
                
    #             return jsonify({"message": "PDF successfully saved", "pdf_path": pdf_path}), 200
    #         else:
    #             return jsonify({
    #                 "error": "Failed to download PDF",
    #                 "status": download_response.status_code,
    #                 "message": download_response.text
    #             }), download_response.status_code

    #     else:
    #         # 첫 번째 API 요청 실패 시
    #         return jsonify({
    #             "error": "Failed to fetch data from external API",
    #             "status": response.status_code,
    #             "message": response.text
    #         }), response.status_code
