from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model for to-do items
class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'task': self.task,
            'completed': self.completed,
            'due_date': self.due_date.isoformat() if self.due_date else None
        }

# Rule-based chatbot responses
def chatbot_response(message):
    msg = message.lower()
    if 'hello' in msg or 'hi' in msg:
        return "Hello! How can I help you with your to-do list?"
    elif 'add' in msg:
        return "To add a to-do, type: add <your task>"
    elif 'list' in msg:
        todos = ToDo.query.all()
        return f"Your to-dos: {', '.join([t.task for t in todos]) if todos else 'No tasks yet.'}"
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
        todos = ToDo.query.all()
        return jsonify({'todos': [t.to_dict() for t in todos]})
    elif request.method == 'POST':
        data = request.json
        task = data.get('task')
        due_date_str = data.get('due_date')
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.fromisoformat(due_date_str)
            except Exception:
                return jsonify({'error': 'Invalid due date format.'}), 400
        if task:
            new_todo = ToDo(task=task, due_date=due_date)
            db.session.add(new_todo)
            db.session.commit()
            todos = ToDo.query.all()
            return jsonify({'message': 'Task added!', 'todos': [t.to_dict() for t in todos]})
        return jsonify({'error': 'No task provided.'}), 400
    elif request.method == 'DELETE':
        data = request.json
        task = data.get('task')
        todo = ToDo.query.filter_by(task=task).first()
        if todo:
            db.session.delete(todo)
            db.session.commit()
            todos = ToDo.query.all()
            return jsonify({'message': 'Task removed!', 'todos': [t.to_dict() for t in todos]})
        return jsonify({'error': 'Task not found.'}), 404

@app.route('/api/todos/complete', methods=['POST'])
def complete_todo():
    data = request.json
    todo_id = data.get('id')
    completed = data.get('completed')
    todo = ToDo.query.get(todo_id)
    if todo is not None:
        todo.completed = completed
        db.session.commit()
        return jsonify({'message': 'Task updated!', 'todo': todo.to_dict()})
    return jsonify({'error': 'Task not found.'}), 404

@app.route('/api/todos/edit', methods=['POST'])
def edit_todo():
    data = request.json
    todo_id = data.get('id')
    new_task = data.get('task')
    new_due_date_str = data.get('due_date')
    todo = ToDo.query.get(todo_id)
    if todo is not None:
        if new_task:
            todo.task = new_task
        if new_due_date_str is not None:
            if new_due_date_str == '':
                todo.due_date = None
            else:
                try:
                    todo.due_date = datetime.fromisoformat(new_due_date_str)
                except Exception:
                    return jsonify({'error': 'Invalid due date format.'}), 400
        db.session.commit()
        return jsonify({'message': 'Task updated!', 'todo': todo.to_dict()})
    return jsonify({'error': 'Task not found or invalid data.'}), 404

@app.route('/api/chatbot', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    response = chatbot_response(message)
    return jsonify({'response': response})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 