"""
Ses → Metin → Word dönüştürücü
Flask backend: Whisper ile transkripsiyon, docx-js ile Word çıktısı
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import tempfile
import os
import subprocess
import json
from pathlib import Path
import threading
import uuid

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = Path(tempfile.gettempdir()) / "ses_transkript"
UPLOAD_DIR.mkdir(exist_ok=True)

jobs = {}

with open(Path(__file__).parent / "templates" / "index.html", encoding="utf-8") as f:
    HTML_PAGE = f.read()


@app.route("/")
def index():
    return HTML_PAGE


@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "Ses dosyası bulunamadı"}), 400

    file = request.files["audio"]
    model = request.form.get("model", "base")
    language = request.form.get("language", "")

    if file.filename == "":
        return jsonify({"error": "Dosya seçilmedi"}), 400

    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "processing", "progress": "Dosya yükleniyor..."}

    suffix = Path(file.filename).suffix or ".mp3"
    audio_path = UPLOAD_DIR / f"{job_id}{suffix}"
    file.save(str(audio_path))

    filename = file.filename

    def process():
        try:
            jobs[job_id]["progress"] = "Whisper modeli yükleniyor..."
            import whisper
            model_obj = whisper.load_model(model)

            jobs[job_id]["progress"] = "Transkripsiyon yapılıyor..."
            opts = {}
            if language:
                opts["language"] = language

            result = model_obj.transcribe(str(audio_path), **opts)
            text = result["text"].strip()
            detected_lang = result.get("language", "?")

            jobs[job_id].update({
                "status": "done",
                "text": text,
                "language": detected_lang,
                "filename": filename,
            })

        except Exception as e:
            jobs[job_id] = {"status": "error", "error": str(e)}
        finally:
            try:
                audio_path.unlink()
            except Exception:
                pass

    thread = threading.Thread(target=process)
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/status/<job_id>")
def status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "İş bulunamadı"}), 404
    return jsonify(job)


@app.route("/download/<job_id>")
def download(job_id):
    job = jobs.get(job_id)
    if not job or job.get("status") != "done":
        return jsonify({"error": "Transkript hazır değil"}), 400

    text = job["text"]
    filename = Path(job.get("filename", "transkript")).stem
    detected_lang = job.get("language", "")

    docx_path = UPLOAD_DIR / f"{job_id}.docx"
    js_script = build_docx_script(text, filename, detected_lang, str(docx_path))

    js_path = UPLOAD_DIR / f"{job_id}.js"
    js_path.write_text(js_script, encoding="utf-8")

    try:
        result = subprocess.run(
            ["node", str(js_path)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return jsonify({"error": f"Word oluşturma hatası: {result.stderr}"}), 500
    finally:
        js_path.unlink(missing_ok=True)

    return send_file(
        str(docx_path),
        as_attachment=True,
        download_name=f"{filename}_transkript.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def build_docx_script(text: str, title: str, lang: str, output_path: str) -> str:
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    safe_title = json.dumps(title)
    safe_lang = json.dumps(lang)
    safe_output = json.dumps(output_path)

    para_lines = []
    for p in paragraphs:
        safe_p = json.dumps(p)
        para_lines.append(f"""
        new Paragraph({{
          children: [new TextRun({{ text: {safe_p}, size: 24, font: "Calibri" }})],
          spacing: {{ after: 160 }}
        }})""")

    paras_js = ",\n".join(para_lines)

    return f"""
const {{ Document, Packer, Paragraph, TextRun, HeadingLevel }} = require("docx");
const fs = require("fs");

const title = {safe_title};
const lang = {safe_lang};
const outputPath = {safe_output};
const now = new Date().toLocaleString("tr-TR");

const doc = new Document({{
  styles: {{
    default: {{ document: {{ run: {{ font: "Calibri", size: 24 }} }} }},
    paragraphStyles: [
      {{
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: {{ size: 36, bold: true, font: "Calibri", color: "1A1A2E" }},
        paragraph: {{ spacing: {{ before: 0, after: 240 }}, outlineLevel: 0 }}
      }}
    ]
  }},
  sections: [{{
    properties: {{
      page: {{
        size: {{ width: 11906, height: 16838 }},
        margin: {{ top: 1440, right: 1440, bottom: 1440, left: 1800 }}
      }}
    }},
    children: [
      new Paragraph({{
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun({{ text: "Transkript: " + title, bold: true, font: "Calibri" }})]
      }}),
      new Paragraph({{
        children: [
          new TextRun({{ text: "Oluşturulma: " + now, size: 18, color: "888888", font: "Calibri" }}),
          lang ? new TextRun({{ text: "   •   Algılanan dil: " + lang.toUpperCase(), size: 18, color: "888888", font: "Calibri" }}) : new TextRun("")
        ],
        spacing: {{ after: 400 }}
      }}),
      new Paragraph({{
        children: [new TextRun({{ text: "" }})],
        border: {{ bottom: {{ style: "single", size: 6, color: "DDDDDD", space: 1 }} }},
        spacing: {{ after: 400 }}
      }}),
      {paras_js}
    ]
  }}]
}});

Packer.toBuffer(doc).then(buf => {{
  fs.writeFileSync(outputPath, buf);
  console.log("OK: " + outputPath);
}}).catch(e => {{
  console.error(e);
  process.exit(1);
}});
"""


if __name__ == "__main__":
    import os
    print("🎙️  Ses → Metin → Word Sunucusu başlatılıyor...")
    print("🌐  http://localhost:5000 adresini açın")
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
