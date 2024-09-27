from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy 초기화
db = SQLAlchemy()

# 부동산 모델 정의
class RealEstate(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)  # 자동 증가하는 BIGINT 타입 ID
    unique_num = db.Column(db.String(20), unique=True, nullable=False)   # 부동산 고유 번호
    ic_id = db.Column(db.BigInteger, nullable=False)                       # IC ID

    def __repr__(self):
        return f'<RealEstate unique_num={self.unique_num}, ic_id={self.ic_id}>'