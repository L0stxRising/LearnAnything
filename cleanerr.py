import re

def cleanerr(text: str) -> str:
    lines=[line.strip() for line in text.strip().splitlines() if line.strip()]
    
    if not lines:
        return ""
    
    if len(lines)==1:
        return lines[0]
    
    frame_pattern = re.compile(r'(?:File\s+["\']?([^"\'>]+?\.py)["\']?,\s+line\s+\d+|(\S+\.py):\d+)')
    

    ignored_segments=(
        "site-packages",
        ".venv",
        "/venv/",
        "\\venv\\",
        "/manim/",
        "\\manim\\",
        "<frozen ",
        "importlib")

    error=lines[-1]
    user_frame=None

    for line in reversed(lines[:-1]):
        match=frame_pattern.search(line)
        if match:
            filepath=match.group(1) or match.group(2)
            if not any(ign in filepath for ign in ignored_segments):
                user_frame=line
                break

    if not user_frame:
        user_frame=lines[-2]

    return f"{user_frame}\n{error}"