from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# In-memory to-do list
todos = []

# Rule-based chatbot responses
def chatbot_response(message):
    msg = message.lower()
    if 'hello' in msg or 'hi' in msg:
        return "Hello! How can I help you with your to-do list?"
    elif 'add' in msg:
        return "To add a to-do, type: add <your task>"
    elif 'list' in msg:
        return f"Your to-dos: {', '.join(todos) if todos else 'No tasks yet.'}"
    elif 'remove' in msg:
        return "To remove a to-do, type: remove <task>"
    elif 'bye' in msg or 'exit' in msg:
        return "Goodbye!"
    else:
        return "I'm your to-do assistant! You can ask me to add, list, or remove tasks."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/todos', methods=['GET', 'POST', 'DELETE'])
def manage_todos():
    if request.method == 'GET':
        return jsonify({'todos': todos})
    elif request.method == 'POST':
        data = request.json
        task = data.get('task')
        if task:
            todos.append(task)
            return jsonify({'message': 'Task added!', 'todos': todos})
        return jsonify({'error': 'No task provided.'}), 400
    elif request.method == 'DELETE':
        data = request.json
        task = data.get('task')
        if task in todos:
            todos.remove(task)
            return jsonify({'message': 'Task removed!', 'todos': todos})
        return jsonify({'error': 'Task not found.'}), 404

@app.route('/api/chatbot', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    response = chatbot_response(message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True) 