"""
build_compact_source_code_pdf.py
Compiles a compact, high-density PDF containing ONLY the core implementation and logic-related source code.
Uses a two-column layout with Pygments syntax highlighting, compact monospace font, and two-pass page numbers
to maximize content per page while preserving 100% of the original logic.
"""

import os
import re
from pygments import lex
from pygments.lexers import PythonLexer, JavascriptLexer, TextLexer
from pygments.token import Token
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, XPreformatted, Spacer, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas

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

def highlight_and_wrap(code_text, lexer, max_cols=82):
    lines = code_text.splitlines()
    formatted_lines = []

    for line in lines:
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
            indent_match = len(line) - len(line.lstrip())
            indent_str = " " * min(indent_match + 2, 20)

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
    Two-pass canvas for running headers and 'Page X of Y' footers.
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
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#4A5568"))

        # Top Header Rule
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(24, 768, 588, 768)
        self.drawString(24, 772, "OmniSign 3D - Core Logic & Implementation Source Code")

        # Bottom Footer Rule
        self.line(24, 22, 588, 22)
        self.setFont("Helvetica", 7.5)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(588, 12, page_text)
        self.drawString(24, 12, "OmniSign 3D Studio - Project Source Code Listing")

        self.restoreState()


def generate_compact_pdf():
    output_filename = "Project_Source_Code.pdf"
    root_dir = os.path.dirname(os.path.abspath(__file__))

    # Page Geometry: Letter (612 x 792 pt), 24 pt horizontal margins, 32 pt vertical margins
    PAGE_WIDTH, PAGE_HEIGHT = letter
    margin_x = 24
    margin_y = 28
    gap = 10
    col_width = (PAGE_WIDTH - (2 * margin_x) - gap) / 2  # 277 pt
    col_height = PAGE_HEIGHT - (2 * margin_y)             # 736 pt

    frame1 = Frame(margin_x, margin_y, col_width, col_height, id='col1',
                   leftPadding=0, rightPadding=3, topPadding=0, bottomPadding=0)
    frame2 = Frame(margin_x + col_width + gap, margin_y, col_width, col_height, id='col2',
                   leftPadding=3, rightPadding=0, topPadding=0, bottomPadding=0)

    template = PageTemplate(id='two_columns', frames=[frame1, frame2])
    doc = BaseDocTemplate(output_filename, pagesize=letter)
    doc.addPageTemplates([template])

    code_style = ParagraphStyle(
        'CompactCode',
        fontName='Courier',
        fontSize=5.4,
        leading=6.6,
        textColor=colors.HexColor('#1A202C')
    )

    header_style = ParagraphStyle(
        'BannerText',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9,
        textColor=colors.white
    )

    story = []

    # 1. requirements.txt
    req_path = os.path.join(root_dir, "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            req_code = f.read()
        banner = Table([[Paragraph("<b>FILE: requirements.txt (Core Dependencies)</b>", header_style)]], colWidths=[col_width])
        banner.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1A365D')),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(banner)
        story.append(Spacer(1, 2))
        story.append(XPreformatted(highlight_and_wrap(req_code, TextLexer(), max_cols=82), code_style))
        story.append(Spacer(1, 6))

    # 2. app.py (Core Backend REST API, Neural Ensemble & NLP Translation)
    app_path = os.path.join(root_dir, "app.py")
    if os.path.exists(app_path):
        with open(app_path, "r", encoding="utf-8") as f:
            app_code = f.read()
        banner = Table([[Paragraph("<b>FILE: app.py (Backend REST API, Neural Ensemble & Translation Logic)</b>", header_style)]], colWidths=[col_width])
        banner.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1A365D')),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(banner)
        story.append(Spacer(1, 2))
        story.append(XPreformatted(highlight_and_wrap(app_code, PythonLexer(), max_cols=82), code_style))
        story.append(Spacer(1, 6))

    # 3. train_model.py (Spatial-Temporal Transformer & BiLSTM Architectures)
    train_path = os.path.join(root_dir, "train_model.py")
    if os.path.exists(train_path):
        with open(train_path, "r", encoding="utf-8") as f:
            train_code = f.read()
        banner = Table([[Paragraph("<b>FILE: train_model.py (Spatial-Temporal Transformer & BiLSTM Architecture)</b>", header_style)]], colWidths=[col_width])
        banner.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1A365D')),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(banner)
        story.append(Spacer(1, 2))
        story.append(XPreformatted(highlight_and_wrap(train_code, PythonLexer(), max_cols=82), code_style))
        story.append(Spacer(1, 6))

    # 4. extract_features_parallel.py (225-Point MediaPipe Feature Pipeline)
    feat_path = os.path.join(root_dir, "extract_features_parallel.py")
    if os.path.exists(feat_path):
        with open(feat_path, "r", encoding="utf-8") as f:
            feat_code = f.read()
        banner = Table([[Paragraph("<b>FILE: extract_features_parallel.py (MediaPipe 225-Point Extraction Logic)</b>", header_style)]], colWidths=[col_width])
        banner.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1A365D')),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(banner)
        story.append(Spacer(1, 2))
        story.append(XPreformatted(highlight_and_wrap(feat_code, PythonLexer(), max_cols=82), code_style))
        story.append(Spacer(1, 6))

    # 5. live_test.py (Real-Time Vision & Desktop Prediction Loop)
    live_path = os.path.join(root_dir, "live_test.py")
    if os.path.exists(live_path):
        with open(live_path, "r", encoding="utf-8") as f:
            live_code = f.read()
        banner = Table([[Paragraph("<b>FILE: live_test.py (Desktop Real-Time OpenCV Inference Loop)</b>", header_style)]], colWidths=[col_width])
        banner.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1A365D')),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(banner)
        story.append(Spacer(1, 2))
        story.append(XPreformatted(highlight_and_wrap(live_code, PythonLexer(), max_cols=82), code_style))
        story.append(Spacer(1, 6))

    # 6. index.html (Core JavaScript 3D Kinematics & Client Logic)
    html_path = os.path.join(root_dir, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html_raw = f.read()
        
        # Extract the client logic inside <script>
        scripts = re.findall(r'<script\b[^>]*>(.*?)</script>', html_raw, re.DOTALL)
        if scripts:
            js_code = scripts[-1].strip()
            banner = Table([[Paragraph("<b>FILE: index.html (Client Logic: Three.js 3D Avatar, Hermite Kinematics & TTS)</b>", header_style)]], colWidths=[col_width])
            banner.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1A365D')),
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('LEFTPADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(banner)
            story.append(Spacer(1, 2))
            story.append(XPreformatted(highlight_and_wrap(js_code, JavascriptLexer(), max_cols=82), code_style))
            story.append(Spacer(1, 6))

    print("Building compact high-density PDF ...")
    doc.build(story, canvasmaker=NumberedCanvas)

    if os.path.exists(output_filename):
        size_mb = os.path.getsize(output_filename) / (1024 * 1024)
        print(f"SUCCESS: {output_filename} compiled! Size: {size_mb:.2f} MB")
    else:
        print(f"ERROR: {output_filename} was not created.")

if __name__ == "__main__":
    generate_compact_pdf()
