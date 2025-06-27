#formatter
import json
import re
from typing import List, Dict

def parse_flexible_gpt_output(text: str) -> List[Dict]:
    try:
        match = re.search(r"```json(.*?)```", text, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
            parsed = json.loads(json_str)
            return _normalize_to_list(parsed)
    except Exception as e:
        print("❌ Failed JSON from markdown block:", e)

    try:
        parsed = json.loads(text)
        return _normalize_to_list(parsed)
    except Exception as e:
        print("❌ Failed raw JSON parsing:", e)

    return parse_markdown_style(text)

def _normalize_to_list(parsed_obj) -> List[Dict]:
    if isinstance(parsed_obj, list):
        return parsed_obj

    if isinstance(parsed_obj, dict):
        result = []
        for qno, val in parsed_obj.items():
            if isinstance(val, dict):
                result.append({
                    "question_number": str(qno),
                    "subparts": val
                })
            else:
                result.append({
                    "question_number": str(qno),
                    "answer": val
                })
        return result
    return []

def parse_markdown_style(text: str) -> List[Dict]:
    parsed = []
    lines = text.splitlines()
    current_question_number = None
    current_question = None
    current_answer_lines = []

    for line in lines:
        line = line.strip()
        if line.startswith("### Q"):
            if current_question_number is not None:
                parsed.append({
                    "question_number": current_question_number,
                    "question": current_question,
                    "answer": "\n".join(current_answer_lines).strip() or "Not answered"
                })
            parts = line[4:].split(".", 1)
            current_question_number = parts[0].strip()
            current_question = parts[1].strip() if len(parts) > 1 else ""
            current_answer_lines = []
        elif line.startswith("**Answer:**"):
            current_answer_lines.append(line.replace("**Answer:**", "").strip())
        elif current_answer_lines is not None:
            current_answer_lines.append(line)

    if current_question_number is not None:
        parsed.append({
            "question_number": current_question_number,
            "question": current_question,
            "answer": "\n".join(current_answer_lines).strip() or "Not answered"
        })

    return parsed

def save_to_json_file(data: List[Dict], filename: str = "structured_answers.json") -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"✅ Saved structured answers to {filename}")
