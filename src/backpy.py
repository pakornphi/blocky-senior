import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit  # Import SocketIO
from bs4 import BeautifulSoup
from csrf2 import CSRFTester

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize SocketIO
socketio = SocketIO(app)

@app.route('/api/test-csrf', methods=['POST'])
def test_csrf():
    data = request.get_json()
    target_url = data.get('url')

    if not target_url:
        return jsonify({'error': 'URL is required'}), 400

    # Create an instance of CSRFTester with the target URL
    tester = CSRFTester(target_url)

    # Perform CSRF tests
    test_results = tester.perform_test()

    return jsonify({'results': test_results}), 200

@app.route('/api/check-key', methods=['POST'])
def check_key():
    data = request.get_json()
    target_url = data.get('url')
    key = data.get('key')

    if not target_url or not key:
        return jsonify({'error': 'URL and key are required'}), 400

    try:
        response = requests.get(target_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the meta tag with the owner-key
        meta_tag = soup.find('meta', {'name': 'owner-key'})
        
        if meta_tag and meta_tag.get('content') == key:
            return jsonify({'key_match': True, 'message': 'Key matched in head tag.'})
        else:
            return jsonify({'key_match': False, 'message': 'Key not found or mismatch.'})

    except Exception as e:
        return jsonify({'error': f'Error while fetching the page: {str(e)}'}), 500

# WebSocket route to handle messages
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('message', {'data': 'Connected to WebSocket server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(data):
    print(f"Received message: {data['data']}")
    emit('message', {'data': 'Message received!'})

if __name__ == '__main__':
    socketio.run(app, debug=True)
