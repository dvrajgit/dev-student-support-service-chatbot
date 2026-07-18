from flask import Flask, request, jsonify, session
from student_support_chatbot import StudentSupportChatbot
import os

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-student-support-secret')

chatbot = StudentSupportChatbot()


def valid_login(username, password):
    expected_username = os.environ.get('CHATBOT_USERNAME', 'student')
    expected_password = os.environ.get('CHATBOT_PASSWORD', 'student123')
    return username == expected_username and password == expected_password


@app.route('/api/session', methods=['GET'])
def session_status():
    return jsonify({'logged_in': bool(session.get('logged_in'))})


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if valid_login(username, password):
        session['logged_in'] = True
        session['username'] = username
        return jsonify({'message': 'Login successful.'})

    return jsonify({'message': 'Invalid username or password.'}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out.'})


@app.route('/api/chat', methods=['POST'])
def chat():
    if not session.get('logged_in'):
        return jsonify({'reply': 'Please log in before using the chatbot.'}), 401

    data = request.get_json(silent=True) or {}
    message = data.get('message', '')
    mode = data.get('mode', 'general')
    
    # Extract API key if sent in custom header or JSON body.
    api_key = request.headers.get('X-Groq-API-Key') or data.get('api_key')

    if not message or not message.strip():
        return jsonify({'reply': "Please provide a question or request so I can help."}), 400

    try:
        reply = chatbot.respond(message, api_key=api_key, mode=mode)
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': 'An error occurred while processing your request.'}), 500


@app.route('/')
def root():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
