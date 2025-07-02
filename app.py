#app.py
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
import os
import shutil
from main import extract_question_text, process_student_pdf  # Make sure main is correctly imported

UPLOAD_FOLDER = "uploads"
QUESTION_FOLDER = os.path.join(UPLOAD_FOLDER, "question_data")
STUDENT_FOLDER = os.path.join(UPLOAD_FOLDER, "students_data")
OUTPUT_FOLDER = "outputs"

os.makedirs(QUESTION_FOLDER, exist_ok=True)
os.makedirs(STUDENT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs("tmp", exist_ok=True)  # Ensure the tmp directory used by ocr_openai.py exists

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

question_text = None  # OCRed question paper text


@app.route("/download/<filename>")
def download(filename):
    # This route serves files for download (generated PDFs from OUTPUT_FOLDER)
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)


@app.route('/preview/<path:filename>')  # Use <path:filename> to handle subdirectories
def preview_pdf(filename):
    # This route serves files for iframe preview
    # Check if the filename belongs to a generated PDF (ends with _answers.pdf)
    if filename.endswith("_answers.pdf"):
        return send_from_directory(OUTPUT_FOLDER, filename)
    else:
        # Otherwise, assume it's an original student PDF.
        # The filename here should be the path relative to STUDENT_FOLDER
        return send_from_directory(STUDENT_FOLDER, filename)


@app.route("/", methods=["GET", "POST"])
def index():
    global question_text

    if request.method == "POST":
        last_processed_pdf_filename = None  # Filename of the generated PDF (e.g., 'G24AI1006_Abhinav Kumar Ranjan_Social Network Analysis (Code CSL 7390)_Major Exam April 2025_answers.pdf')
        last_processed_extracted_text = None
        original_student_relative_path_for_preview = None  # Store path relative to STUDENT_FOLDER for preview (e.g., 'MyFolder/student.pdf')

        # Handle question paper upload
        if "question_paper" in request.files:
            q_file = request.files["question_paper"]
            # Clear old question papers
            for f in os.listdir(QUESTION_FOLDER):
                file_path = os.path.join(QUESTION_FOLDER, f)
                if os.path.isfile(file_path) and file_path.lower().endswith('.pdf'):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error removing old question file {file_path}: {e}")
            q_path = os.path.join(QUESTION_FOLDER, q_file.filename)
            q_file.save(q_path)
            question_text = extract_question_text(q_path)
            if not question_text:
                return jsonify({"error": "Failed to extract text from question paper."}), 500

        # Handle student PDFs upload
        if "student_pdfs" in request.files and question_text:
            student_files = request.files.getlist("student_pdfs")
            if not student_files:
                return jsonify({"error": "No student PDFs provided."}), 400

            # Clear *only PDF files* from the student data folder (and their subdirectories)
            for root, dirs, files in os.walk(STUDENT_FOLDER, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    if file_path.lower().endswith('.pdf'):
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            print(f"Error removing old student file {file_path}: {e}")
                for name in dirs:
                    dir_path = os.path.join(root, name)
                    if not os.listdir(dir_path):  # Only remove empty directories
                        try:
                            os.rmdir(dir_path)
                        except Exception as e:
                            print(f"Error removing empty directory {dir_path}: {e}")

            for s_file in student_files:
                # s_file.filename will contain the relative path from the folder chosen by webkitdirectory
                # e.g., 'MyAnswers/student1.pdf' or just 'student2.pdf' if files were selected directly

                # Construct the full path where the file will be saved
                full_save_path = os.path.join(STUDENT_FOLDER, s_file.filename)

                # Ensure the directory structure exists before saving
                os.makedirs(os.path.dirname(full_save_path), exist_ok=True)

                s_file.save(full_save_path)

                # Store the path relative to STUDENT_FOLDER for the frontend preview
                original_student_relative_path_for_preview = s_file.filename

                pdf_filename, extracted_latex = process_student_pdf(
                    # **** THIS IS THE LINE TO CHANGE ****
                    full_save_path,  # Pass the relative path as the first positional argument
                    question_text=question_text,
                    output_dir=OUTPUT_FOLDER
                )

                if pdf_filename:
                    last_processed_pdf_filename = pdf_filename
                    last_processed_extracted_text = extracted_latex
                else:
                    print(f"Warning: PDF compilation failed for {s_file.filename}. Extracted text still available.")
                    last_processed_extracted_text = extracted_latex  # Keep the extracted text even if PDF fails

                # IMPORTANT: We are processing one PDF at a time in the loop.
                # The frontend's current design assumes one result per POST.
                # If you upload multiple student PDFs, only the LAST one processed
                # will have its data sent back. You might need to change the frontend
                # to handle multiple results if that's the desired behavior.
                break  # <-- Keeping this `break` as per your existing code structure
                # This means only the first student PDF in the list will be processed fully.
                # Remove this 'break' if you intend to process all and return a list of results.

            if last_processed_pdf_filename or last_processed_extracted_text:
                return jsonify({
                    "pdf_filename": last_processed_pdf_filename,
                    "extracted_text": last_processed_extracted_text,
                    "original_student_pdf": original_student_relative_path_for_preview  # Send the relative path
                })
            else:
                return jsonify({"error": "No valid output generated. Please check files and try again."}), 500
        elif not question_text:
            return jsonify({"error": "Please upload the question paper first."}), 400

        return jsonify({"message": "No files processed or no output generated."}), 200

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)