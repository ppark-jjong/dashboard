from flask import Flask, jsonify, request
import redis

app = Flask(__name__)

# Redis 클라이언트 설정
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


@app.route('/add_delivery', methods=['POST'])
def add_delivery():
    data = request.json  # JSON 데이터 받기
    dps = data.get('dps')

    if not dps:
        return jsonify({'error': 'dps (primary key) is required'}), 400

    # Redis 해시로 데이터 저장
    redis_client.hset(f"delivery:{dps}", mapping=data)
    return jsonify({'message': f'Delivery with dps {dps} added'}), 201


@app.route('/get_delivery/<int:dps>', methods=['GET'])
def get_delivery(dps):
    # Redis에서 데이터 조회
    delivery_data = redis_client.hgetall(f"delivery:{dps}")

    if not delivery_data:
        return jsonify({'error': f'Delivery with dps {dps} not found'}), 404

    return jsonify(delivery_data), 200


@app.route('/update_delivery/<int:dps>', methods=['PUT'])
def update_delivery(dps):
    # 업데이트할 데이터 받기
    update_data = request.json
    if not redis_client.exists(f"delivery:{dps}"):
        return jsonify({'error': f'Delivery with dps {dps} not found'}), 404

    # 데이터 업데이트
    redis_client.hset(f"delivery:{dps}", mapping=update_data)
    return jsonify({'message': f'Delivery with dps {dps} updated'}), 200


@app.route('/delete_delivery/<int:dps>', methods=['DELETE'])
def delete_delivery(dps):
    if not redis_client.exists(f"delivery:{dps}"):
        return jsonify({'error': f'Delivery with dps {dps} not found'}), 404

    # 데이터 삭제
    redis_client.delete(f"delivery:{dps}")
    return jsonify({'message': f'Delivery with dps {dps} deleted'}), 200


if __name__ == '__main__':
    app.run(debug=True)
