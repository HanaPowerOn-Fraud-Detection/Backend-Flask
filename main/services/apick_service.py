import requests
from flask import current_app

class ApickService:
    def __init__(self):
        # 첫 번째 API 요청 URL
        self.get_icid_url = "https://apick.app/rest/iros/1"
        # 두 번째 API 요청 URL (PDF 다운로드)
        self.get_pdf_url = "https://apick.app/rest/iros_download/1"
        # API 키 가져오기
        self.auth_key = current_app.config['APICK_CLIENT_API_KEY']

    def get_ic_id(self, unique_num):
        """
        첫 번째 API 호출 - IC ID를 가져오는 함수
        :param unique_num: 요청에 필요한 고유 번호
        :return: IC ID
        """
        # 요청 헤더 설정
        headers = {"CL_AUTH_KEY": self.auth_key}
        # 요청 데이터 설정
        data = {"unique_num": unique_num}

        # 첫 번째 API 요청 (IC ID 가져오기)
        try:
            response = requests.post(self.get_icid_url, headers=headers, data=data)
            response.raise_for_status()
            print("------ICID 요청 API Response------")
            response_data = response.json()
            return response_data['data'].get('ic_id')
        except requests.exceptions.RequestException as e:
            print(f"Error while fetching IC ID: {e}")
            return None

    def download_pdf(self, ic_id):
        """
        두 번째 API 호출 - IC ID로 PDF 다운로드
        :param ic_id: 첫 번째 요청에서 받은 IC ID
        :return: PDF 파일의 바이너리 데이터
        """
        # 요청 헤더 설정
        headers = {"CL_AUTH_KEY": self.auth_key}
        # 요청 데이터 설정
        data = {"ic_id": int(ic_id)}

        # 두 번째 API 요청 (PDF 다운로드)
        try:
            print("------PDF 다운로드 API Request------")
            response = requests.post(self.get_pdf_url, headers=headers, data=data)
            response.raise_for_status()
            return response.content  # PDF 파일의 바이너리 데이터 반환
        except requests.exceptions.RequestException as e:
            print(f"Error while downloading PDF: {e}")
            return None