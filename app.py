from flask import Flask, request, jsonify
from student_support_chatbot import StudentSupportChatbot
import os

app = Flask(__name__, static_folder='.', static_url_path='')

chatbot = StudentSupportChatbot()


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get('message', '')
    if not message or not message.strip():
        return jsonify({'reply': "Please provide a question or request so I can help."}), 400

    try:
        reply = chatbot.respond(message)
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': 'An error occurred while processing your request.'}), 500


@app.route('/')
def root():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
