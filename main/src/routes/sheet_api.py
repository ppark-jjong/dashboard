from flask import Blueprint, jsonify
from src.services.sheet_service import fetch_google_sheets_data

# Blueprint 등록
sheet_api = Blueprint("sheet_api", __name__)

@sheet_api.route("/get-sheet-data", methods=["GET"])
def get_sheet_data():
    """
    API 요청으로 Google Sheets 데이터를 가져오는 엔드포인트
    """
    try:
        data = fetch_google_sheets_data()
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
