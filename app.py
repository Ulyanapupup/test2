from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit
import re
import string
import json
import os
import eventlet
eventlet.monkey_patch()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

secret_number = 17

def is_greater(x): return secret_number > x
def is_less(x): return secret_number < x
def is_equal(x): return secret_number == x
def is_prime(_=None):
    if secret_number < 2: return False
    for i in range(2, int(secret_number ** 0.5) + 1):
        if secret_number % i == 0: return False
    return True

question_functions = {
    "is_greater": is_greater,
    "is_less": is_less,
    "is_equal": is_equal,
    "is_prime": is_prime
}

with open('questions.json', 'r', encoding='utf-8') as f:
    question_map = json.load(f)

def process_question(q):
    q = q.lower()
    q = q.translate(str.maketrans('', '', string.punctuation))
    for keyword, func_name in question_map.items():
        if keyword in q:
            func = question_functions[func_name]
            if func_name == "is_prime":
                return "Да" if func() else "Нет"
            else:
                nums = re.findall(r'\d+', q)
                if not nums:
                    return "Пожалуйста, укажите число в вопросе"
                x = int(nums[0])
                return "Да" if func(x) else "Нет"
    return "Неизвестный вопрос"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get("question", "")
    answer = process_question(question)
    return jsonify({"answer": answer})

@socketio.on('message')
def handle_message(msg):
    print("Сообщение от клиента:", msg)
    send(msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)