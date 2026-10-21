import re
from typing import Callable, List, Optional, Tuple


def _split_top_level_args(arg_str: str) -> List[str]:
    """Splits a function call's argument string by top-level commas only."""
    args = []
    current = []
    depth = 0
    for ch in arg_str:
        if ch in "([{":
            depth += 1
            current.append(ch)
        elif ch in ")]}":
            depth = max(0, depth - 1)
            current.append(ch)
        elif ch == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if "".join(current).strip():
        args.append("".join(current).strip())
    return args


def _rewrite_call(
    code: str,
    func_name: str,
    transform_fn: Callable[[List[str]], Optional[str]],
    log: List[str],
    description: str,
    verbose: bool,
) -> str:
    """
    Finds calls to `func_name(...)` handling arbitrary nested parentheses
    and rewrites them using `transform_fn(parsed_args)`.
    """
    pattern = re.compile(rf"\b{re.escape(func_name)}\s*\(")
    pos = 0
    out = []
    changed = False

    while True:
        match = pattern.search(code, pos)
        if not match:
            out.append(code[pos:])
            break

        # Ensure it's not a method definition `def func_name(`
        prefix = code[max(0, match.start() - 10):match.start()]
        if re.search(r"\bdef\s+$", prefix):
            out.append(code[pos:match.end()])
            pos = match.end()
            continue

        out.append(code[pos:match.start()])
        open_paren_idx = match.end() - 1

        # Scan forward for matching closing parenthesis
        depth = 0
        end_idx = -1
        for i in range(open_paren_idx, len(code)):
            ch = code[i]
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
                if depth == 0:
                    end_idx = i
                    break

        if end_idx == -1:
            # Unbalanced parens in source; leave untouched
            out.append(code[match.start():])
            break

        inner_args_str = code[open_paren_idx + 1:end_idx]
        parsed_args = _split_top_level_args(inner_args_str)
        replacement = transform_fn(parsed_args)

        if replacement is not None:
            out.append(replacement)
            changed = True
        else:
            out.append(code[match.start():end_idx + 1])

        pos = end_idx + 1

    if verbose and changed:
        log.append(f"  [FIX] {description}")

    return "".join(out)


