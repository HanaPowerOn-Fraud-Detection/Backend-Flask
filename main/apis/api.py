from flask import Blueprint, request, jsonify, current_app
from main.services.apick_service import ApickService
from main.services.clova_service import ClovaService
from main.services.gpt_service import GPTService
# Now you should be able to import db and RealEstate
from main.models.models import db, RealEstate, Report
import fitz  # PyMuPDF
import os
from datetime import datetime

# 블루프린트 정의
api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/health-check', methods=['GET'])
def health_check():
    return 'ok'

@api_bp.route('/registrations', methods=['POST'])
def get_registration():
    unique_num = request.json.get('unique_num')
    print(unique_num)
    if not unique_num:
        return jsonify({
            "status_code": 404,
            "error": "페이지를 찾을 수 없습니다.",
            "message": "요청하신 데이터가 존재하지 않습니다."
        }), 404
    
    existing_record = RealEstate.query.filter_by(unique_num=unique_num).first()
    apickService = ApickService()  # ApickService 인스턴스화
    if existing_record:
        ic_id = existing_record.ic_id
        print(f"기존 레코드 발견: ic_id={ic_id}")
    else:
        try:
            # ic_id = apickService.get_ic_id(unique_num)  # unique_num을 넘겨서 메소드 호출
            print("ic_id 반환값:", ic_id)
            if not ic_id:
                print("IC ID가 반환되지 않음(Apick 부동산 등기부 등본 열람 API 요청에 실패했습니다.")
                return jsonify({
                    "status_code": 400,
                    "error": "IC ID 없음",
                    "message": "IC ID가 반환되지 않음(Apick 부동산 등기부 등본 열람 API 요청에 실패했습니다."
                }), 400
            
            new_record = RealEstate(unique_num=unique_num, ic_id=ic_id)
            db.session.add(new_record)
            db.session.commit()
            print(f"새로운 레코드 생성: unique_num={unique_num}, ic_id={ic_id}")

        except Exception as e:
            print(f"IC ID 가져오기 실패: {str(e)}")
            return jsonify({
                "status_code": 500,
                "error": "IC ID 가져오기 실패",
                "message": str(e)
            }), 500
    
    pdf_data = apickService.download_pdf(ic_id)
    print("PDF 다운로드 시도 중...")
    # existing_report = Report.query.filter_by(id = 1).first()
    # pdf_data = existing_report.registration_pdf
    # PDF 출력 디렉토리가 존재하지 않으면 생성
    pdf_output_dir = current_app.config['PDF_OUTPUT_DIR']
    os.makedirs(pdf_output_dir, exist_ok=True)
    if pdf_data:
        # real_estate = RealEstate.query.filter_by(unique_num=unique_num).first()
        # report_record = Report(real_estate_id = real_estate.id, registration_pdf=pdf_data)
        # db.session.add(report_record)
        # db.session.commit()
        print("PDF 데이터베이스에 저장 완료.")

        # 현재 시간 정보를 YYYYMMDDttmm 형식으로 포맷
        current_time = datetime.now().strftime('%Y%m%d%H%M')
        
        # 파일 이름 생성
        pdf_filename = f"{ic_id}_{current_time}.pdf"
        pdf_path = os.path.join(pdf_output_dir, pdf_filename)
        
        # PDF 파일 저장
        with open(pdf_path, "wb") as f:
            f.write(pdf_data)
        print(f"PDF 저장 완료: {pdf_path}")

        # PDF 파일을 이미지로 변환
        doc = fitz.open(pdf_path)
        image_paths = []
        image_output_dir = current_app.config['IMAGE_OUTPUT_DIR']
        os.makedirs(image_output_dir, exist_ok=True)
        print(f"이미지 출력 디렉토리 생성 완료: {image_output_dir}")

        for i, page in enumerate(doc):
            img = page.get_pixmap()
            # 이미지 파일명 생성 (PDF명_페이지번호.png)
            image_filename = f"{ic_id}_{current_time}_{i + 1}.png"
            image_path = os.path.join(image_output_dir, image_filename)  # Use the output directory
            img.save(image_path)
            print(f"이미지 저장 완료: {image_path}")
            image_paths.append(image_path)
            
        # Clova OCR API 호출
        clova_service = ClovaService()
        print("Clova OCR API 호출 중...")
        result = clova_service.get_registration_text(image_paths)

        if 'error' in result:
            print(f"OCR 처리 실패: {result['error']}")
            return jsonify({
                "status_code": 500,
                "error": "OCR 처리 실패",
                "message": result['error']
            }), 500

        extracted_texts = []
        
        for image_result in result['images']:
            fields = sorted(image_result['fields'], key=lambda x: x['boundingPoly']['vertices'][0]['y'])

            lines = []
            current_line = []
            current_line_y = fields[0]['boundingPoly']['vertices'][0]['y']

            for field in fields:
                field_y = field['boundingPoly']['vertices'][0]['y']
                
                if abs(field_y - current_line_y) > 10:
                    current_line = sorted(current_line, key=lambda x: x['boundingPoly']['vertices'][0]['x'])
                    lines.append(current_line)
                    current_line = []
                    current_line_y = field_y
                
                current_line.append(field)

            if current_line:
                current_line = sorted(current_line, key=lambda x: x['boundingPoly']['vertices'][0]['x'])
                lines.append(current_line)

            for line in lines:
                line_text = " ".join([word['inferText'] for word in line])
                extracted_texts.append(line_text)
                print(f"추출된 텍스트: {line_text}")

        return jsonify({
            "status_code": 200,
            "message": "OCR 처리 완료",
            "ic_id": ic_id,
            "extracted_texts": extracted_texts
        }), 200

    else:
        print("PDF 다운로드 실패: PDF 데이터를 다운로드하는 데 실패했습니다.")
        return jsonify({
            "status_code": 500,
            "error": "PDF 다운로드 실패",
            "message": "PDF 데이터를 다운로드하는 데 실패했습니다."
        }), 500
    
