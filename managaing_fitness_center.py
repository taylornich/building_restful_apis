from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
ma = Marshmallow(app)

def connect_db():
    try: 
        conn = mysql.connector.connect(
            database="gym_management_assignment",
            user="root",
            password="",
            host="localhost"
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error: {e}")
        return None

class Member(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email')

member_schema = Member()
members_schema = Member(many=True)

class WorkoutSession(ma.Schema):
    class Meta:
        fields = ('id', 'member_id', 'session_date', 'duration')

workout_session_schema = WorkoutSession()
workout_sessions_schema = WorkoutSession(many=True)


#question 1 task 2

@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    name, email = data.get('name'), data.get('email')
    if not name or not email:
        return handle_error("Name and email are required", 400)
    
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO Members (name, email) VALUES (%s, %s)", (name, email))
        conn.commit()
        new_member = {'id': cursor.lastrowid, 'name': name, 'email': email}
        return member_schema.jsonify(new_member), 201
    except Error as e:
        print(f"Error: {e}")
        return handle_error("Database error occurred", 500)
    finally:
        cursor.close()
        conn.close()

@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM Members WHERE id = %s", (id,))
        member = cursor.fetchone()
        if not member:
            return handle_error("Member not found", 404)
        return jsonify(member)
    except Error as e:
        print(f"Error: {e}")
        return handle_error("Database error occurred", 500)
    finally:
        cursor.close()
        conn.close()

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    data = request.get_json()
    name, email = data.get('name'), data.get('email')
    if not name and not email:
        return handle_error("Name or email is required", 400)
    
    conn = connect_db()
    cursor = conn.cursor()

    try:
        fields = []
        params = []
        if name:
            fields.append("name = %s")
            params.append(name)
        if email:
            fields.append("email = %s")
            params.append(email)
        
        params.append(id)
        query = f"UPDATE Members SET {', '.join(fields)} WHERE id = %s"
        cursor.execute(query, tuple(params))
        conn.commit()

        if cursor.rowcount == 0:
            return handle_error("Member not found", 404)
        
        return jsonify({"message": "Member updated successfully"})
    except Error as e:
        print(f"Error: {e}")
        return handle_error("Database error occurred", 500)
    finally:
        cursor.close()
        conn.close()

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM Members WHERE id = %s", (id,))
        conn.commit()

        if cursor.rowcount == 0:
            return handle_error("Member not found", 404)
        
        return jsonify({"message": "Member deleted successfully"})
    except Error as e:
        print(f"Error: {e}")
        return handle_error("Database error occurred", 500)
    finally:
        cursor.close()
        conn.close()

#question 1 task 3

@app.route('/workout_sessions', methods=['POST'])
def schedule_workout_session():
    data = request.get_json()
    member_id, session_date, duration = data.get("member_id"), data.get("session_date"), data.get("duration")
    if not member_id or not session_date or not duration:
        return handle_error("Member ID, session date, and duration are required", 400)
    
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO WorkoutSessions (member_id, session_date, duration) VALUES (%s, %s, %s)",
                       (member_id, session_date, duration))
        conn.commit()
        new_session = {'id': cursor.lastrowid, 'member_id': member_id, 'session_date': session_date, 'duration': duration}
        return workout_session_schema.jsonify(new_session), 201
    except Error as e:
        print(f"Error: {e}")
        return handle_error("Database error occurred", 500)
    finally:
        cursor.close()
        conn.close()

@app.route('/workout_sessions/<int:id>', methods=['GET'])
def get_workout_session(id):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM WorkoutSessions WHERE id = %s", (id,))
        session = cursor.fetchone()
        if not session:
            return handle_error("Session not found", 404)
        return jsonify(session)
    except Error as e:
        print(f"Error: {e}")
        return handle_error("Database error occurred", 500)
    finally:
        cursor.close()
        conn.close()

@app.route('/workout_sessions/<int:id>', methods=['PUT'])
def update_workout_session(id):
    data = request.get_json()
    session_date, duration = data.get('session_date'), data.get('duration')

    if not session_date and not duration:
        return handle_error("Session date or duration is required", 400)
    
    conn = connect_db()
    cursor = conn.cursor()

    try: 
        fields = []
        params = []

        if session_date:
            fields.append("session_date = %s")
            params.append(session_date)
        if duration:
            fields.append("duration = %s")
            params.append(duration)

        params.append(id)
        query = f"UPDATE WorkoutSessions SET {', '.join(fields)} WHERE id = %s"
        cursor.execute(query, tuple(params))
        conn.commit()

        if cursor.rowcount == 0:
            return handle_error("Session not found", 404)
        
        return jsonify({"message": "Workout session updated successfully"})
    except Error as e:
        print(f"Error: {e}")
        return handle_error("Database error occurred", 500)
    finally: 
        cursor.close()
        conn.close()

@app.route('/workout_sessions/<int:id>', methods=['DELETE'])
def delete_workout_session(id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM WorkoutSessions WHERE id = %s", (id,))
        conn.commit()

        if cursor.rowcount == 0:
            return handle_error("Session not found", 404)
        
        return jsonify({"message": "Workout session deleted successfully"})
    except Error as e:
        print(f"Error: {e}")
        return handle_error("Database error occurred", 500)
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
