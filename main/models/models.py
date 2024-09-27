from flask_sqlalchemy import SQLAlchemy
import pytz
from datetime import datetime

# SQLAlchemy 초기화
db = SQLAlchemy()
KST = pytz.timezone('Asia/Seoul')

# 부동산 모델 정의
class RealEstate(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)  # 자동 증가하는 BIGINT 타입 ID
    unique_num = db.Column(db.String(20), unique=True, nullable=False)   # 부동산 고유 번호
    ic_id = db.Column(db.Integer, nullable=False)                        # IC ID

    def __repr__(self):
        return f'<RealEstate unique_num={self.unique_num}, ic_id={self.ic_id}>'

# 보고서 모델 정의
class Report(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)  # 자동 증가하는 BIGINT 타입 ID
    real_estate_id = db.Column(db.BigInteger, db.ForeignKey('real_estate.id'), nullable=True)  # Foreign key referencing RealEstate
    created_at = db.Column(db.DateTime, default=datetime.now(KST))  # 생성일
    registration_pdf = db.Column(db.LargeBinary(length=None), nullable=False)  # LONGBLOB

    # 외래키 관계 설정 (선택적)
    real_estate = db.relationship('RealEstate', backref='reports', lazy=True)

    def __repr__(self):
        return f'<Report id={self.id}, real_estate_id={self.real_estate_id}>'
