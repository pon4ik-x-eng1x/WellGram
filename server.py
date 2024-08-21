from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}
rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = json.loads(request.data)
    username = data.get('username')
    if username in users:
        return jsonify({'success': False, 'message': 'Username already taken'})
    users[username] = None
    return jsonify({'success': True})

@socketio.on('message')
def handle_message(data):
    room = data['room']
    message = data['message']
    username = data['username']
    emit('message', {'username': username, 'message': message}, room=room)

@socketio.on('join')
def on_join(data):
    room = data['room']
    username = data['username']
    join_room(room)
    emit('status', {'username': username, 'action': 'joined', 'room': room}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    username = data['username']
    leave_room(room)
    emit('status', {'username': username, 'action': 'left', 'room': room}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
