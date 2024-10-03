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
    full_text = '''
                    등기사항전부증명서(말소사항 포함)
                    - 집합건물 -
                    고유번호 1501-2023-013141
                    [집합건물] 충청북도 청주시 상당구 방서동 825 동남지구호반써밋브룩사이드 제108동 제15층 제1503호
                    표제부 】 1동의 건물의 표시 )
                    표시번호 접수 소재지번,건물명칭및 번호 건물내역 등기원인 및 기타사항
                    1 2023년9월15일 충청북도 청주시 상당구 철근콘크리트구조
                    방서동 825 평슬라브지붕 25층
                    동남지구호반써밋브룩사이드 공동주택(아파트)
                    제108동 1층 289,6447m22
                    [도로명주소] 2층 299.8998m2
                    충청북도 청주시 상당구 3층 299.8998m2
                    동남로 2 4층 299.8998m2
                    5층 299.8998m2
                    6층 299.8998m2
                    7층 299.8998m2
                    8층 299.8998m2
                    9층 299.8998m2
                    10층 299.8998m2
                    열 11층 299.8998m2
                    12층 299.8998m2
                    13층 299.8998m2
                    14층 299.8998m2
                    15층 299.8998m2
                    16층 299.8998m2
                    17층 299.8998m2
                    18층 299.8998m2
                    19층 299.8998m2
                    20층 299.8998m
                    21층 299.8998
                    22층 299.8998m2
                    23층 299.8998m2
                    24층 299.8998m2
                    25층 299.8998m2
                    열람일시 : 2024년09월27일 23시54분07초 1/4
                    [집합건물] 충청북도 청주시 상당구 방서동 825 동남지구호반써밋브룩사이드 제108동 제15층 제1503호
                    ( 대지권의 목적인 토지의 표시 )
                    표시번호 소재지번 지 목 면 적 등기원인 및 기타사항
                    1 1. 충청북도 청주시 상당구 대 66210.5m2 2023년9월15일 등기
                    방서동 825
                    표제부 】 ( 전유부분의 건물의 표시 )
                    표시번호 접수 건물번호 건물내역 등기원인 및 기타사항
                    1 2023년9월15일 제15층 제1503호 철근콘크리트구조
                    74.9713m2
                    (대지권의 표시)
                    표시번호 대지권종류 대지권비율 등기원인 및 기타사항
                    1 1 소유권대지권 66210.5분의 2023년7월21일 대지권
                    48.9063
                    2023년9월15일 등기
                    2 람 별도등기 있음
                    열 1토지(갑구2-1번 금지시 행등기)
                    2023년9월15일 등가
                    3 2번 별도등기 말소
                    2023년10월31일 등기
                    갑 구 】 ( 소유권에 관한 사항 )
                    순위번호 등기목적 접수 등기원인 권리자 및 기타사항
                    1 소유권보존 2023년9월15일 소유자 주식회사호반건설 204711-0007384
                    제91633호 서울특별시 서초구 양재대로2길
                    18(우면동,호반파크2관)
                    11 금지사항등기 아 주택은 부동산등기법에 따라
                    소유권보존등기를 마친 주택으로서
                    입주예정지의 동의 없이는 양도하거나
                    제한물권을 설정하거나 압류, 기압류, 가처분
                    열람일시 : 2024년09월27일 23시54분07초 2/4
                    [집합건물] 충청북도 청주시 상당구 방서동 825 동남지구호반써밋브룩사이드 제108동 제15층 제1503호
                    순위번호 등기목적 접수 등기원인 권리자 및 기타사항
                    등 소유권에 제한을 가하는 일체의 행위를 할
                    수 없음
                    2023년9월15일 부가
                    2 소유권이전 2023년10월31일 2021년4월9일 소유자 김윤섭 840719-*******
                    제111611호 매매 충청북도 청주시 상당구 동남로 2, 108동
                    1503호 (방서동,호반써밋 브룩사이드)
                    거래가액 금290,722,000원
                    3 1-1번금지사항등기 소유권이전등기로 인하여
                    말소 2023년10월31일 등기
                    을 구 ] (소유권 이외의 권리에 관한 사항 )
                    순위번호 등기목적 접수 등기원인 권리자 및 기타사항
                    1 근저당권설정 2023년10월31일 2023년6월29일 채권최고액 금250,360,000원
                    제111612호 설정계약 채무자 김윤섭
                    충청북도 청주시 상당구 동남로 2, 108동
                    1503호 (방서동,호반써밋 브룩사이드)
                    근저당권자 주식회사우리은행 110111-0023393
                    여 라 서울특별시 중구 소공로 51(회현동1가)
                    ( 서청주지점 )
                    2 근저당권설정 2023년10월31일 2023년6월29일 채권최고액 금55,000,000원
                    제111613호 설정계약 채무자 김윤섭
                    충청북도 청주시 상당구 동남로 2, 108동
                    1503호 (방서동,호반써밋 브룩사이드)
                    근저당권자 주식회사우리은행 110111-0023393
                    서울특별시 중구 소공로 51(회현동1가)
                    ( 서청주지점 )
                    -- 이하여백 --
                    열람일시 : 2024년09월27일 23시54분07초
                    3/3
                    [집합건물] 충청북도 청주시 상당구 방서동 825 동남지구호반써밋브룩사이드 제108동 제15층 제1503호
                    관할등기소 청주지방법원 등기과
                    열람용
                    * 실선으로 그어진 부분은 말소사항을 표시함. * 기록사항 없는 갑구, 을구는 '기록사항 없음' 으로 표시함
                    * 증명서는 컬러 또는 흑백으로 출력 가능함.
                    * 본 등기사항증명서는 열람용이므로 출력하신 등기사항증명서는 법적인 효력이 없습니다.
                    열람일시 : 2024년09월27일 23시54분07초 4/4
                    주요 등기사항 요약 (참고용)
                    [주의사항]
                    본 주요 등기사항 요약은 증명서상에 말소되지 않은 사항을 간략히 요약한 것으로 증명서로서의 기능을 제공하지 않습니다.
                    실제 권리사항 파악을 위해서는 발급된 증명서를 필히 확인하시기 바랍니다.
                    고유번호 1501-2023-013141
                    [집합건물] 충청북도 청주시 상당구 방서동 825 동남지구호반써밋브룩사이드 제108동 제15층 제1503호
                    1. 소유지분현황 ( 갑구 )
                    등기명의인 (주민)등록번호 최종지분 주 소 순위번호
                    김윤섭 (소유자) 840719-******* 단독소유 충청북도 청주시 상당구 동남로 2, 108동 1503호 2
                    (방서동,호반써밋 브룩사이드)
                    2. 소유지분을 제외한 소유권에 관한 사항 ( 갑구 )
                    - 기록사항 없음
                    3. (근)저당권 및 전세권 등 ( 을구 )
                    순위번호 등기목적 접수정보 주요등기사항 대상소유자
                    1 근저당권설정 2023년10월31일 채권최고액 금250,360,000원 김윤섭
                    제111612호 근저당권자 주식회사우리은행
                    2 근저당권설정 2023년10월31일 채권최고액 금55,000,000원 김윤섭
                    제111613호 근저당권자 주식회사우리은행
                    [참고사항]
                    가. 등기기록에서 유효한 지분을 가진 소유자 혹은 공유자 현황을 가나다 순으로 표시합니다.
                    나. 최종지분은 등기명의인이 가진 최종지분이며, 2개 이상의 순위번호에 지분을 가진 경우 그 지분을 합산하였습니다.
                    다. 지분이 통분되어 공시된 경우는 전체의 지분을 통분하여 공시한 것입니다.
                    라. 대상소유자가 명확하지 않은 경우 '확인불가' 로 표시될 수 있습니다. 정확한 권리사항은 등기사항증명서를 확인하시기
                    바랍니다.
                    출력일시 : 2024년 09월 27일 23시 54분 07초
                    1/1
                '''

    # 시세 예측 로직(우선 생략)
    market_price = 400000000

    # GPT 모델을 통해 보고서 생성
    print("3단계: GPT 모델에 텍스트 전달 중...")
    gpt_service = GPTService()
    report_response, mortgage_amounts, final_evalutaion = gpt_service.call_gpt(full_text, market_price)
    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
    print("GPT 모델 응답:", report_response)
    print("추출된 근저당설정 금액 배열:", mortgage_amounts)
    print("최종 평가 결과", final_evalutaion )

    # 보고서 결과를 JSON으로 반환
    return jsonify({"report": report_response})