import re

R = [
    (r"```(?:python)?", ""),
    (r"```", ""),
    (r"\bTextMobject\b", "Text"),
    (r"\bTexMobject\b", "MathTex"),
    (r"\bShowCreation\b", "Create"),
    (r"\bFadeInFrom(?:Down|Large)?\b", "FadeIn"),
    (r"\bFadeOutAndShift\b", "FadeOut"),
    (r"\bGrowFromCenter\b", "FadeIn"),
    (r"\.get_graph\b", ".plot"),
]

def fix_manim_code(code: str, verbose=False) -> str:
    if not code:
        return ""
    
    for pat, rep in R:
        code = re.sub(pat, rep, code)
    
    if "from manim import *" not in code:
        code = "from manim import *\n" + code.lstrip()
    return code.strip()

def fix_and_validate(code: str, verbose=False):
    c = fix_manim_code(code)
    try:
        compile(c, "<manim_scene>", "exec")
        return c, None
    
    except SyntaxError as e:
        return c, f"SyntaxError line {e.lineno}: {e.msg}"
