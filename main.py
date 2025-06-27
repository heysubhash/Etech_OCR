# main.py
import os
import subprocess
from dotenv import load_dotenv
from utils.ocr_openai import pdf_to_images, gpt4o_extract_answer_latex

STUDENT_PDF_FOLDER = "uploads/students_data"
OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def extract_question_text(pdf_path: str):
    image_paths = pdf_to_images(pdf_path)
    return gpt4o_extract_answer_latex(image_paths, question_text="")  # For question paper

def process_student_pdf(filename: str, question_text: str, output_folder: str):
    student_name = os.path.splitext(filename)[0]
    print(f"\n🧑‍🎓 Processing: {student_name}")

    local_path = os.path.join("uploads/students_data", filename)
    image_pages = pdf_to_images(local_path)

    latex_output = gpt4o_extract_answer_latex(image_pages, question_text)

    tex_path = os.path.join(output_folder, f"{student_name}_answers.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_output)

    compile_command = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-output-directory", output_folder,
        tex_path
    ]

    try:
        subprocess.run(compile_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"📄 PDF generated for {student_name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ LaTeX compile error: {e.stderr.decode()}")

    for ext in [".aux", ".log", ".tex"]:
        try:
            os.remove(os.path.join(output_folder, f"{student_name}_answers{ext}"))
        except FileNotFoundError:
            pass

    return f"{student_name}_answers.pdf"
