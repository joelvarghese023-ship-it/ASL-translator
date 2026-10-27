"""
build_source_code_pdf.py
Generates Project_Source_Code.pdf containing ONLY the source code of the project.
Strictly excludes all documentation, intro, summaries, and explanations.
Includes filename labels, syntax highlighting, proper indentation, and page numbers.
"""

import os
import sys
from pygments import lex
from pygments.lexers import PythonLexer, HtmlLexer, JsonLexer, TextLexer
from pygments.token import Token
from reportlab.platypus import SimpleDocTemplate, XPreformatted, PageBreak, Spacer, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# Syntax highlighting color map
TOKEN_COLORS = {
    Token.Keyword: ("#0000FF", True, False),
    Token.Keyword.Constant: ("#0000FF", True, False),
    Token.Keyword.Declaration: ("#0000FF", True, False),
    Token.Keyword.Namespace: ("#0000FF", True, False),
    Token.Keyword.Type: ("#267F99", True, False),
    Token.Name.Class: ("#267F99", True, False),
    Token.Name.Function: ("#795E26", True, False),
    Token.Name.Builtin: ("#0000FF", False, False),
    Token.Name.Tag: ("#800000", True, False),
    Token.Name.Attribute: ("#E50000", False, False),
    Token.String: ("#A31515", False, False),
    Token.String.Doc: ("#A31515", False, True),
    Token.Number: ("#098658", False, False),
    Token.Comment: ("#008000", False, True),
    Token.Comment.Single: ("#008000", False, True),
    Token.Comment.Multiline: ("#008000", False, True),
    Token.Operator: ("#000000", False, False),
    Token.Punctuation: ("#000000", False, False),
}

def escape_xml(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def highlight_and_wrap(code_text, lexer, max_cols=125):
    """
    Applies Pygments syntax highlighting and wraps lines longer than max_cols
    to ensure text stays within printable page margins.
    """
    lines = code_text.splitlines()
    formatted_lines = []

    for line in lines:
        # Expand tabs to 4 spaces
        line = line.replace('\t', '    ')

        if len(line) <= max_cols:
            parts = []
            for token_type, value in lex(line, lexer):
                curr = token_type
                color_info = None
                while curr:
                    if curr in TOKEN_COLORS:
                        color_info = TOKEN_COLORS[curr]
                        break
                    curr = curr.parent

                escaped = escape_xml(value)
                if color_info:
                    c, b, it = color_info
                    tag_open = f'<font color="{c}">'
                    tag_close = '</font>'
                    if b: tag_open += '<b>'; tag_close = '</b>' + tag_close
                    if it: tag_open += '<i>'; tag_close = '</i>' + tag_close
                    parts.append(f"{tag_open}{escaped}{tag_close}")
                else:
                    parts.append(escaped)
            formatted_lines.append("".join(parts))
        else:
            # Long line: wrap at max_cols with indent
            indent_match = len(line) - len(line.lstrip())
            indent_str = " " * (indent_match + 4)

            token_list = list(lex(line, lexer))
            curr_line_parts = []
            curr_len = 0

            for token_type, value in token_list:
                curr = token_type
                color_info = None
                while curr:
                    if curr in TOKEN_COLORS:
                        color_info = TOKEN_COLORS[curr]
                        break
                    curr = curr.parent

                val_len = len(value)
                if curr_len + val_len > max_cols and curr_len > 0:
                    formatted_lines.append("".join(curr_line_parts))
                    curr_line_parts = [indent_str]
                    curr_len = len(indent_str)

                escaped = escape_xml(value)
                if color_info:
                    c, b, it = color_info
                    tag_open = f'<font color="{c}">'
                    tag_close = '</font>'
                    if b: tag_open += '<b>'; tag_close = '</b>' + tag_close
                    if it: tag_open += '<i>'; tag_close = '</i>' + tag_close
                    curr_line_parts.append(f"{tag_open}{escaped}{tag_close}")
                else:
                    curr_line_parts.append(escaped)
                curr_len += val_len

            if curr_line_parts:
                formatted_lines.append("".join(curr_line_parts))

    return "\n".join(formatted_lines)


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to compute total page count and render running header & footer.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))

        # Top Header Rule
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.6)
        self.line(36, 756, 576, 756)
        self.drawString(36, 762, "Project Source Code Listing")

        # Bottom Footer Rule
        self.line(36, 36, 576, 36)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 24, page_text)

        self.restoreState()


def generate_source_code_pdf():
    output_filename = "Project_Source_Code.pdf"
    root_dir = os.path.dirname(os.path.abspath(__file__))

    # Target source files in logical execution & architecture order
    source_files = [
        ("requirements.txt", TextLexer()),
        ("app.py", PythonLexer()),
        ("index.html", HtmlLexer()),
        ("live_test.py", PythonLexer()),
        ("train_model.py", PythonLexer()),
        ("train_model_2000.py", PythonLexer()),
        ("extract_features_parallel.py", PythonLexer()),
        ("split_directories.py", PythonLexer()),
        ("generate_paper_assets.py", PythonLexer()),
        ("build_research_paper_docx.py", PythonLexer()),
        ("generate_phase3_presentation.py", PythonLexer()),
        ("generate_presentation.py", PythonLexer()),
        ("classes.json", JsonLexer()),
    ]

    # Setup document: Letter (612 x 792 pt), margins 36 pt (0.5 in)
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    code_style = ParagraphStyle(
        'SourceCode',
        fontName='Courier',
        fontSize=6.8,
        leading=8.2,
        textColor=colors.HexColor('#1E1E1E')
    )

    header_style = ParagraphStyle(
        'FileHeader',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.white
    )

    story = []

    for file_idx, (filename, lexer) in enumerate(source_files):
        file_path = os.path.join(root_dir, filename)
        if not os.path.exists(file_path):
            print(f"Warning: File {filename} not found, skipping.")
            continue

        print(f"Processing ({file_idx + 1}/{len(source_files)}): {filename} ...")

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            code_content = f.read()

        # PageBreak between files (except before the first file)
        if file_idx > 0:
            story.append(PageBreak())

        # Clean Filename Header Banner
        banner_data = [[Paragraph(f"<b>File: {filename}</b>", header_style)]]
        banner_table = Table(banner_data, colWidths=[540])
        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1A365D')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))
        story.append(banner_table)
        story.append(Spacer(1, 6))

        # Syntax highlighted and wrapped code block
        highlighted_code = highlight_and_wrap(code_content, lexer, max_cols=125)
        story.append(XPreformatted(highlighted_code, code_style))
        story.append(Spacer(1, 12))

    print("Compiling PDF with NumberedCanvas ...")
    doc.build(story, canvasmaker=NumberedCanvas)

    if os.path.exists(output_filename):
        size_mb = os.path.getsize(output_filename) / (1024 * 1024)
        print(f"SUCCESS: {output_filename} generated successfully! Size: {size_mb:.2f} MB")
    else:
        print(f"ERROR: {output_filename} was not created.")

if __name__ == "__main__":
    generate_source_code_pdf()
