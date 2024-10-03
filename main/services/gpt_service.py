from flask import current_app
from openai import OpenAI
import re

class GPTService:
    def __init__(self):
        self.secret_key = current_app.config['OPENAI_SECRET_KEY']

    def extract_mortgage_and_evaluation(self, response_text):
        # '근저당설정: [n1, n2, ...]' 패턴에서 숫자 추출
        mortgage_pattern = r"근저당설정:\s*\[([0-9,\s]+)\]"
        mortgage_match = re.search(mortgage_pattern, response_text)

        if mortgage_match:
            # 콤마와 공백을 제거한 후 숫자들을 배열로 변환
            mortgage_amounts = [int(x.strip().replace(",", "")) for x in mortgage_match.group(1).split(',')]
        else:
            mortgage_amounts = []

        # '최종 평가: 위험' 또는 '최종 평가: 주의' 또는 '최종 평가: 안전' 패턴에서 최종 평가 추출
        evaluation_pattern = r"최종 평가:\s*(위험|주의|안전)"
        evaluation_match = re.search(evaluation_pattern, response_text)

        if evaluation_match:
            final_evaluation = evaluation_match.group(1)
        else:
            final_evaluation = None

        return mortgage_amounts, final_evaluation

    def call_gpt(self, registration_text, market_price):
        try:
            # GPT 호출을 위한 클라이언트 초기화
            print("1단계: GPT 클라이언트 초기화 중...")
            client = OpenAI(api_key=self.secret_key)
            
            # GPT 모델에 전달할 메시지 생성
            print("2단계: GPT에 전달할 메시지 구성 중...")
            messages = [{
                        "role": "system",
                        "content": f'''
                            너는 사용자가 제공한 부동산 등기부 등본을 분석하여 전세 사기를 예방할 수 있도록 보고서를 작성하는 역할을 맡고 있어.
                            아래는 부동산 등기부 등본을 분석하는 데 필요한 체크리스트야. 이 체크리스트를 바탕으로 사용자가 요청한 보고서를 작성해야 해.

                            갑구 체크리스트
                            1. 소유주 확인
                                - "등기목적" 열에 '소유권보존' 또는 '소유권이전'이 표시된 마지막 순위번호 행을 확인.
                                - 그 행의 "권리자 및 기타사항" 열에 나타나는 소유주와 계약하려는 집주인이 동일한지 확인해야 함.

                            2. 소유권을 제한하는 등기 확인
                                - "등기목적" 열의 내용이 다음 중 하나인지 확인:
                                    1. '소유권보존' 또는 '소유권이전'만 있는 경우 → [안전]
                                    2. '압류', '가압류'인 경우:
                                        - 말소된 경우: 과거에 보증금 반환 능력에 문제가 있었으므로 주의 필요 [주의].
                                        - 말소되지 않은 경우: 보증금을 갚을 능력이 없다는 판결로 권한 박탈 [위험].
                                    3. '신탁'인 경우 → 부동산 소유권이 신탁회사에 있음 [위험].
                                    4. '임의경매개시결정' 또는 '강제경매개시결정'인 경우 → 집주인이 대출금을 갚지 못해 경매가 진행 중 [위험].
                                    5. '임차권'인 경우 → 앞서 세입자가 보증금을 돌려받지 못한 사례가 있으므로 주의 필요 [주의].

                            을구 체크리스트
                            1. 소유권 외의 권리사항 확인
                                - "기록사항 없음"이면 → [안전].
                                - '근저당권설정'이 있는 경우 → 대출 상환을 못할 경우 보증금 반환이 어려울 수 있음 [위험].
                                이 경우, 시장 시세 {market_price}에서 모든 채권최고액을 합산한 값(예: 250,360,000원과 55,000,000원을 더한 값)을 뺀 결과가 보증금보다 큰지 확인.
                                그 값이 보증금보다 크면 안전하지만, 작으면 경매로 넘어갈 때 보증금을 돌려받기 어려움.
                                이 계산 결과를 바탕으로 안전한 보증금 범위를 보고서에 포함시켜야 해.

                            여기까지가 체크가 필요한 리스트이고 각각의 체크리스트에 대해 실제 등기부 등본과 비교하여 처리해서 레포트를 작성해주고 최대한 근거를 잘 포함시켜서 작성해줘.
                            이때 반환 시에 사람이 이해하기 쉽도록 가독성 좋도록 잘 풀어서 최대한 자세하게 "~합니다" 말투로 반환해주면 좋겠어
                            가장 마지막에 종합적으로 위험 요소가 하나라도 있으면 '최종 평가: 위험', 위험 없이 주의가 있으면 '최종 평가: 주의', 모두 다 안전이면 '최종 평가: 안전' 이라고 한줄 적어주고
                            또 그 밑에 가장 마지막 줄에 '근저당설정: [n1,n2, ...]' 이런식으로 배열로 반환해. 그때 반환 시 근저당설정 금액 배열을 ex) "[250360000, 55000000]" 형식으로 반환해줘. 콤마로 구분된 숫자 내에서 각 숫자를 잘라서는 안 돼.
                        '''
                    },
                    {
                        # 사용자 입력 텍스트를 처리하여 보고서를 작성해야 한다는 요청
                        "role": "user",
                        "content": f"Process the following text: {registration_text}"
                    }
            ]

            # GPT 모델 호출
            print("3단계: GPT 모델 호출 중...")
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )

            # GPT 응답 처리
            print("4단계: GPT 응답 처리 중...")
            gpt_response = completion.choices[0].message.content

            # ** 및 ### 제거하여 읽기 쉽게 변환
            clean_response = gpt_response.replace("**", "").replace("####", "\n").replace("###", "\n")

            # 근저당권 금액 추출
            mortgage_amounts, final_evaluation = self.extract_mortgage_and_evaluation(clean_response)

            # 최종 결과와 근저당 금액 배열 반환
            return clean_response, mortgage_amounts, final_evaluation
        
        except Exception as e:
            # 오류 발생 시 로그 출력
            print(f"Error while calling GPT: {e}")
            return None