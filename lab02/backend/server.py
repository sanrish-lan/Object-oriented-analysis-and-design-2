from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import shutil
import os
import uuid

app = FastAPI()

# Папка для сохранения видео
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Простая "база данных" в памяти (список словарей)
# В реальном проекте тут был бы SQL, но для лабы нам хватит списка
database = []

# --- 1. ЭНДПОИНТ ДЛЯ ТВОЕГО C++ КЛИЕНТА (ФАСАДА) ---
@app.post("/api/upload")
async def upload_video(caption: str = Form(...), file: UploadFile = File(...)):
    # Генерируем уникальное имя файла, чтобы видео не перезаписывали друг друга
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Сохраняем файл на диск
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Сохраняем инфу о видео в нашу "БД"
    video_data = {
        "id": unique_filename,
        "url": f"/uploads/{unique_filename}",
        "caption": caption
    }
    database.append(video_data)
    
    print(f"[+] Загружено видео: {unique_filename} | Текст: {caption}")
    return {"status": "success", "video": video_data}

# --- 2. ЭНДПОИНТ ДЛЯ ВЕБ-ФРОНТЕНДА ---
@app.get("/api/videos")
async def get_videos():
    # Отдаем список видео в обратном порядке (новые сверху)
    return database[::-1]

# --- 3. РАЗДАЧА СТАТИКИ И ВЕБ-СТРАНИЦЫ ---
# Раздаем папку uploads, чтобы тег <video> мог грузить файлы
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Главная страница отдаст наш index.html
@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")
