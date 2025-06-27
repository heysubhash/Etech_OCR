#answer_structuring_chain
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap
import os

def get_answer_structuring_chain(model_name="gpt-4o"):
    llm = ChatOpenAI(
        model=model_name,
        temperature=0.1,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    prompt = ChatPromptTemplate.from_template(r"""
    You are a helpful assistant. A professor uploaded a question paper and a student's answer sheet.

    1. Match each student's answer with the correct question number.
    2. The student may have written answers in a different order.
    3. Write each and everything written by the student in the answer sheet, Strictly do not skip anything from the answer sheet.
    4. If answer contains some points or arrows in it, then extract and represent them nicely in the result.
    5. For numerical problem solution in the answer sheet, extract exact solution from the answer sheet, do not try to reason and correct it and solve by your own.
    6. Also include required packages for math expressions.
    7. Generate a complete LaTeX document which includes:
       - \documentclass, \title, \section* for each question.
       - Answer under each question.
       - Use proper LaTeX formatting.

    Start the output from \documentclass and end with \end{{document}}. Do not explain or wrap with code block.

    QUESTION PAPER:
    {question_paper}

    ANSWER SHEET:
    {student_answers}
    """)

    # ✅ Wrap into a Runnable chain explicitly
    chain = prompt | llm
    return chain
