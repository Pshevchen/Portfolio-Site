# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import jsonify, render_template, redirect, request, session, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from .utils.database.database  import database
from werkzeug.datastructures   import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
from . import socketio
db = database()


#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

def getUser():
	return session['email'] if 'email' in session else 'Unknown'

@app.route('/signup')
def signup():
     return render_template('signup.html')

@app.route('/createaccount', methods = ["POST","GET"])
def createaccount():
    email = request.form.get('email')
    password = request.form.get('password')

    db.createUser(email,password)
    return redirect('/login')
         

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/logout')
def logout():
	session.pop('email', default=None)
	return redirect('/home')

@app.route('/processlogin', methods = ["POST","GET"])
def processlogin():
	
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
	
    session['email'] = form_fields['email']
    session['password'] = form_fields['password']

    # Assuming db is your database instance
    status = db.authenticate(session['email'], session['password'])

    if status['success']:
        session['email'] = db.reversibleEncrypt('encrypt', session['email'])

    return json.dumps(status)


#######################################################################################
# BOARD RELATED
#######################################################################################
@app.route('/createboard', methods=['POST'])
def create_board():
    if request.method == 'POST':
        feedback_data = request.form
        project_name = feedback_data.get('name')
        boardusers = feedback_data.get('users_invited').split(',')
        try:
            db.create_board(project_name, boardusers)
        except Exception as e:
            app.logger.error(f"Failed to create board: {e}")
            return jsonify({'success': False, 'message': str(e)}), 500
    
        return jsonify({'success': True, 'boardName': project_name})


@app.route('/board-home')
def boardhome():
     return render_template('board-home.html')


@app.route('/boards')
def boards():


    try:
        user_email = db.reversibleEncrypt('decrypt',session.get('email'))
        boards = db.get_user_boards(user_email)
        board_names = []
        board_ids = []
        for board in boards:
            # Assuming each board dictionary has a 'name' key
            board_names.append(board['name'])
            board_ids.append(board['board_id'])

        return render_template('boards.html', boards_ids=zip(boards,board_ids))
    except TypeError:
        return redirect('/login')

@app.route('/board/<int:board_id>')
def board(board_id):
    columns = db.get_columns_by_board(board_id)  # Assuming a function to fetch columns
    board_name = db.query('SELECT name FROM boards WHERE board_id=%s',[board_id])[0]['name']
    for column in columns:
        column['cards'] = db.get_cards_by_column([column['column_id']])
    return render_template('board.html', columns=columns, board_name=board_name, board_id=board_id)

@app.route('/add_card', methods=['POST'])
def add_card():
    data = request.get_json()
    column_id = data.get('column_id')
    card_content = data.get('card_content')
    if not column_id or not card_content:
        return jsonify({'success': False, 'message': 'Missing data'}), 400

    card_id = db.insert_card(column_id, card_content)  # Make sure this returns the new card's ID
    return jsonify({'success': True, 'card_id': card_id}), 200

@app.route('/add_column', methods=['POST'])
def add_column():
    data = request.get_json()
    name = data.get('name')
    board_id = data.get('board_id')

    if not name:
        return jsonify({'success': False, 'message': 'Column name is required'}), 400

    try:
        column_id = db.insert_column(board_id,name)  # Implement this function in your database handling class
        return jsonify({'success': True, 'column_id': column_id}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
@app.route('/update_card_position', methods=['POST'])
def update_card_position():
    if not request.is_json:
        return jsonify({'success': False, 'message': 'Missing JSON in request'}), 400

    data = request.get_json()
    card_id = data.get('card_id')
    new_column_id = data.get('new_column_id')

    if not card_id or not new_column_id:
        return jsonify({'success': False, 'message': 'Missing card_id or new_column_id'}), 400

    # Assuming a method in your database class that handles the update
    result = db.update_card_position(card_id, new_column_id)
    if result:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'message': 'Failed to update card position'}), 500
        





#######################################################################################
# CHATROOM RELATED
#######################################################################################
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=getUser())

@socketio.on('joined', namespace='/chat')
def joined(message):
    join_room('main')
    if db.reversibleEncrypt('decrypt', getUser()) == 'owner@email.com':
        emit('status', {'msg': db.reversibleEncrypt('decrypt', getUser()) + ' has entered the room.', 'style': 'width: 100%;color:blue;text-align: right'}, room='main')
    else:
       emit('status', {'msg': db.reversibleEncrypt('decrypt', getUser()) + ' has entered the room.', 'style': 'width: 100%;color:gray;text-align: left'}, room='main')

@socketio.on('left', namespace='/chat')
def joined(message):
    leave_room('main')
    if db.reversibleEncrypt('decrypt', getUser()) == 'owner@email.com':
        emit('status', {'msg': db.reversibleEncrypt('decrypt', getUser()) + ' has left the room.', 'style': 'width: 100%;color:blue;text-align: right'}, room='main')
    else:
       emit('status', {'msg': db.reversibleEncrypt('decrypt', getUser()) + ' has left the room.', 'style': 'width: 100%;color:gray;text-align: left'}, room='main')


@socketio.on('new_message', namespace='/chat')
def handle_new_message(data):
    # Decrypt the user email from the session
    user_email = db.reversibleEncrypt('decrypt', getUser())
    # Check if the user is the owner
    if user_email == 'owner@email.com':
        # Emit a message for the owner with blue text aligned to the right
        emit('new_message', {
            'msg': user_email + ': ' + data['message'],
            'style': 'color:blue; text-align:right;'
        }, broadcast=True, namespace='/chat')
    else:
        # Emit a message for other users with black text aligned to the left
        emit('new_message', {
            'msg': user_email + ': ' + data['message'],
            'style': 'color:gray; text-align:left;'
        }, broadcast=True, namespace='/chat')
	


#######################################################################################
# OTHER
#######################################################################################
# Default app route
@app.route('/')
def root():
	return redirect('/home')

# App route for homepage
@app.route('/home')
def home(): 
	return render_template('home.html')

# App route for projects
@app.route('/projects')
def projects():
	return render_template('projects.html')

# App route for resume
@app.route('/resume')
def resume():	
	# Get the resume data
	resume_data = db.getResumeData()
	return render_template('resume.html', resume_data = resume_data)

@app.route('/piano')
def piano():	
	return render_template('piano.html')

@app.route('/processfeedback', methods=['POST'])
def processfeedback():
	if request.method == 'POST':
		feedback_data = request.form
		name = feedback_data.get('name')
		email = feedback_data.get('email')
		comment = feedback_data.get('comment')
		db.insertRows('feedback',['comment_id','name','email','comment'],[['',name,email,comment]])
		return render_template('feedback.html')
			