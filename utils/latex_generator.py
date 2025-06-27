#latex_generator
import re

def escape_latex(text):
    replacements = {
        "_": r"\_",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\^{}",
        "\\": r"\textbackslash{}",
    }
    return re.sub(r'([_&%$#{}~^\\])', lambda m: replacements[m.group()], text)

def convert_to_latex(structured_list, output_tex_path="student_answers.tex", student_name="Student"):
    latex_lines = [
        r"\documentclass[12pt]{article}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{amsmath, amsfonts, amssymb}",
        r"\usepackage{geometry}",
        r"\geometry{margin=1in}",
        rf"\title{{Answer Sheet - {escape_latex(student_name)}}}",
        r"\date{}",
        r"\begin{document}",
        r"\maketitle",
        ""
    ]

    for item in structured_list:
        q_no = item.get("question_number", "Unknown")
        latex_lines.append(r"\section*{Question " + escape_latex(q_no) + "}")

        if "subparts" in item:
            for sub_label, sub_content in item["subparts"].items():
                ans = sub_content.get("answer", "Not answered")
                latex_lines.append(r"\subsection*{(" + escape_latex(sub_label) + ")}")
                latex_lines.append(r"\textbf{Answer:}")
                latex_lines.append(escape_latex(ans))
        else:
            ans = item.get("answer", "Not answered")
            latex_lines.append(r"\textbf{Answer:}")
            latex_lines.append(escape_latex(ans))

        latex_lines.append("")

    latex_lines.append(r"\end{document}")

    with open(output_tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(latex_lines))

    print(f"📄 LaTeX file saved as: {output_tex_path}")
