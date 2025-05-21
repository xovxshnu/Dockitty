from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF
import docx
import requests
import os

app = FastAPI()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), action: str = Form(...)):
    content = ""
    if file.filename.endswith(".pdf"):
        pdf = fitz.open(stream=await file.read(), filetype="pdf")
        for page in pdf:
            content += page.get_text()
    elif file.filename.endswith(".docx"):
        doc = docx.Document(await file.read())
        for para in doc.paragraphs:
            content += para.text + "\n"
    else:
        return JSONResponse({"error": "Unsupported file format"}, status_code=400)

    prompt = f"{action}:\n{content}"
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        json={
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": prompt}u
            ]
        }
    )
    result = response.json()
    return {"reply": result["choices"][0]["message"]["content"]}
