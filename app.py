import os
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_pymongo import PyMongo
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename


app = Flask(__name__)


@app.errorhandler(RequestEntityTooLarge)
def handle_file_size_error(e):
    return jsonify({"error": "File is too large. Max size is 16MB."}), 413

@app.errorhandler(Exception)
def handle_general_error(e):
    return jsonify({"error": str(e)}), 500


app.config["MONGO_URI"] = "mongodb+srv://poornachandra14046_db_user:poorna123@cluster0.yajczea.mongodb.net/studenthubdb?retryWrites=true&w=majority&appName=Cluster0"  # Replace with your MongoDB connection string
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size


mongo = PyMongo(app)
notes_collection = mongo.db.notes

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'zip', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
   
    return render_template('studenthub.html')

@app.route('/upload', methods=['POST'])
def upload():
        title = request.form.get('title')
        subject = request.form.get('subject')
        semester = request.form.get('semester')
        tags = request.form.get('tags', '').split(',')
    
        file = request.files.get('file')
        if not file or file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400
    
        filename = secure_filename(file.filename)
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
    
        filesize = f"{os.path.getsize(filepath) / (1024*1024):.1f} MB"
    
        note = {
            "title": title,
            "subject": subject,
            "semester": semester,
            "tags": [tag.strip() for tag in tags if tag.strip()],
            "fileName": filename,
            "fileSize": filesize
        }
        notes_collection.insert_one(note)
    
        return jsonify({"message": "Upload successful"}), 201
    

@app.route('/notes', methods=['GET'])
def notes():
    notes_cursor = notes_collection.find().sort('_id', -1)
    notes = []
    for n in notes_cursor:
        n['_id'] = str(n['_id'])
        notes.append(n)
    return jsonify(notes)

@app.route('/uploads/<filename>')
def download(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)
