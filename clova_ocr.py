import requests
import os
import json
import uuid
import time
from dotenv import load_dotenv
import fitz  # PyMuPDF

# .env 파일에서 환경 변수를 불러옴
load_dotenv()

# Clova OCR API 인증 정보 가져오기
clova_ocr_secret = os.getenv('CLOVA_SECRET_KEY')  # Clova OCR API 비밀키
apigw_url = os.getenv('CLOVA_OCR_URL')  # Clova OCR API URL
# PDF 파일 경로 설정
file_path = '/Users/juseung/Documents/Hana/result.pdf'

# PDF 파일을 이미지로 변환
doc = fitz.open(file_path)
cnt = 0
for i, page in enumerate(doc):
    # 각 페이지를 이미지로 변환
    img = page.get_pixmap()
    image_path = f'/Users/juseung/Documents/Hana/page_{i+1}.png'
    img.save(image_path)  # 이미지 저장
    print(f"Image saved at {image_path}")
    cnt += 1

image_paths = [f'/Users/juseung/Documents/Hana/page_{i+1}.png' for i in range(cnt)]
files = [('file', open(img, 'rb')) for img in image_paths]

request_json = {'images': [{'format': 'jpeg',
                            'name': 'demo'}],
                'requestId': str(uuid.uuid4()),
                'version': 'V2',
                'timestamp': int(round(time.time() * 1000))
                }

payload = {'message': json.dumps(request_json).encode('UTF-8')}

headers = {
  'X-OCR-SECRET': clova_ocr_secret
}

response = requests.request("POST", apigw_url, headers=headers, data=payload, files=files)
result = response.json()
print("\n<< OCR RESULT >>\n")
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
        print(line_text)