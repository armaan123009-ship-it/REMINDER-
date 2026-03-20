from flask import Flask, render_template, request
import pymongo

app = Flask(__name__)

# MongoDB Connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mera_database"]
collection = db["users"]

@app.route('/')
def index():
    return render_template('index.html') # HTML file load hogi

@app.route('/submit', methods=['POST'])
def submit():
    naam = request.form.get('naam')
    # MongoDB mein save karna
    collection.insert_one({"naam": naam})
    return f"Bhai, {naam} ka data MongoDB mein save ho gaya!"

if __name__ == '__main__':
    app.run(debug=True)