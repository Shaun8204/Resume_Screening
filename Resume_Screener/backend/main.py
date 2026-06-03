from concurrent.futures import ThreadPoolExecutor
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np

from embeddings import get_embeddings, cosine_sim

from utils import (
    save_upload_to_temp,
    extract_text_from_file,
    cleanup_path,
)

app = FastAPI(title="Resume Screener API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MatchResult(BaseModel):
    filename: str
    score: float
    snippet: str | None = None


def process_file(upload: UploadFile):
    tmp = save_upload_to_temp(upload)
    try:
        text = extract_text_from_file(tmp)
    finally:
        cleanup_path(tmp)
    return upload.filename, text


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/screen", response_model=List[MatchResult])
async def screen(job_description: str = Form(...), files: List[UploadFile] | None = File(None), top_k: int = Form(10)):
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="job_description is required")

    files = files or []
    if len(files) > 200:
        raise HTTPException(status_code=400, detail="max 200 files allowed")

    # Process files concurrently (IO-bound parsing)
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(process_file, f) for f in files]
        results = [f.result() for f in futures]

    filenames = [r[0] for r in results]
    docs = [r[1] or "" for r in results]

    # If no resumes, return empty list
    if not docs:
        return []

    # Compute semantic embeddings for job and resumes
    texts = [job_description] + docs
    try:
        vecs = get_embeddings(texts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    job_vec = vecs[0:1]
    resume_vecs = vecs[1:]

    sims = cosine_sim(job_vec, resume_vecs).flatten()
    ranked_idx = np.argsort(-sims)

    results_out = []
    for idx in ranked_idx[:top_k]:
        score = float(sims[idx])
        text = docs[idx]
        snippet = (text[:500].strip() + "...") if text else ""
        results_out.append(MatchResult(filename=filenames[idx], score=score, snippet=snippet))

    return results_out
