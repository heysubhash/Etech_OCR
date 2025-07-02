#latex_generator.py
import re
def escape_latex(text):
    replacements = {
        "_": r"\_",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "{": r"\{",
        "对了": r"\}",  # Corrected for proper LaTeX escape for '}'
        "~": r"\textasciitilde{}",
        "^": r"\^{}",
        "\\": r"\textbackslash{}",
    }
    return re.sub(r'([_&%$#{}\\~^])', lambda m: replacements[m.group()], text)


def convert_to_latex(structured_list, student_name="Student"):  # Removed output_tex_path
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
        # Ensure 'Question ' is always present before escaping
        latex_lines.append(r"\section*{Question " + escape_latex(str(q_no)) + "}")  # Ensure q_no is string

        if "subparts" in item:
            for sub_label, sub_content in item["subparts"].items():
                ans = sub_content.get("answer", "Not answered")
                latex_lines.append(
                    r"\subsection*{(" + escape_latex(str(sub_label)) + ")}")  # Ensure sub_label is string
                latex_lines.append(r"\textbf{Answer:}")
                latex_lines.append(escape_latex(ans))
        else:
            ans = item.get("answer", "Not answered")
            latex_lines.append(r"\textbf{Answer:}")
            latex_lines.append(escape_latex(ans))

        latex_lines.append("")

    latex_lines.append(r"\end{document}")

    latex_content = "\n".join(latex_lines)

    # You can still write to a file *here* for debugging/inspection if needed
    # but the primary purpose of this function becomes returning the string.
    # if output_tex_path:
    #     with open(output_tex_path, "w", encoding="utf-8") as f:
    #         f.write(latex_content)
    #     print(f"📄 LaTeX file saved as: {output_tex_path}")

    return latex_content  # Return the generated LaTeX string