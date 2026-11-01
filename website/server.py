import asyncio,json,os,sys,time
from pathlib import Path
from fastapi import FastAPI,HTTPException,Query,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse,StreamingResponse
from fastapi.staticfiles import StaticFiles

# import threading
# from flask import Flask, request, jsonify
# flask_app = Flask(__name__)

app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

b_dir=Path(__file__).resolve().parent
w_root=b_dir.parent
st_dir=b_dir/"static"
rt_file=b_dir/"ratings.jsonl"

# def old_sync_runner(pr):
#     os.system(f"python render.py --prompt '{pr}'")
#     return "/tmp/out.mp4"

def get_script():
    # priority to root render.py
    for f in [w_root/"render.py",b_dir/"render.py",b_dir/"render_example.py"]:
        if f.exists():
            return f
    return b_dir/"render_example.py"

# @app.get("/api/poll")
# def poll(tid:str):
#     if os.path.exists(f"/tmp/{tid}.mp4"):
#         return {"done":True,"url":f"/api/video?path=/tmp/{tid}.mp4"}
#     return {"done":False}

async def stream_proc(pr,inc):
    scr=get_script()
    cmd=[sys.executable,str(scr),"--prompt",pr]
    if inc:
        cmd.append("--include-code")

    yield f"data: {json.dumps({'type':'init','script':scr.name})}\n\n"

    try:
        p=await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(w_root)
        )
    except Exception as err:
        yield f"data: {json.dumps({'type':'error','message':str(err)})}\n\n"
        return

    # todo: fix stderr buffer blocking
    while True:
        line=await p.stdout.readline()
        if not line:
            break
        raw=line.decode("utf-8",errors="replace").strip()
        if not raw:
            continue
        if raw.startswith("{") and raw.endswith("}"):
            try:
                # pass json direct
                json.loads(raw)
                yield f"data: {raw}\n\n"
                continue
            except:
                pass
        if ".mp4" in raw.lower():
            vp=raw.replace("VIDEO_PATH:","").strip().strip('"').strip("'")
            yield f"data: {json.dumps({'type':'complete','video_path':vp})}\n\n"
            continue
        yield f"data: {json.dumps({'type':'log','message':raw})}\n\n"

    await p.wait()
    if p.returncode!=0:
        err_out=(await p.stderr.read()).decode("utf-8",errors="replace").strip()
        yield f"data: {json.dumps({'type':'error','message':err_out or f'Exit code {p.returncode}'})}\n\n"

@app.get("/api/render")
async def api_render(prompt:str=Query(...),include_code:bool=Query(False)):
    return StreamingResponse(
        stream_proc(prompt,include_code),
        media_type="text/event-stream",
        headers={"Cache-Control":"no-cache","Connection":"keep-alive","X-Accel-Buffering":"no"}
    )

@app.get("/api/video")
async def api_video(path:str=Query(...)):
    f=Path(path).resolve()
    if not f.exists():
        f=(w_root/path).resolve()
    if not f.exists() or not f.is_file():
        raise HTTPException(status_code=404,detail="Video not found")
    return FileResponse(str(f),media_type="video/mp4",filename=f.name)

@app.post("/api/rate")
async def api_rate(req:Request):
    b=await req.json()
    r=int(b.get("rating",0))
    if r<1 or r>10:
        raise HTTPException(status_code=400,detail="Invalid rating")
    ent={"t":time.time(),"rating":r,"prompt":b.get("prompt",""),"video":b.get("video_path","")}
    with open(rt_file,"a",encoding="utf-8") as f_out:
        f_out.write(json.dumps(ent)+"\n")
    return {"status":"ok"}

# @app.get("/status")
# def get_st():
#     return {"status":"running","uptime":time.time()}

app.mount("/",StaticFiles(directory=str(st_dir),html=True),name="static")

if __name__=="__main__":
    import uvicorn
    # run dev
    uvicorn.run("server:app",host="0.0.0.0",port=8000,reload=True)
