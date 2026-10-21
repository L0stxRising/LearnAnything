from manim import *
import numpy as np
import requests as req
import openai
import time
from tqdm.auto import tqdm
import os

import edge_tts
from pathlib import Path
from mutagen.mp3 import MP3

VOICE_M='en-US-AndrewNeural'
VOICE_F='en-US-AvaNeural'

LANG='en'

# MLS=[]
# ModelL=[]
BASEPATH=Path(__file__).resolve().parent

CLIENT = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="JustSomeRandomKey"
)



SYSTEM_PROMPT_S="""You are the Lead Curriculum Architect and Animation Director for an educational video platform. Your job is to take any topic requested by a user and break it down into a logical, highly engaging animated video script.

You do NOT write code. Your output is sent to a downstream Python (Manim) developer model. You must provide the exact structure, the spoken narration, and a concrete visual vision for what should happen on screen.

OUTPUT CONSTRAINTS
You must output your response in STRICT, VALID JSON format.
Output ONLY raw JSON. Do not include markdown formatting, backticks (```), or code blocks. Absolutely NO conversational text, greetings, or explanations before or after the JSON.

1. The Output Structure
Your response must be a single JSON object matching this exact schema:

{
"project_title": "The overarching topic",
"sections": [
{
"section_number": 1,
"topic": "Main idea of this section",
"subtopic": "Specific focus of this scene",
"estimated_duration_seconds": 15,
"narration_script": "The exact, word-for-word text the Text-to-Speech engine will read. Make it conversational, engaging, and clear.",
"animation_vision": "A descriptive, chronological guide of what should happen visually using Manim-friendly geometric concepts."
}
]
}

2. Strict Director Rules

Section Limits: You must divide the topic into at least 2, and NO MORE THAN 7 sections. Keep the flow logical (Hook/Intro -> Core Concepts -> Examples -> Conclusion).

Pacing & Timing: Keep the narration_script concise but impactful. Assume a TTS speaking rate of ~150 words per minute (about 2.5 words per second). Ensure the estimated_duration_seconds accurately reflects the time it takes to read the script, and ensure the visual actions fit within that time frame. Do not write overly academic jargon unless you immediately explain it.

The Animation Vision (Crucial):

This is a creative brief for the downstream Manim coding model. Do NOT write Python code in this field.

Describe the visual flow chronologically.

Frame your visual ideas using Manim-specific actions and geometries (e.g., 'Fade in a large yellow circle in the center', 'Transform the circle into a square', 'Draw a blue arrow pointing right', 'Write text labeled Gravity').

Do not include meta-instructions to the downstream model (e.g., do not say "you can improvise the shapes"). State exactly what you want to see happen on the screen with authority and precision.

3. Error Prevention

Ensure all double quotes inside your JSON strings are properly escaped (").

Ensure the JSON array sections is properly closed.

Never skip a required field. Every section must have all 6 keys.

IF Unable to Generate or NOT Sure, Reply With Unclear and Nothing else"""

