from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def handle_data():
    data = request.json  # Google Sheets에서 받은 데이터
    print("Received data:", data)
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(port=5000)  # 5000번 포트에서 서버 실행
