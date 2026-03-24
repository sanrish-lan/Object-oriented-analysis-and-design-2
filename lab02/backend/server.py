from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import shutil
import os
import uuid

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

database = []

@app.post("/api/upload")
async def upload_video(caption: str = Form(...), file: UploadFile = File(...)):
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    video_data = {
        "id": unique_filename,
        "url": f"/uploads/{unique_filename}",
        "caption": caption
    }
    database.append(video_data)
    
    print(f"[+] Загружено видео: {unique_filename} | Текст: {caption}")
    return {"status": "success", "video": video_data}

@app.get("/api/videos")
async def get_videos():
    return database[::-1]

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")
