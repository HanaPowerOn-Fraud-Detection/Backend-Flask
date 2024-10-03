from flask import current_app
from openai import OpenAI

class GPTService:
    def __init__(self):
        self.secret_key = current_app.config['OPENAI_SECRET_KEY']

    def call_gpt(self, registration_text, market_price):
        try:
            # GPT 호출을 위한 클라이언트 초기화
            print("1단계: GPT 클라이언트 초기화 중...")
            client = OpenAI(api_key=self.secret_key)
            
            # GPT 모델에 전달할 메시지 생성
            print("2단계: GPT에 전달할 메시지 구성 중...")
            messages = [
                {"role": "system", "content": f'''
                                                    너는 전세 사기를 예방하기 위해서 내가 제공해준 부동산 등기부 등본을 아래의 내용을 바탕으로 보고서를 작성해줘(답변은 대한민국 언어로 해줘)
                                                    ## **갑구 체크리스트**
                                                    ### 1.ㄴ 소유주 확인

                                                    “등기목적" 열의 내용이 ‘소유권보존’, ‘소유권이전’인 행 중에서 가장 마지막 순위번호에 해당하는 행의 “권리자 및 기타사항” 열에 나타나는 소유주와 계약하려는 집주인과 동일한지 확인해야함

                                                    ### 2. 소유권 제한하는 등기 확인

                                                    “등기목적"열의 내용이

                                                    1. ‘소유권보존’, ‘소유권이전’인 행 외에는 없는 경우
                                                    → [안전]
                                                    2. ‘압류', ’가압류'인 행이 있는 경우
                                                        1. 말소된 경우 → 집주인에게 과거 보증금 반환 능력에 문제가 생긴 적 있으므로 주의 필요 [주의]
                                                        2. 말소되지 않은 경우 → 집주인이 보증금을 갚을 능력이 없다는 판결에 따라 권한 박탈 [위험]
                                                    3. ‘신탁’인 행이 있는 경우
                                                    → 현재 해당 부동산의 소유권은 신탁회사에 있음 [위험]
                                                    4. ‘임의경매개시결정’ or ‘강제경매개시결정'인 행이 있는 경우
                                                    → 집주인이 주택담보대출금을 못 갚아 집에 대한 경매가 진행 중 [위험]
                                                    5. ‘임차권’인 행이 있는 경우
                                                    → 앞서 집을 빌린 세입자가 보증금을 돌려받지 못 한 사례가 있으므로 주의 필요 [주의]
                                                    
                                                    ## **을구 체크리스트**

                                                    ### 1. 소유권 이외의 권리사항 확인

                                                    1. ‘기록사항 없음’의 경우 → [안전]
                                                    2. “등기목적"열의 내용이 ‘근저당권설정'인 행이 있는 경우 → 집주인이 주택담보대출을 갚지 못 할 경우 보증금을 전부 돌려받지 못 할 수 있음 [위험]
                                                    (시장 시세인 {market_price})에서 (해당 행의 “권리자 및 기타사항”에 나타나는 ‘채권최고액’에 해당하는 금액들의 총합)를 뺀 값이 내가 내야할 보증금보다 큰 경우 안전하고 더 작다면 경매로 넘어가더라도
                                                    차익이 보증금보다 작기 때문에 돌려받기 힘들다. 그렇기 때문에 위험하다. 그래서 저 계산 식을 통해 계약하고자하는 보증금이 얼마 이하여야 돌려받을 확률이 높아지는지 보고서에 포함시켜줘

                 '''},
                {"role": "user", "content": f"Process the following text: {registration_text}"}
            ]
            
            # GPT 모델 호출
            print("3단계: GPT 모델 호출 중...")
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )

            # GPT 응답 처리
            print("4단계: GPT 응답 처리 중...")
            print("GPT 응답 전체 구조:", completion)
            gpt_response = completion.choices[0].message.content  # 수정된 부분
            print("GPT 응답:", gpt_response)
            return gpt_response
        
        except Exception as e:
            # 오류 발생 시 로그 출력
            print(f"Error while calling GPT: {e}")
            return None
