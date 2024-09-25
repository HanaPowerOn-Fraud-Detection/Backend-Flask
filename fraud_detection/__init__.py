# __init__.py

# board_app 모듈 초기화

# 필요한 서브 모듈을 임포트
from .views import route  # views의 route.py 임포트
from .models import model  # models의 model.py 임포트
from .schemas import schema  # schemas의 schema.py 임포트
from .apis import api  # apis의 api.py 임포트

__all__ = [
    'route',  # views 모듈의 공개 객체
    'model',  # models 모듈의 공개 객체
    'schema',  # schemas 모듈의 공개 객체
    'api',  # apis 모듈의 공개 객체
]

# 모듈 초기화와 관련된 추가 설정이나 함수 정의
def initialize():
    print("Board app이 초기화되었습니다.")
