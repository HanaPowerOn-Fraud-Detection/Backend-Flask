from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    # 400 에러 처리
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "status": 400,
            "error": "잘못된 요청",
            "message": str(error)
        }), 400

    # 404 에러 처리
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "페이지를 찾을 수 없습니다.",
            "status": 404,
            "message": "요청하신 URL을 찾을 수 없습니다. URL을 확인하고 다시 시도해주세요."
        }), 404

    # 500 에러 처리
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "status": 500,
            "error": "서버 내부 오류",
            "message": "서버에서 문제가 발생했습니다."
        }), 500

    # HTTPException 처리 (기타 HTTP 관련 예외)
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({
            "status": e.code,
            "error": e.name,
            "message": e.description
        }), e.code

    # 처리되지 않은 예외 전역 처리
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        return jsonify({
            "status": 500,
            "error": "예기치 않은 오류",
            "message": str(error)
        }), 500
