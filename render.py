import sys
import os
import json
import argparse
import threading
import glob
from Main import *

def emit(data):
    print(json.dumps(data), flush=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, required=True)
    parser.add_argument("--include-code", action="store_true")
    args = parser.parse_args()

    prompt = args.prompt
    inc_code = args.include_code

    emit({"type": "stage", "stage": 1, "status": "processing", "message": "Drafting script and scenes..."})
    sects, title = scrptGen(prompt)
    emit({"type": "stage", "stage": 1, "status": "done", "script": {"project_title": title, "sections": sects}})

    emit({"type": "stage", "stage": 2, "status": "processing"})
    ths = []
    for n, sect in enumerate(sects):
        emit({"type": "section_update", "stage": 2, "section": n, "status": "processing"})
        t = threading.Thread(target=voice, args=(sect, n))
        ths.append(t)
        t.start()
    for t in ths:
        t.join()

    for n, sect in enumerate(sects):
        if "voiceoverLen" not in sect or not sect.get("voiceoverp"):
            voice(sect, n)
            if "voiceoverLen" not in sect or not sect.get("voiceoverp"):
                emit({"type": "section_update", "stage": 2, "section": n, "status": "error"})
                emit({"type": "error", "message": f"Voiceover failed for section {n}"})
                sys.exit(1)
        emit({"type": "section_update", "stage": 2, "section": n, "status": "done"})
    emit({"type": "stage", "stage": 2, "status": "done"})

    emit({"type": "stage", "stage": 3, "status": "processing"})
    ths = []
    for n, sect in enumerate(sects):
        emit({"type": "section_update", "stage": 3, "section": n, "status": "processing"})
        t = threading.Thread(target=RenderVid, args=(sect, n))
        ths.append(t)
        t.start()
    for t in ths:
        t.join()

    valid_sects = 0
    for n, s in enumerate(sects):
        vids = glob.glob(os.path.join(s["path"], "**", "*.mp4"), recursive=True)
        vids = [p for p in vids if "partial_movie_files" not in p]
        if vids:
            valid_sects += 1
            emit({"type": "section_update", "stage": 3, "section": n, "status": "done"})
        else:
            emit({"type": "section_update", "stage": 3, "section": n, "status": "error"})

    if valid_sects < max(1, len(sects) // 2):
        emit({"type": "error", "message": "Video generation failed for majority of sections."})
        sys.exit(1)

    emit({"type": "stage", "stage": 3, "status": "done"})

    out_file = Mergevidsandvoice(sects, title)
    if not out_file or not os.path.exists(out_file):
        out_file = os.path.join(BASEPATH_M, "output", "out", "Out.mp4")

    code_all = None
    if inc_code:
        codes = []
        for sect in sects:
            p = os.path.join(sect.get("path", ""), "ManimC.py")
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    codes.append(f"# Section {sect.get('section_number')}: {sect.get('topic')}\n" + f.read())
        code_all = "\n\n".join(codes)

    emit({
        "type": "complete",
        "video_path": os.path.abspath(out_file),
        "code": code_all,
        "message": "Video generated and merged successfully!!"
    })

if __name__ == "__main__":
    main()
