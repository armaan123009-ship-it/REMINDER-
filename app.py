from flask import Flask, render_template, request, redirect, session, url_for
from bson.objectid import ObjectId
import pymongo

app = Flask(__name__)
app.secret_key = "student_reminder_key_3d"

# MongoDB Connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["student_app"]
users_col = db["users"]
assign_col = db["assignments"]

# --- HOME ROUTE ---
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# --- REGISTER ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_data = {
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "password": request.form.get('password')
        }
        users_col.insert_one(user_data)
        return redirect(url_for('login'))
    return render_template('register.html')

# --- LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = users_col.find_one({"email": email, "password": password})
        
        if user:
            session['user'] = user['name']
            session['email'] = user['email']  # YE ZAROORI HAI: Email ko session mein save karna
            return redirect(url_for('dashboard'))
        else:
            return "Galat Details! <a href='/login'>Wapas jayein</a>"
    return render_template('login.html')

# --- DASHBOARD (Reminder App) ---
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_email = session.get('email')
    # MongoDB se sirf is user ke assignments lana
    user_assignments = list(assign_col.find({"user_email": user_email}))
    
    # Performance Evaluation Logic
    total = len(user_assignments)
    completed = len([a for a in user_assignments if a['status'] == 'Completed'])
    performance = (completed / total * 100) if total > 0 else 0
    
    return render_template('dashboard.html', 
                           name=session['user'], 
                           assignments=user_assignments, 
                           perf=round(performance, 2))

# --- ADD ASSIGNMENT ---
@app.route('/add_assignment', methods=['POST'])
def add_assignment():
    if 'user' in session:
        data = {
            "title": request.form.get('title'),
            "deadline": request.form.get('deadline'),
            "status": "Pending",
            "user_email": session.get('email')
        }
        assign_col.insert_one(data)
    return redirect(url_for('dashboard'))

# --- UPDATE STATUS ---
@app.route('/update_status/<id>/<status>')
def update_status(id, status):
    if 'user' in session:
        assign_col.update_one({"_id": ObjectId(id)}, {"$set": {"status": status}})
    return redirect(url_for('dashboard'))

# --- LOGOUT ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- YE HAI RUN COMMAND (Iske bina terminal khali rehta hai) ---
if __name__ == '__main__':
    print("Bhai, Server Start Ho Raha Hai... http://127.0.0.1:5000 kholo")
    app.run(debug=True)