def fix_manim_code(code: str, verbose: bool = False) -> str:
    """
    Fixes outdated ManimGL / 3b1b Manim code and common LLM hallucinations
    to work with Manim Community Edition (Manim CE v0.18+).
    """
    log: List[str] = []

    def _replace(pattern: str, replacement, source: str,
                 description: str = "", flags: int = 0) -> str:
        new_source = re.sub(pattern, replacement, source, flags=flags)
        if verbose and new_source != source:
            log.append(f"  [FIX] {description or pattern}")
        return new_source

    # =========================================================================
    # 0. STRIP LLM MARKDOWN CODE FENCES FIRST
    # =========================================================================
    code = _replace(
        r"^\s*```(?:python|py)?\s*\n",
        "",
        code, "Strip opening markdown fence"
    )
    code = _replace(
        r"\n\s*```\s*$",
        "",
        code, "Strip closing markdown fence"
    )

    # =========================================================================
    # 0.5 PROTECT STRING LITERALS FROM ACCIDENTAL REGEX CORRUPTION
    # =========================================================================
    protected_strings: List[str] = []

    def _mask_strings(match):
        idx = len(protected_strings)
        protected_strings.append(match.group(0))
        return f"__MANIM_STR_{idx}__"

    string_pattern = (
        r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\''
        r'|r?"(?:\\.|[^"\\])*"|r?\'(?:\\.|[^\'\\])*\')'
    )
    code = re.sub(string_pattern, _mask_strings, code)

    # =========================================================================
    # 1. IMPORT FIXES
    # =========================================================================
    code = _replace(
        r"from\s+manimlib\.imports\s+import\s+\*",
        "from manim import *",
        code, "manimlib.imports → manim"
    )
    code = _replace(
        r"from\s+big_ol_pile_of_manim_imports\s+import\s+\*",
        "from manim import *",
        code, "big_ol_pile_of_manim_imports → manim"
    )
    code = _replace(
        r"from\s+manimlib\.scene\.scene\s+import\s+Scene",
        "from manim import Scene",
        code, "manimlib.scene.scene → manim"
    )
    code = _replace(
        r"from\s+manimlib\.([a-zA-Z_.]+)\s+import\s+([^\n]+)",
        "from manim import *",
        code, "manimlib.* submodule → from manim import *"
    )
    code = _replace(
        r"from\s+manimlib\b",
        "from manim",
        code, "manimlib → manim"
    )
    code = _replace(
        r"import\s+manimlib\b",
        "import manim",
        code, "import manimlib → import manim"
    )

    # =========================================================================
    # 2. BALANCED-PAREN CALL REWRITES (Handles arbitrary nested parens & kwargs)
    # =========================================================================

    # FadeInFromDown(mob, **kwargs) → FadeIn(mob, shift=DOWN, **kwargs)
    code = _rewrite_call(
        code, "FadeInFromDown",
        lambda args: f"FadeIn({args[0]}, shift=DOWN" + (f", {', '.join(args[1:])})" if len(args) > 1 else ")") if args else None,
        log, "FadeInFromDown → FadeIn(..., shift=DOWN)", verbose
    )

    # FadeInFromUp(mob, **kwargs) → FadeIn(mob, shift=UP, **kwargs)
    code = _rewrite_call(
        code, "FadeInFromUp",
        lambda args: f"FadeIn({args[0]}, shift=UP" + (f", {', '.join(args[1:])})" if len(args) > 1 else ")") if args else None,
        log, "FadeInFromUp → FadeIn(..., shift=UP)", verbose
    )

    # FadeInFrom(mob, dir, **kwargs) → FadeIn(mob, shift=dir, **kwargs)
    def _fix_fade_in_from(args: List[str]) -> Optional[str]:
        if len(args) < 2:
            return f"FadeIn({', '.join(args)})"
        mob = args[0]
        direction = re.sub(r"^direction\s*=\s*", "", args[1])
        rest = f", {', '.join(args[2:])}" if len(args) > 2 else ""
        return f"FadeIn({mob}, shift={direction}{rest})"

    code = _rewrite_call(
        code, "FadeInFrom", _fix_fade_in_from,
        log, "FadeInFrom(mob, dir) → FadeIn(mob, shift=dir)", verbose
    )

    # FadeInFromLarge(mob, scale_factor=2, **kwargs) → FadeIn(mob, scale=..., **kwargs)
    def _fix_fade_in_large(args: List[str]) -> Optional[str]:
        if not args:
            return None
        mob = args[0]
        if len(args) == 1:
            return f"FadeIn({mob}, scale=2)"
        second = re.sub(r"^scale_factor\s*=\s*", "", args[1])
        rest = f", {', '.join(args[2:])}" if len(args) > 2 else ""
        return f"FadeIn({mob}, scale={second}{rest})"

    code = _rewrite_call(
        code, "FadeInFromLarge", _fix_fade_in_large,
        log, "FadeInFromLarge → FadeIn(..., scale=...)", verbose
    )

    # FadeInFromPoint(mob, point, **kwargs) → FadeIn(mob, target_position=point, **kwargs)
    def _fix_fade_in_point(args: List[str]) -> Optional[str]:
        if len(args) < 2:
            return f"FadeIn({', '.join(args)})"
        rest = f", {', '.join(args[2:])}" if len(args) > 2 else ""
        return f"FadeIn({args[0]}, target_position={args[1]}{rest})"

    code = _rewrite_call(
        code, "FadeInFromPoint", _fix_fade_in_point,
        log, "FadeInFromPoint → FadeIn(..., target_position=...)", verbose
    )

    # FadeOutAndShift(mob, dir, **kwargs) → FadeOut(mob, shift=dir, **kwargs)
    def _fix_fade_out_shift(args: List[str]) -> Optional[str]:
        if len(args) < 2:
            return f"FadeOut({', '.join(args)})"
        direction = re.sub(r"^direction\s*=\s*", "", args[1])
        rest = f", {', '.join(args[2:])}" if len(args) > 2 else ""
        return f"FadeOut({args[0]}, shift={direction}{rest})"

    code = _rewrite_call(
        code, "FadeOutAndShift", _fix_fade_out_shift,
        log, "FadeOutAndShift → FadeOut(..., shift=...)", verbose
    )

    # FadeOutAndShiftDown(mob, **kwargs) → FadeOut(mob, shift=DOWN, **kwargs)
    code = _rewrite_call(
        code, "FadeOutAndShiftDown",
        lambda args: f"FadeOut({args[0]}, shift=DOWN" + (f", {', '.join(args[1:])})" if len(args) > 1 else ")") if args else None,
        log, "FadeOutAndShiftDown → FadeOut(..., shift=DOWN)", verbose
    )

    # ChangingDecimal(mob, func, **kwargs) → UpdateFromAlphaFunc(mob, lambda _m, _a: _m.set_value((func)(_a)), **kwargs)
    def _fix_changing_decimal(args: List[str]) -> Optional[str]:
        if len(args) < 2:
            return None
        mob, func = args[0], args[1]
        rest = f", {', '.join(args[2:])}" if len(args) > 2 else ""
        return f"UpdateFromAlphaFunc({mob}, lambda _m, _a: _m.set_value(({func})(_a)){rest})"

    code = _rewrite_call(
        code, "ChangingDecimal", _fix_changing_decimal,
        log, "ChangingDecimal → UpdateFromAlphaFunc", verbose
    )

    # always_shift(mob, direction, rate) → mob.add_updater(...)
    def _fix_always_shift(args: List[str]) -> Optional[str]:
        if len(args) < 2:
            return None
        mob = args[0]
        direction = re.sub(r"^direction\s*=\s*", "", args[1])
        rate = re.sub(r"^rate\s*=\s*", "", args[2]) if len(args) > 2 else "1"
        return f"{mob}.add_updater(lambda m, dt: m.shift(({direction}) * ({rate}) * dt))"

    code = _rewrite_call(
        code, "always_shift", _fix_always_shift,
        log, "always_shift → .add_updater", verbose
    )

    # ApplyMethod(mob.method, *args) → mob.animate.method(*args) (when no extra anim kwargs)
    def _fix_apply_method(args: List[str]) -> Optional[str]:
        if not args or "." not in args[0]:
            return None
        # If animation kwargs like run_time= or rate_func= are passed inside ApplyMethod,
        # keep ApplyMethod as-is (ApplyMethod still exists in Manim CE!)
        for a in args[1:]:
            if re.match(r"^(run_time|rate_func|lag_ratio)\s*=", a):
                return None
        mob_method = args[0]
        dot_idx = mob_method.rfind(".")
        mob = mob_method[:dot_idx]
        method = mob_method[dot_idx + 1:]
        call_args = ", ".join(args[1:])
        return f"{mob}.animate.{method}({call_args})"

    code = _rewrite_call(
        code, "ApplyMethod", _fix_apply_method,
        log, "ApplyMethod → .animate", verbose
    )

    # =========================================================================
    # 3. CLASS / MOBJECT RENAMES
    #    (Note: AddTextLetterByLetter removed since it exists natively in CE)
    # =========================================================================
    class_renames = {
        "TextMobject": "Tex",
        "TexMobject": "MathTex",
        "RunningStart": "rush_into",
        "CheckeredCircle": "Circle",
        "GraphScene": "Scene",
        "ReconfigurableScene": "Scene",
        "SampleSpaceScene": "Scene",
        "ParametricSurface": "Surface",
        "ShowCreation": "Create",
        "UnCreate": "Uncreate",
        "ShowSubmobjectsOneByOne": "ShowIncreasingSubsets",
        "FadeInFromDown": "FadeIn",
        "FadeInFromUp": "FadeIn",
        "FadeInFromLarge": "FadeIn",
        "FadeInFrom": "FadeIn",
        "FadeOutAndShift": "FadeOut",
        "FadeOutAndShiftDown": "FadeOut",
        "FadeInFromPoint": "FadeIn",
        "MultiCamera": "Camera",
        "MappingCamera": "Camera",
        "BraceText": "BraceLabel",
        "CircleIndicate": "Circumscribe",
        "ShowCreationThenDestruction": "ShowPassingFlash",
        "ShowCreationThenDestructionAround": "ShowPassingFlash",
        "ShowCreationThenFadeAround": "ShowPassingFlash",
        "AnimationOnSurroundingRectangle": "Indicate",
        "ShowSurroundingRectangle": "ShowPassingFlash",
        "FlashyFadeIn": "FadeIn",
    }

    for old_name, new_name in class_renames.items():
        code = _replace(
            rf"\b{re.escape(old_name)}\b",
            new_name,
            code, f"class: {old_name} → {new_name}"
        )

    # =========================================================================
    # 4. METHOD CALLS WITH CHANGED SIGNATURES (Supports multi-arg & nested parens)
    # =========================================================================
    code = _replace(
        r"\.set_fill_opacity\s*\(\s*(?!opacity\s*=)",
        ".set_fill(opacity=",
        code, ".set_fill_opacity(...) → .set_fill(opacity=...)"
    )
    code = _replace(
        r"\.set_stroke_width\s*\(\s*(?!width\s*=)",
        ".set_stroke(width=",
        code, ".set_stroke_width(...) → .set_stroke(width=...)"
    )
    code = _replace(
        r"\.set_fill_color\s*\(\s*(?!color\s*=)",
        ".set_fill(color=",
        code, ".set_fill_color(...) → .set_fill(color=...)"
    )
    code = _replace(
        r"\.set_stroke_color\s*\(\s*(?!color\s*=)",
        ".set_stroke(color=",
        code, ".set_stroke_color(...) → .set_stroke(color=...)"
    )

    # .scale_about_point(factor, point) → .scale(factor, about_point=point)
    ARG_EXPR = r"(?:[^(),]|\([^()]*\))+"
    code = _replace(
        rf"\.scale_about_point\s*\(\s*({ARG_EXPR})\s*,\s*(?!about_point\s*=)({ARG_EXPR})\s*\)",
        r".scale(\1, about_point=\2)",
        code, ".scale_about_point(f, pt) → .scale(f, about_point=pt)"
    )

    # =========================================================================
    # 5. SIMPLE METHOD / PROPERTY RENAMES
    # =========================================================================
    method_renames = {
        ".get_center_of_mass": ".get_center",
        ".set_submobject_colors_by_gradient": ".set_color_by_gradient",
        ".family_members_with_points": ".get_family",
        ".get_points_defining_boundary": ".get_boundary_point",
        ".rotate_in_place": ".rotate",
        ".scale_in_place": ".scale",
        ".shift_onto_screen": ".shift",
        ".stretch_in_place": ".stretch",
        ".set_color_by_tex_to_color_map": ".set_color_by_tex",
        ".highlight": ".set_color",
        ".set_submobject_colors": ".set_color",
        ".wait_to": ".wait",
        ".get_graph": ".plot",
        ".get_vertical_line_to_graph": ".get_vertical_line",
        ".arrange_submobjects": ".arrange",
    }

    for old_method, new_method in method_renames.items():
        code = _replace(
            rf"{re.escape(old_method)}\b",
            new_method,
            code, f"method: {old_method} → {new_method}"
        )

    # =========================================================================
    # 6. PARAMETER / KEYWORD ARGUMENT & FRAME CONSTANT RENAMES
    # =========================================================================
    code = _replace(
        r"submobject_mode\s*=\s*__MANIM_STR_\d+__",
        "lag_ratio=0.5",
        code, "submobject_mode=... → lag_ratio=0.5"
    )
    code = _replace(
        r"\bFRAME_X_RADIUS\b",
        "(config.frame_width / 2)",
        code, "FRAME_X_RADIUS → (config.frame_width / 2)"
    )
    code = _replace(
        r"\bFRAME_Y_RADIUS\b",
        "(config.frame_height / 2)",
        code, "FRAME_Y_RADIUS → (config.frame_height / 2)"
    )
    code = _replace(
        r"\bFRAME_WIDTH\b",
        "config.frame_width",
        code, "FRAME_WIDTH → config.frame_width"
    )
    code = _replace(
        r"\bFRAME_HEIGHT\b",
        "config.frame_height",
        code, "FRAME_HEIGHT → config.frame_height"
    )
    code = _replace(
        r"\btext_to_color_map\b",
        "tex_to_color_map",
        code, "text_to_color_map → tex_to_color_map"
    )
    code = _replace(
        r"\brate_function\s*=",
        "rate_func=",
        code, "rate_function= → rate_func="
    )

    # =========================================================================
    # 7. COLOR & RATE FUNCTION RENAMES
    # =========================================================================
    color_renames = {
        "DARK_GREY": "DARK_GRAY",
        "LIGHT_GREY": "LIGHT_GRAY",
        "GREY": "GRAY",
        "GREY_A": "GRAY_A",
        "GREY_B": "GRAY_B",
        "GREY_C": "GRAY_C",
        "GREY_D": "GRAY_D",
        "GREY_E": "GRAY_E",
        "GREY_BROWN": "GRAY_BROWN",
    }
    for old_color, new_color in color_renames.items():
        code = _replace(
            rf"\b{re.escape(old_color)}\b",
            new_color,
            code, f"color: {old_color} → {new_color}"
        )

    rate_func_renames = {
        "running_start": "rush_from",
        "slow_into": "ease_in_sine",
        "slow_out": "ease_out_sine",
    }
    for old_rf, new_rf in rate_func_renames.items():
        code = _replace(
            rf"\b{re.escape(old_rf)}\b",
            new_rf,
            code, f"rate_func: {old_rf} → {new_rf}"
        )

    # =========================================================================
    # 8. INDENT-SAFE GRAPHSCENE → AXES MIGRATION (With fallback initialization)
    # =========================================================================
    code = _replace(
        r"^([ \t]*)self\.setup_axes\s*\(\s*animate\s*=\s*True\s*\)",
        r"\1self.axes = Axes()\n\1self.play(Create(self.axes))",
        code, "setup_axes(animate=True) → self.axes = Axes() (indent-safe)",
        flags=re.MULTILINE
    )
    code = _replace(
        r"^([ \t]*)self\.setup_axes\s*\([^)]*\)",
        r"\1self.axes = Axes()\n\1self.add(self.axes)",
        code, "setup_axes() → self.axes = Axes() (indent-safe)",
        flags=re.MULTILINE
    )

    for graph_method in [
        "plot", "get_graph_label", "coords_to_point", "point_to_coords",
        "get_vertical_line", "get_area", "input_to_graph_point",
        "get_riemann_rectangles"
    ]:
        code = _replace(
            rf"self\.{graph_method}\s*\(",
            f"self.axes.{graph_method}(",
            code, f"self.{graph_method} → self.axes.{graph_method}"
        )

    # If self.axes is used (e.g. from self.plot) without setup_axes ever being called,
    # initialize self.axes = Axes() at the top of construct(self):
    if "self.axes." in code and "self.axes =" not in code and "self.axes=" not in code:
        code = _replace(
            r"(def\s+construct\s*\(\s*self\s*\)\s*:\s*\n)([ \t]+)",
            r"\1\2self.axes = Axes()\n\2",
            code, "Inject fallback self.axes = Axes() in construct()"
        )

    # =========================================================================
    # 9. CAMERA & PLAY KWARG FIXES
    # =========================================================================
    code = _replace(
        r"self\.camera_frame\b",
        "self.camera.frame",
        code, "self.camera_frame → self.camera.frame"
    )
    code = _replace(
        r",\s*added_anims\s*=\s*\[([^\]]*)\]",
        r", \1",
        code, "added_anims=[...] → inline anims"
    )

    # =========================================================================
    # 10. AXES / NUMBERLINE / SURFACE RANGE FIXES
    # =========================================================================
    code = _replace(
        r"NumberLine\s*\(\s*x_min\s*=\s*(-?[\d.]+)\s*,\s*x_max\s*=\s*(-?[\d.]+)",
        r"NumberLine(x_range=[\1, \2, 1]",
        code, "NumberLine(x_min, x_max) → NumberLine(x_range=[])"
    )
    code = _replace(
        r"(Axes|NumberPlane)\s*\(\s*x_min\s*=\s*(-?[\d.]+)\s*,\s*x_max\s*=\s*(-?[\d.]+)\s*,\s*y_min\s*=\s*(-?[\d.]+)\s*,\s*y_max\s*=\s*(-?[\d.]+)",
        r"\1(x_range=[\2, \3, 1], y_range=[\4, \5, 1]",
        code, "Axes/NumberPlane(x_min...) → (x_range=...)"
    )
    code = _replace(
        r"Surface\s*\(([^)]*?)u_min\s*=\s*(-?[\d.]+)\s*,\s*u_max\s*=\s*(-?[\d.]+)\s*,\s*v_min\s*=\s*(-?[\d.]+)\s*,\s*v_max\s*=\s*(-?[\d.]+)",
        r"Surface(\1u_range=[\2, \3], v_range=[\4, \5]",
        code, "Surface u_min/v_min → u_range/v_range"
    )

    # =========================================================================
    # 11. CORNER / EDGE CONSTANTS (Allows `== TOP`, blocks `TOP = ...`)
    # =========================================================================
    code = _replace(
        r"\bTOP\b(?!\s*=[^=])",
        "(UP * config.frame_height / 2)",
        code, "TOP → (UP * config.frame_height / 2)"
    )
    code = _replace(
        r"\bBOTTOM\b(?!\s*=[^=])",
        "(DOWN * config.frame_height / 2)",
        code, "BOTTOM → (DOWN * config.frame_height / 2)"
    )
    code = _replace(
        r"\bLEFT_SIDE\b(?!\s*=[^=])",
        "(LEFT * config.frame_width / 2)",
        code, "LEFT_SIDE → (LEFT * config.frame_width / 2)"
    )
    code = _replace(
        r"\bRIGHT_SIDE\b(?!\s*=[^=])",
        "(RIGHT * config.frame_width / 2)",
        code, "RIGHT_SIDE → (RIGHT * config.frame_width / 2)"
    )

    # =========================================================================
    # 12. DIGEST_CONFIG CLEANUP
    # =========================================================================
    code = _replace(
        r"digest_config\s*\(\s*self\s*,?\s*\w*\s*\)",
        "pass  # digest_config removed in CE",
        code, "digest_config → pass"
    )
    code = _replace(
        r"digest_locals\s*\(\s*self\s*\)",
        "pass  # digest_locals removed in CE",
        code, "digest_locals → pass"
    )

    # =========================================================================
    # 13. RESTORE PROTECTED STRING LITERALS
    # =========================================================================
    def _unmask_strings(match):
        idx = int(match.group(1))
        return protected_strings[idx]

    code = re.sub(r"__MANIM_STR_(\d+)__", _unmask_strings, code)

    # =========================================================================
    # 14. FINAL IMPORT CLEANUP (Always ensure `from manim import *` is present)
    # =========================================================================
    if not re.search(r"^\s*from\s+manim\s+import\s+\*", code, flags=re.MULTILINE):
        code = "from manim import *\n\n" + code

    lines = code.split("\n")
    seen_imports = set()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("from manim import", "import manim")):
            if stripped not in seen_imports:
                seen_imports.add(stripped)
                new_lines.append(line)
        else:
            new_lines.append(line)
    code = "\n".join(new_lines)

    if verbose:
        if log:
            print(f"Manim Code Fixer: {len(log)} fixes applied:")
            for entry in log:
                print(entry)
        else:
            print("Manim Code Fixer: No changes needed.")

    return code


def fix_and_validate(code: str, verbose: bool = False) -> Tuple[str, Optional[str]]:
    fixed = fix_manim_code(code, verbose=verbose)
    try:
        compile(fixed, "<manim_scene>", "exec")
        return fixed, None
    except SyntaxError as e:
        return fixed, f"SyntaxError at line {e.lineno}: {e.msg} -> {e.text}"