@api_bp.route('/registrations/report', methods=['GET'])
def get_report():
    # # 상대경로 기준으로 PDF 파일 경로 설정
    # pdf_path = 'output_pdf/3137313_202409280152.pdf'
    
    # # ClovaService 인스턴스 생성
    # clova_service = ClovaService()
    
    # # Clova OCR API를 호출하여 PDF에서 텍스트 추출
    # print("1단계: Clova OCR API 호출 중...")
    # ocr_result = clova_service.get_registration_text(pdf_path)
    # print("OCR API 응답:", ocr_result)
    
    # # OCR API 결과 파싱
    # print("2단계: OCR 결과 파싱 중...")
    # extracted_text = []
    # for image_result in ocr_result.get('images', []):
    #     fields = sorted(image_result.get('fields', []), key=lambda x: x['boundingPoly']['vertices'][0]['y'])
        
    #     lines = []
    #     current_line = []
    #     current_line_y = fields[0]['boundingPoly']['vertices'][0]['y'] if fields else 0

    #     for field in fields:
    #         field_y = field['boundingPoly']['vertices'][0]['y']
            
    #         if abs(field_y - current_line_y) > 10:
    #             current_line = sorted(current_line, key=lambda x: x['boundingPoly']['vertices'][0]['x'])
    #             lines.append(current_line)
    #             current_line = []
    #             current_line_y = field_y
            
    #         current_line.append(field)

    #     if current_line:
    #         current_line = sorted(current_line, key=lambda x: x['boundingPoly']['vertices'][0]['x'])
    #         lines.append(current_line)

    #     for line in lines:
    #         line_text = " ".join([word['inferText'] for word in line])
    #         extracted_text.append(line_text)

    # full_text = "\n".join(extracted_text)
    full_text = current_app.config('FULL_TEXT')
    print("추출된 전체 텍스트:\n", full_text)

    # GPT 모델을 통해 보고서 생성
    print("3단계: GPT 모델에 텍스트 전달 중...")
    gpt_service = GPTService()
    report_response = gpt_service.call_gpt(full_text)
    print("GPT 모델 응답:", report_response)

    # 보고서 결과를 JSON으로 반환
    return jsonify({"report": report_response})