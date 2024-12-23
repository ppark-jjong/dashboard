from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from datetime import datetime
import os

app = Flask(__name__)



# API Routes
@app.route('/health')
def health_check():
    return {'status': 'healthy'}

@app.route('/test/db')
def test_db():
    try:
        db.session.execute('SELECT 1')
        return {'status': 'MySQL connected'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
