#main.py
import os
import subprocess
from dotenv import load_dotenv
from utils.ocr_openai import pdf_to_images, gpt4o_extract_answer_latex
import re # <--- NEW: Import regex for cleaning

# These global paths should match the ones in app.py
STUDENT_PDF_FOLDER = "uploads/students_data"
OUTPUT_FOLDER = "outputs"

os.makedirs(OUTPUT_FOLDER, exist_ok=True) # Ensure outputs directory exists

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


def extract_question_text(pdf_path: str):
    """
    Extracts text from the question paper PDF.
    Args:
        pdf_path (str): The full path to the question paper PDF.
    Returns:
        str: Extracted text from the question paper.
    """
    image_paths = pdf_to_images(pdf_path)
    # For question paper, we don't have existing question text to provide
    return gpt4o_extract_answer_latex(image_paths, question_text="")


def process_student_pdf(full_input_pdf_path: str, question_text: str, output_dir: str):
    """
    Processes a single student answer sheet PDF, extracts answers, and generates a LaTeX file and PDF.

    Args:
        full_input_pdf_path (str): The FULL path to the student PDF.
                                   E.g., "/Users/subhashmishra/PythonProject/uploads/students_data/MyFolder/student.pdf".
        question_text (str): The extracted text from the question paper.
        output_dir (str): The directory where the generated .tex and .pdf files will be saved.
                          (This should be the global 'outputs' folder).

    Returns:
        tuple[str | None, str]: A tuple containing:
            - The filename of the generated PDF (e.g., "G24AI1111_Aakanksha_SNA Major Exam_answers.pdf")
              or None if PDF compilation failed.
            - The raw LaTeX string extracted (after cleaning, for display/debugging).
    """

    # Extract just the base filename (e.g., "G24AI1126-G23AI1028PreetamSocialNAn.pdf")
    base_filename_only = os.path.basename(full_input_pdf_path)

    # Get the student name without extension (e.g., "G24AI1126-G23AI1028PreetamSocialNAn")
    student_name = os.path.splitext(base_filename_only)[0]

    print(f"\n🧑‍🎓 Processing: {student_name}")

    # 2. Convert PDF to images
    try:
        image_pages = pdf_to_images(full_input_pdf_path)
    except Exception as e:
        print(f"Error converting PDF to images for {full_input_pdf_path}: {e}")
        return None, f"Error converting PDF to images: {e}"


    # 3. Extract LaTeX from images using GPT-4o
    raw_latex_output = gpt4o_extract_answer_latex(image_pages, question_text)

    # --- START OF NEW/MODIFIED CODE FOR CLEANING LATEX OUTPUT ---
    # Remove markdown code fences from the GPT-4o output
    cleaned_latex_output = raw_latex_output.strip()
    if cleaned_latex_output.startswith("```latex"):
        cleaned_latex_output = cleaned_latex_output[len("```latex"):].strip()
    if cleaned_latex_output.endswith("```"):
        cleaned_latex_output = cleaned_latex_output[:-len("```")].strip()
    # Ensure no extra newlines or spaces at the very beginning/end after stripping fences
    cleaned_latex_output = cleaned_latex_output.strip()

    # Optional: Further cleaning for common LaTeX display issues if needed
    # For example, if GPT-4o outputs \begin{document} etc. within the main content,
    # you might want to remove them if you're wrapping it in a full document structure.
    # However, given your sample LaTeX, it seems GPT-4o is already producing a full document.
    # So, we just need to remove the markdown fences.
    # If GPT-4o is producing a full document including \documentclass, \begin{document} etc.
    # then you should NOT wrap it again with full_latex_document below.
    # Instead, just write cleaned_latex_output directly to the .tex file.

    # Let's assume GPT-4o provides a complete, compilable LaTeX document including preamble
    # based on your previous output. If it only provides the content, then the wrapping
    # logic below is necessary. The sample LaTeX you provided earlier *did* include
    # \documentclass, \usepackage, \begin{document} etc.
    # So, we should just write the cleaned_latex_output directly.
    # If it *sometimes* provides a full document and *sometimes* just content,
    # you'd need more sophisticated parsing or a more consistent prompt to GPT-4o.
    # For now, let's assume it provides a full document.

    final_latex_to_write = cleaned_latex_output
    # --- END OF NEW/MODIFIED CODE FOR CLEANING LATEX OUTPUT ---


    # 4. Prepare LaTeX file path
    tex_filename = f"{student_name}_answers.tex"
    tex_path = os.path.join(output_dir, tex_filename)

    os.makedirs(output_dir, exist_ok=True)

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(final_latex_to_write) # <--- Use the cleaned/final LaTeX here

    # 5. Compile LaTeX to PDF
    pdf_filename = f"{student_name}_answers.pdf"
    compile_command = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-output-directory", output_dir,
        tex_path
    ]

    try:
        result = subprocess.run(compile_command, cwd=output_dir, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            print(f"❌ LaTeX compile error for {student_name}:")
            print(result.stderr) # Print the actual LaTeX errors from pdflatex
            print(f"Warning: PDF compilation failed for {base_filename_only}. Extracted text still available.")
            return None, final_latex_to_write # Return None for pdf_filename on failure
        else:
            print(f"📄 PDF generated for {student_name}")

    except FileNotFoundError:
        print("❌ Error: pdflatex command not found. Please ensure LaTeX is installed and in your PATH.")
        return None, final_latex_to_write
    except Exception as e:
        print(f"❌ An unexpected error occurred during LaTeX compilation for {student_name}: {e}")
        return None, final_latex_to_write

    # 6. Clean up auxiliary files (keeping .tex for debugging)
    #for ext in [".aux", ".log"]: # Removed .tex from this list to keep it
        #try:
            #os.remove(os.path.join(output_dir, f"{student_name}_answers{ext}"))
        #except FileNotFoundError:
            #pass

    return pdf_filename, final_latex_to_write # Return the cleaned LaTeX for display/debugging