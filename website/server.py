import asyncio
import json
import os
import sys
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="LearnAnything Minimal Web Runner")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = BASE_DIR.parent
STATIC_DIR = BASE_DIR / "static"
RATINGS_FILE = BASE_DIR / "ratings.jsonl"

def resolve_render_script() -> Path:
    """Finds render.py in root or website dir, falling back to render_example.py."""
    candidates = [
        WORKSPACE_ROOT / "render.py",
        BASE_DIR / "render.py",
        BASE_DIR / "render_example.py"
    ]
    for p in candidates:
        if p.exists():
            return p
    return BASE_DIR / "render_example.py"

async def run_render_stream(prompt: str, include_code: bool) -> AsyncGenerator[str, None]:
    render_script = resolve_render_script()
    
    cmd = [sys.executable, str(render_script), "--prompt", prompt]
    if include_code:
        cmd.append("--include-code")

    yield f"data: {json.dumps({'type': 'init', 'script': render_script.name, 'include_code': include_code})}\n\n"

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(WORKSPACE_ROOT),
            env=os.environ.copy()
        )
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': f'Failed to launch {render_script.name}: {str(e)}'})}\n\n"
        return

    stderr_lines = []

    async def read_stderr():
        while True:
            line = await proc.stderr.readline()
            if not line:
                break
            stderr_lines.append(line.decode("utf-8", errors="replace"))

    stderr_task = asyncio.create_task(read_stderr())

    while True:
        line_bytes = await proc.stdout.readline()
        if not line_bytes:
            break
        raw_line = line_bytes.decode("utf-8", errors="replace").strip()
        if not raw_line:
            continue

        # If stdout is valid JSON, stream it directly
        if raw_line.startswith("{") and raw_line.endswith("}"):
            try:
                parsed = json.loads(raw_line)
                yield f"data: {json.dumps(parsed)}\n\n"
                continue
            except json.JSONDecodeError:
                pass

        # If stdout prints raw video path (e.g. /path/to/video.mp4 or VIDEO_PATH: ...)
        if ".mp4" in raw_line.lower():
            clean_path = raw_line.replace("VIDEO_PATH:", "").strip().strip('"').strip("'")
            yield f"data: {json.dumps({'type': 'complete', 'video_path': clean_path, 'message': 'Video generated!'})}\n\n"
            continue

        # Otherwise emit as log line
        yield f"data: {json.dumps({'type': 'log', 'message': raw_line})}\n\n"

    await proc.wait()
    await stderr_task

    if proc.returncode != 0:
        err_msg = "".join(stderr_lines).strip() or f"Process exited with error code {proc.returncode}"
        yield f"data: {json.dumps({'type': 'error', 'message': err_msg})}\n\n"

@app.get("/api/render")
async def render_api(prompt: str = Query(...), include_code: bool = Query(False)):
    """Server-Sent Events endpoint streaming the generation progress."""
    return StreamingResponse(
        run_render_stream(prompt, include_code),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/api/video")
async def get_video(path: str = Query(...)):
    """Serves the generated MP4 file securely."""
    video_file = Path(path).resolve()
    
    # Check if relative to workspace
    if not video_file.exists():
        video_file = (WORKSPACE_ROOT / path).resolve()

    if not video_file.exists() or not video_file.is_file():
        raise HTTPException(status_code=404, detail=f"Video file not found at: {path}")

    return FileResponse(str(video_file), media_type="video/mp4", filename=video_file.name)

class RatingRequest(BaseModel):
    rating: int
    prompt: str
    video_path: str = ""

@app.post("/api/rate")
async def rate_video(req: RatingRequest):
    """Saves user rating (1-10) to a JSON Lines file."""
    if not (1 <= req.rating <= 10):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 10.")

    entry = {
        "timestamp": asyncio.get_event_loop().time(),
        "rating": req.rating,
        "prompt": req.prompt,
        "video_path": req.video_path
    }

    with open(RATINGS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return {"status": "ok", "message": f"Rating of {req.rating}/10 recorded."}

# Mount static web directory
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("\n[+] Starting LearnAnything Minimal Web Server on http://localhost:8000\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