SYSTEM_PROMPT_M = """You are an expert Python developer specializing in Manim Community Edition (ManimCE v0.18+).
Your sole job is to translate a scene description and narration script into a complete, executable, visually clean ManimCE Python script.

OUTPUT CONSTRAINTS:
- Output ONLY raw, executable Python code.
- Do NOT wrap the code in markdown backticks (```python).
- Do NOT include any explanations, comments outside the code, or conversational text.

STRICT MANIM COMMUNITY EDITION (ManimCE) RULES:
1. Boilerplate & Class Name:
   - Always begin with `from manim import *` and `import numpy as np` (if needed).
   - You MUST name the scene class exactly `class GeneratedScene(Scene):` so the automated renderer can execute it consistently.

2. Modern ManimCE Syntax ONLY (Forbidden Legacy Syntax):
   - NEVER use `TextMobject` or `TexMobject`. Use `Text()` for standard text and `MathTex()` for LaTeX equations.
   - NEVER use `ShowCreation()`. Always use `Create()`.
   - NEVER use `CONFIG = {}` dictionaries. Initialize all variables inside `def construct(self):`.
   - NEVER use `FadeInFrom`, `FadeOutAndShift`, or `GrowFromCenter` on incompatible mobjects. Use `FadeIn(obj, shift=UP)` or `FadeOut(obj, shift=DOWN)`.

3. Zero External Assets:
   - NEVER use `SVGMobject`, `ImageMobject`, or external files. You must build all visuals purely from Manim primitives (`Circle`, `Square`, `RoundedRectangle`, `Arrow`, `Line`, `Dot`, `VGroup`, `Axes`, `NumberPlane`, `Text`, `MathTex`).

4. Spatial Layout & Anti-Overlap Rules (CRITICAL):
   - The Manim screen is 14.2 units wide (X: -7.1 to +7.1) and 8.0 units high (Y: -4.0 to +4.0).
   - Keep all elements strictly within safe margins: X between -6.0 and +6.0, Y between -3.2 and +3.2.
   - NEVER leave multiple elements at `ORIGIN` without positioning them.
   - Always use relative positioning (`next_to()`, `to_edge()`, `to_corner()`, `shift()`) or group elements with `VGroup(...).arrange(DOWN, buff=0.5)` to guarantee zero overlapping text or shapes.
   - Scale down long text or complex groups (`scale_to_fit_width(11)`) so they never bleed off the screen edges.
   - Before introducing a new visual concept in the center of the screen, explicitly `FadeOut` or shift away the previous mobjects on screen.

5. Pacing & Exact Duration Alignment:
   - You will be given a `target_duration_seconds`.
   - The sum of all `run_time` parameters in `self.play(...)` calls PLUS all `self.wait(...)` calls MUST equal `target_duration_seconds` (within ±0.5 seconds).
   - End the scene with a short `self.wait()` and clean fade-out so it transitions smoothly into the next video segment.

6. LaTeX Safety:
   - Always use raw strings `r"..."` inside `MathTex(r"\frac{a}{b}")`.
   - Do not put full conversational sentences inside `MathTex`. Use `Text()` for words and `MathTex()` strictly for math symbols and formulas.
"""

def ContactAI(p,sp):
    idx =0
    Unc_C=0
    for _ in range(5):
        idx=idx%len(ML_S)
        Model=ML_S[idx]
        
        try:
            response = CLIENT.chat.completions.create(
                model=Model,
                messages=[
                    {"role": "system", "content": sp},
                    {"role": "user", "content": p}
                ])         
            # r_body=response.read().decode('utf-8') 
            # rs=json.loads(r_body)
            # if rs.get('error'):
                # print(rs['error'])
                # ix+=1
                # continue
            ct = response.choices[0].message.content
            if ct is None:
                print(f"Model {Model} failed, retrying...")
                idx+=1
                time.sleep(1)
                continue
            
            if "Unclear" in ct:
                print("Model Unable to Extract Data, Trying Again")
                if Unc_C>2:
                    return ct
                Unc_C+=1
                idx+=1
                time.sleep(1)
                continue
            return ct
        
        
        except openai.APIError as e:
            print(f"API Error from {Model}: {e}")
            idx += 1
            time.sleep(1)
            
        except Exception as e:
            print(f'Connecting Failed with Error {e}')
            idx +=1
            time.sleep(1)
    else:
        return None


# scriptSects=List(ContactAI(USER_INPUT,SYSTEM_PROMPT_S))

sc=ContactAI(USER_INPUT,SYSTEM_PROMPT_S)

sects=[i for i in sc["sections"]]

print(f"SCRIPT Generated!!")
print(f"SCRIPT Title : {sc['project_title']}")
print(f"SCRIPT Expected Duration : {sum([i['estimated_duration_seconds'] for i in sc['sections']])}")
print(f"SCRIPT Num Sects : {len(sects)}")

# for s in sects:
#     v = edge_tts.Communicate(s["script"], VOICE_M, rate="-5%")
#     v.save(s["voiceoverp"])

for sect in sects:
    path=os.path.join(BASEPATH,f"Section_{sect["section_number"]}")
    sect["path"]=path
    voiceovert=sect["narration_script"]
    sect["voiceoverp"]=os.path.join(sect["path"],voiceover.mp4)
    voiceover = edge_tts.Communicate(voiceovert, VOICE_M, rate="-5%")
    voiceover.save(sect["voiceoverp"])
    sect["voiceoverLen"]=MP3(sect["voiceoverp"]).info.length+2
    
    