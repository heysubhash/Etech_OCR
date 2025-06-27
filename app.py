# app.py
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
from main import extract_question_text, process_student_pdf

UPLOAD_FOLDER = "uploads"
QUESTION_FOLDER = os.path.join(UPLOAD_FOLDER, "question_data")
STUDENT_FOLDER = os.path.join(UPLOAD_FOLDER, "students_data")
OUTPUT_FOLDER = "outputs"

os.makedirs(QUESTION_FOLDER, exist_ok=True)
os.makedirs(STUDENT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

question_text = None  # OCRed question paper text

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory("outputs", filename, as_attachment=True)
@app.route('/preview/<filename>')
def preview_pdf(filename):
    return render_template('preview.html', filename=filename)
@app.route("/", methods=["GET", "POST"])
def index():
    global question_text
    generated_pdfs = []

    if request.method == "POST":
        if "question_paper" in request.files:
            q_file = request.files["question_paper"]
            q_path = os.path.join(QUESTION_FOLDER, q_file.filename)
            q_file.save(q_path)
            question_text = extract_question_text(q_path)

        if "student_pdfs" in request.files:
            student_files = request.files.getlist("student_pdfs")
            for s_file in student_files:
                s_path = os.path.join(STUDENT_FOLDER, s_file.filename)
                s_file.save(s_path)
                pdf_filename = process_student_pdf(s_file.filename, question_text, OUTPUT_FOLDER)
                generated_pdfs.append(pdf_filename)

        return render_template("index.html", generated_pdfs=os.listdir(OUTPUT_FOLDER))

    return render_template("index.html", generated_pdfs=os.listdir(OUTPUT_FOLDER))

if __name__ == "__main__":
    app.run(debug=True)
