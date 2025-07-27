import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.services.chat import *
from app.services.tempfile_manager import *
from app.services.progress_manager import *
from app.state import progress_store, data_store, current_task_id

app = FastAPI()

# CORS for AJAX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates setup
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

temp_folder = "temp"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    global current_task_id
    task_id = str(uuid.uuid4())

    # print("Generated Task ID:", task_id)

    current_task_id = task_id


    clean_temp_folder(temp_folder)
    filename = f"temp_{task_id}{os.path.splitext(file.filename)[1]}"
    temp_path = os.path.join("temp", filename)

    # os.makedirs("temp", exist_ok=True)
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    progress_store[task_id] = {
    "text_extraction": 0,
    "chunk_creation": 0,
    "embedding_generation": 0
}

    data_store[task_id] = {"file_path": temp_path}

    background_tasks.add_task(process_document, task_id, temp_path)
    
    # return RedirectResponse(url=f"/chat?task_id={task_id}", status_code=302)
    return JSONResponse({"task_id": task_id})


@app.get("/progress/{task_id}/{phase}")
async def get_progress(task_id: str, phase: str):
    return {
        "progress": progress_store.get(task_id, {}).get(phase, 0)
    }

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, task_id: str):
    if task_id not in data_store:
        return RedirectResponse(url="/upload")
    return templates.TemplateResponse("chat.html", {"request": request, "task_id": task_id})

@app.post("/query/{task_id}")
async def query_pdf(task_id: str, request: Request):
    body = await request.json()
    query = body.get("query")
    history= body.get("history")
    # print(history)
    formatted_history = "\n".join([f"{i+1}. {query}" for i, query in enumerate(history or [])])
    # print(formatted_history)

    if task_id not in data_store:
        raise HTTPException(status_code=404, detail="Invalid task ID")

    faiss_index = data_store[task_id].get("faiss_index")
    chunks = data_store[task_id].get("chunks")

    if not faiss_index or not chunks:
        raise HTTPException(status_code=400, detail="Data not processed yet")
    
    structured_query= get_aggregated_query(formatted_history, query)
    similar_chunks = get_similar_chunks(faiss_index, structured_query)
    response = get_llm_response(similar_chunks, structured_query)

    return {"response": response.content}




