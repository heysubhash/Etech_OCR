# ocr_openai

import os
from dotenv import load_dotenv
from PIL import Image
from pdf2image import convert_from_path
import base64
import openai

def pdf_to_images(pdf_path):
    images = convert_from_path(pdf_path, dpi=300)
    image_paths = []
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    os.makedirs(f"tmp/{base_name}", exist_ok=True)
    for i, img in enumerate(images):
        img_path = f"tmp/{base_name}/page_{i + 1}.png"
        img.save(img_path, "PNG")
        image_paths.append(img_path)
    return image_paths

def encode_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def gpt4o_extract_answer_latex(image_paths, question_text):
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "You are a helpful assistant. A professor uploaded a question paper and a student's answer sheet.\n"
                        "Match each student's answer with the correct question number from the question paper.\n"
                        "The student may have written answers in a different order.\n"
                        "Write everything exactly as written in the answer sheet.\n"
                        "Do NOT correct math steps or reasoning. Preserve diagrams with descriptions if present.\n"
                        "Generate a full LaTeX document (start with \\documentclass and end with \\end{document}).\n"
                        "Include required packages.\n"
                        f"\nQUESTION PAPER:\n{question_text}\n"
                        "ANSWER SHEET IMAGES:"
                    )
                }
            ]
        }
    ]

    for path in image_paths:
        img_b64 = encode_image_base64(path)
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{img_b64}"
            }
        })

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.1
    )

    return response.choices[0].message.content

# Example usage:
if __name__ == "__main__":
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    question_text = open("uploads/question_data/question_paper.txt", "r", encoding="utf-8").read()
    student_pdf = "uploads/students_data/G24AI1006_Abhinav Kumar Ranjan_Social Network Analysis.pdf"

    image_pages = pdf_to_images(student_pdf)
    latex_output = gpt4o_extract_answer_latex(image_pages, question_text)

    out_tex_path = f"outputs/{os.path.basename(student_pdf).replace('.pdf', '_answers.tex')}"
    with open(out_tex_path, "w", encoding="utf-8") as f:
        f.write(latex_output)

    print(f"✅ Saved LaTeX to {out_tex_path}")
