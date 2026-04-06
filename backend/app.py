from flask import Flask, jsonify
from flask_cors import CORS
import os
from routes.auth import auth_bp
from routes.student import student_bp
from routes.warden import warden_bp
from routes.admin import admin_bp
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Enable CORS for frontend integration
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(student_bp, url_prefix='/api/student')
app.register_blueprint(warden_bp, url_prefix='/api/warden')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

@app.route('/')
def index():
    return jsonify({'message': 'Welcome to HLEEMS API'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
