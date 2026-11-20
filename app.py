
from flask import Flask, request, render_template_string, send_file
import pymupdf
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

STYLE = """
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{
font-family:Arial,sans-serif;
background:linear-gradient(135deg,#dce5ff,#f3eaff);
min-height:100vh;padding:35px 15px;color:#202b50;
}
.container{
max-width:900px;margin:25px auto;background:white;
padding:40px;border-radius:22px;
box-shadow:0 15px 40px rgba(35,50,100,.13);
}
.logo{text-align:center;color:#4055dc;font-size:38px;
font-weight:bold;margin-bottom:10px}
.subtitle{text-align:center;color:#78809a;margin-bottom:30px}
h2{text-align:center;margin-bottom:15px}
h3{margin:20px 0 12px;color:#3549bd}
.upload{
border:2px dashed #6575e8;border-radius:15px;
padding:35px;text-align:center;background:#f8f9ff;
margin:25px 0;
}
input[type=file]{margin:15px;max-width:100%}
button,.btn{
display:inline-block;background:#4055dc;color:white;
border:0;border-radius:10px;padding:14px 25px;
font-size:15px;cursor:pointer;text-decoration:none;
margin:8px;font-weight:bold;
}
button:hover,.btn:hover{background:#293cb8}
.stats{
display:flex;gap:15px;justify-content:center;
flex-wrap:wrap;margin:25px 0;
}
.stat{
background:#f0f2ff;padding:20px;border-radius:12px;
text-align:center;flex:1;min-width:130px;
}
.stat strong{display:block;font-size:25px;color:#4055dc}
textarea{
width:100%;height:350px;padding:18px;
border:1px solid #ccd2e8;border-radius:12px;
font-size:14px;line-height:1.6;resize:vertical;
background:#fbfcff;
}
.message{
padding:15px;background:#fff2e8;color:#a34b12;
border-radius:10px;margin:20px 0;
}
.center{text-align:center}
.footer{text-align:center;color:#8a91a8;margin-top:30px}
@media(max-width:600px){
.container{padding:22px}
.logo{font-size:30px}
}
</style>
"""

HOME = """
<!DOCTYPE html>
<html>
<head>
<title>DocExtract - Document Data Extractor</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
""" + STYLE + """
</head>
<body>
<div class="container">
<div class="logo">DocExtract</div>
<p class="subtitle">Intelligent Document Data Extractor</p>

<h2>Extract Your Document Data</h2>
<p class="center">Upload your PDF and extract text easily.</p>

<form action="/extract" method="POST"
enctype="multipart/form-data">
<div class="upload">
<h3>📄 Upload Your PDF</h3>
<p>Select a PDF document from your computer.</p>
<input type="file" name="document"
accept=".pdf,application/pdf" required>
<br>
<button type="submit">Extract Text →</button>
</div>
</form>

<div class="stats">
<div class="stat"><strong>PDF</strong>File Support</div>
<div class="stat"><strong>Fast</strong>Extraction</div>
<div class="stat"><strong>Easy</strong>Download</div>
</div>

<div class="footer">
Intelligent Document Data Extractor | MCA Project
</div>
</div>
</body>
</html>
"""

RESULT = """
<!DOCTYPE html>
<html>
<head>
<title>Extraction Result - DocExtract</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
""" + STYLE + """
</head>
<body>
<div class="container">
<div class="logo">DocExtract</div>
<h2>Extraction Successful! 🎉</h2>
<p class="subtitle">Your document has been processed.</p>

<div class="stats">
<div class="stat">
<strong>{{ filename }}</strong>Document Name
</div>
<div class="stat">
<strong>{{ pages }}</strong>Total Pages
</div>
<div class="stat">
<strong>{{ words }}</strong>Total Words
</div>
</div>

{% if not extracted_text.strip() %}
<div class="message">
No selectable text was found in this PDF.
It may be a scanned/image-only PDF.
</div>
{% endif %}

<h3>Extracted Text</h3>
<textarea id="result" readonly>{{ extracted_text }}</textarea>

<div class="center">
<form action="/download" method="POST">
<input type="hidden" name="text"
value="{{ extracted_text | e }}">
<button type="submit">⬇ Download Text</button>
</form>

<a class="btn" href="/">← Upload Another PDF</a>
</div>

<div class="footer">
DocExtract | MCA Python Project
</div>
</div>
</body>
</html>
"""

ERROR = """
<!DOCTYPE html>
<html>
<head>
<title>Error - DocExtract</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
""" + STYLE + """
</head>
<body>
<div class="container center">
<div class="logo">DocExtract</div>
<h2>Something Went Wrong!</h2>
<div class="message">{{ error }}</div>
<a class="btn" href="/">Go Back</a>
</div>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HOME)


@app.route("/extract", methods=["POST"])
def extract():

    if "document" not in request.files:
        return render_template_string(
            ERROR, error="Please select a PDF file."
        )

    file = request.files["document"]

    if file.filename == "":
        return render_template_string(
            ERROR, error="No file selected."
        )

    if not file.filename.lower().endswith(".pdf"):
        return render_template_string(
            ERROR, error="Only PDF files are supported."
        )

    try:
        pdf_data = file.read()

        if not pdf_data:
            return render_template_string(
                ERROR, error="The uploaded file is empty."
            )

        pdf = pymupdf.open(
            stream=pdf_data,
            filetype="pdf"
        )

        if pdf.is_encrypted:
            pdf.close()
            return render_template_string(
                ERROR, error="Password-protected PDFs are not supported."
            )

        total_pages = len(pdf)
        extracted_text = ""

        for page_number, page in enumerate(pdf, start=1):
            extracted_text += f"\n--- Page {page_number} ---\n"
            extracted_text += page.get_text("text")

        pdf.close()

        word_count = len(extracted_text.split())

        return render_template_string(
            RESULT,
            filename=file.filename,
            pages=total_pages,
            words=word_count,
            extracted_text=extracted_text
        )

    except Exception as e:
        return render_template_string(
            ERROR,
            error="Unable to read this PDF: " + str(e)
        )


@app.route("/download", methods=["POST"])
def download():

    text = request.form.get("text", "")

    output = BytesIO(text.encode("utf-8"))
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Extracted_Text.txt",
        mimetype="text/plain"
    )


@app.errorhandler(413)
def file_too_large(error):
    return render_template_string(
        ERROR,
        error="File is too large. Maximum size is 10 MB."
    ), 413


if __name__ == "__main__":
    print("DocExtract Server Started!")
    app.run(debug=True)
