from flask import Blueprint, jsonify

api_bp = Blueprint("api", __name__)

@api_bp.route("/delivery_data", methods=["GET"])
def get_delivery_data():
    return jsonify([
        {"배송번호": 1, "상태": "완료", "주소": "서울"},
        {"배송번호": 2, "상태": "진행중", "주소": "부산"},
    ])

@api_bp.route("/driver_data", methods=["GET"])
def get_driver_data():
    return jsonify([
        {"기사명": "김철수", "지역": "서울", "상태": "배송중"},
        {"기사명": "박영희", "지역": "부산", "상태": "대기"},
    ])
