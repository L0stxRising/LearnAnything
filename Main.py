# %%
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
import random
import string
import asyncio

import json
import moviepy
import sys
import ffmpeg

import shutil
from concurrent.futures import ThreadPoolExecutor

# %%
from SYSTEM_PROMPT_H import *
from SYSTEM_PROMPT_S import *
from SYSTEM_PROMPT_M import *

from cleanerr import *

# %%
cleanerr('''(.venv) l0stsky@L0stxRising:~/ExTraStuff/Competitions/LearnAnything$ manim -ql -v ERROR /home/l0stsky/ExTraStuff/Competitions/LearnAnything/temp/Section_2/ManimC.py
Manim Community v0.22.0

╭─────────────────────────────── Traceback (most recent call last) ────────────────────────────────╮                                                                                                              
│ /home/l0stsky/ExTraStuff/Competitions/LearnAnything/.venv/lib/python3.12/site-packages/manim/cli │
│ /render/commands.py:122 in render                                                                │
│                                                                                                  │
│   119 │   │   │   │   │   scene = SceneClass()                                                   │
│   120 │   │   │   │   │   # Attach explicitly, but preserve custom Scene.render overrides.       │
│   121 │   │   │   │   │   Manager(scene)                                                         │
│ ❱ 122 │   │   │   │   │   scene.render()                                                         │
│   123 │   except Exception:                                                                      │
│   124 │   │   error_console.print_exception()                                                    │
│   125 │   │   sys.exit(1)                                                                        │
│                                                                                                  │
│ /home/l0stsky/ExTraStuff/Competitions/LearnAnything/.venv/lib/python3.12/site-packages/manim/sce │
│ ne/scene.py:320 in render                                                                        │
│                                                                                                  │
│    317 │   │   bool                                                                              │
│    318 │   │   │   Whether an interactive rerun was requested.                                   │
│    319 │   │   """                                                                               │
│ ❱  320 │   │   return self._get_manager().render(preview)                                        │
│    321 │                                                                                         │
│    322 │   def _get_manager(self) -> Manager[Self]:                                              │
│    323 │   │   """Return this scene's manager, creating it for legacy entry points."""           │
│                                                                                                  │
│ /home/l0stsky/ExTraStuff/Competitions/LearnAnything/.venv/lib/python3.12/site-packages/manim/man │
│ ager.py:155 in render                                                                            │
│                                                                                                  │
│   152 │   │                                                                                      │
│   153 │   │   self.setup()                                                                       │
│   154 │   │   try:                                                                               │
│ ❱ 155 │   │   │   self.construct()                                                               │
│   156 │   │   except EndSceneEarlyException:                                                     │
│   157 │   │   │   # Reaching the configured animation boundary ends the scene normally.          │
│   158 │   │   │   pass                                                                           │
│                                                                                                  │
│ /home/l0stsky/ExTraStuff/Competitions/LearnAnything/.venv/lib/python3.12/site-packages/manim/man │
│ ager.py:193 in construct                                                                         │
│                                                                                                  │
│   190 │                                                                                          │
│   191 │   def construct(self) -> None:                                                           │
│   192 │   │   """Run the managed scene's :meth:`~manim.scene.scene.Scene.construct` hook."""     │
│ ❱ 193 │   │   self.scene.construct()                                                             │
│   194 │                                                                                          │
│   195 │   def post_construct(self) -> None:                                                      │
│   196 │   │   """Finalize output after scene construction and tear-down.                         │
│                                                                                                  │
│ /home/l0stsky/ExTraStuff/Competitions/LearnAnything/temp/Section_2/ManimC.py:53 in construct     │
│                                                                                                  │
│    50 │   │   pred_dot = always_redraw(                                                          │
│    51 │   │   │   lambda: Dot(axes.c2p(pred_x.get_value(), 0), color=RED)                        │
│    52 │   │   )                                                                                  │
│ ❱  53 │   │   pred_line = always_redraw(                                                         │
│    54 │   │   │   lambda: axes.get_vertical_line(                                                │
│    55 │   │   │   │   axes.c2p(pred_x.get_value(), 0),                                           │
│    56 │   │   │   │   axes.c2p(pred_x.get_value(),                                               │
│                                                                                                  │
│ /home/l0stsky/ExTraStuff/Competitions/LearnAnything/.venv/lib/python3.12/site-packages/manim/ani │
│ mation/updaters/mobject_update_utils.py:107 in always_redraw                                     │
│                                                                                                  │
│   104 │   │   │   │   self.add(ax, sine, point, tangent)                                         │
│   105 │   │   │   │   self.play(alpha.animate.set_value(1), rate_func=linear, run_time=2)        │
│   106 │   """                                                                                    │
│ ❱ 107 │   mob = func()                                                                           │
│   108 │   mob.add_updater(lambda _: mob.become(func()))                                          │
│   109 │   return mob                                                                             │
│   110                                                                                            │
│                                                                                                  │
│ /home/l0stsky/ExTraStuff/Competitions/LearnAnything/temp/Section_2/ManimC.py:54 in <lambda>      │
│                                                                                                  │
│    51 │   │   │   lambda: Dot(axes.c2p(pred_x.get_value(), 0), color=RED)                        │
│    52 │   │   )                                                                                  │
│    53 │   │   pred_line = always_redraw(                                                         │
│ ❱  54 │   │   │   lambda: axes.get_vertical_line(                                                │
│    55 │   │   │   │   axes.c2p(pred_x.get_value(), 0),                                           │
│    56 │   │   │   │   axes.c2p(pred_x.get_value(),                                               │
│    57 │   │   │   │   np.exp(-pred_x.get_value()**2 / (2 * sigma**2)) / (sigma * np.sqrt(2 * n   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
TypeError: CoordinateSystem.get_vertical_line() takes 2 positional arguments but 3 were given''')

# %%
VOICE_M='en-US-AndrewNeural'
VOICE_F='en-US-AvaNeural'

LANG='en'
TRIES=3

# %%
BASEPATH_M=str(Path.cwd())
BASEPATH=os.path.join(BASEPATH_M,"temp")

# %%
ML_S=["google/gemma-4-31b-it:free","nvidia/nemotron-3-ultra-550b-a55b:free"]

# %%
CLIENT = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="smth"
)


# %%
def ContactAI(p,sp,give_j=True,img=None):
    idx =0
    Unc_C=0
    for _ in range(TRIES):
        idx=idx%len(ML_S)
        Model=ML_S[idx]
        
        try:
            if Unc_C>3:
                print("Model Not Reachable try again!")
                sys.exit()
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
            print(f"Response for Model {ct}")
            if ct is None:
                print(f"Model {Model} failed, retrying...")
                idx+=1
                time.sleep(1)
                continue
            
            ct = re.sub(r"^```(?:json)?\s*|\s*```$", "", ct.strip(), flags=re.MULTILINE)
            if give_j:
                try:
                    ct = json.loads(ct)
                except:
                    print("Model Data Curropted, Trying again")
                    idx+=1
                    time.sleep(1)
                    continue
                
                if ct.get("error",None)=="unclear":
                    print("Model Not Able to Perform Action, Trying Again!")
                    idx+=1
                    Unc_C+=1
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


# %% [markdown]
# # Layer 1 : Scripter Model

# %%
def scrptGen(USER_INPUT):
    data=ContactAI(USER_INPUT,SYSTEM_PROMPT_S)
    if not data:
        print("Unable to contact Model, try again!")
        sys.exit()
    print(f"Output {data}")
    # try:
    #     data = json.loads(c)
    # except:
    #     print("Model Data Curropted, Try Again Later!")
    #     sys.exit()
    
    # if data.get("error")=="unclear":
    #     print("Model Not Able to Perform Action, Try Again Later!")
    #     sys.exit()
        
    sects=data.get("sections", [])
    if not len(sects)>=1:
        print("Model Error, Try again Later")
        sys.exit()
    title = data.get("project_title", "Untitled Project")
    dur=sum([i.get("estimated_duration_seconds",0) for i in sects])
    
    
    print(f"SCRIPT Generated!!")
    print(f"SCRIPT Title : {title}")
    print(f"SCRIPT Expected Duration : {dur}")
    print(f"SCRIPT Num Sects : {len(sects)}")
    
    
    sects.sort(key=lambda i : i["section_number"])
    return sects, title

# %% [markdown]
# # Layer 2 : Generating VoiceOVER Code

# %%
def voice(sect,n):
    path=os.path.join(BASEPATH,f"Section_{n}")
    os.makedirs(path, exist_ok=True)
    sect["path"]=path
    voiceovert=sect["narration_script"]
    sect["voiceoverp"]=os.path.join(sect["path"],"voiceover.mp3")
    voiceover = edge_tts.Communicate(voiceovert, VOICE_M, rate="-5%")
    asyncio.run(voiceover.save(sect["voiceoverp"]))
    sect["voiceoverLen"]=MP3(sect["voiceoverp"]).info.length+2

# %% [markdown]
# # Layer 3 : Generating MANIN Code

# %%
from fixManim import *
# import sys
import subprocess

# %%
# def Healer(Code, Model, Tries):
#     prompt=f"This the CODE for a Animation made in MANIMCE, it has the following errors {err}, Fix it"

# %%
def runM(Code, sect, n):
    path=os.path.join(sect["path"],"ManimC.py")
    
    Code=Code[0] if isinstance(Code,list) else Code
    p=os.path.join(sect["path"])
    with open(path, "w") as f:
        f.write(Code)
    bin=shutil.which("manim") or "manim"
    cmd=[bin,"-ql","-v","ERROR","--media_dir",p,"-o",f"Section_{n}.mp4",path]
    try:
        out=subprocess.run(cmd,cwd=p,env=os.environ.copy(), capture_output=True, text=True, check=True)
        return None
    except subprocess.CalledProcessError as e:
        errl=[]
        errw=(e.stderr or "")+"\n"+(e.stdout or "")
        summ = cleanerr(errw)
        return errw

# %%
def Heal(Code, sect, pr, n, err, L=0):
    if L>1:
        print(f"The Code Cannot be Healed, Skipping section {n}")
        return 1
    print(f"Healing section {n}, Try : {L+1}")
    
    # TODO : the Err log is huge so idk strip it or smth => done
    prN=pr+ f"""
    - Animation Code Failed: 
    ```python
    {Code}
    ```
    - Animation Error: 
    ```text
    {err}
    ```
    """
    ManimCode=ContactAI(prN,SYSTEM_PROMPT_H,False)
    if not ManimCode:
        err="None"
        return Heal(ManimCode, sect, pr, n, err, L+1)
    ManimCode,err=fix_and_validate(ManimCode)
    out=runM(ManimCode,sect,n)
    if out==None:
        print(f"Render Done for Section {n}")
        return 0
    else:
        err=out
        return Heal(ManimCode, sect, pr, n, err, L+1)

# %%
def RenderVid(section, n):
    prompt = f"""
    Render the following scene in ManimCE (AVOID USING MANIMGL):
    - Topic: {section['topic']} ({section['subtopic']})
    - Target Duration: {section['voiceoverLen']} seconds
    - Narration Script (for pacing): "{section['narration_script']}"
    - Animation Vision: "{section['animation_vision']}"
    """
    ManimCodeN=ContactAI(prompt,SYSTEM_PROMPT_M,False)
    if not ManimCodeN:
        print(f"Model Failed Section {n}, Skipping....")
        return None
    ManimCode,err=fix_and_validate(ManimCodeN)
    if not isinstance(ManimCode,str):
        ManimCode=ManimCodeN
    out=runM(ManimCode,section,n)
    
    if out==None:
        print(f"Render Done for Section {n}")
    else:
        print(f"Error Running Section {n} Code with err : {out}")
        Heal(ManimCode,section,prompt,n,out)

# %%
def Mergevidsandvoice(sects, title):
    outp = os.path.join(BASEPATH_M, "output", "out")
    os.makedirs(outp, exist_ok=True)
    clean_title = re.sub(r'[\\/*?:"<>|]', "", title or "Out").strip() or "Out"
    out_file = os.path.join(outp, f"{clean_title}.mp4")

    streams = []
    segment_count = 0

    for sect in sects:
        pathl = glob.glob(os.path.join(sect["path"], "**", "*.mp4"), recursive=True)
        pathl = [p for p in pathl if "partial_movie_files" not in p]
        ap = sect.get("voiceoverp") or os.path.join(sect["path"], "voiceover.mp3")

        if not pathl or not os.path.exists(ap):
            continue

        vp = pathl[0]

        a_probe = ffmpeg.probe(ap)
        a_duration = float(a_probe["format"]["duration"])

        v_stream = (ffmpeg.input(vp).filter("scale", 854, 480, force_original_aspect_ratio="decrease").filter("pad", 854, 480, -1, -1, color="black").filter("fps", fps=15, round="up").filter("trim", duration=a_duration).filter("setpts", "PTS-STARTPTS"))

        a_stream = (ffmpeg.input(ap).filter("atrim", duration=a_duration).filter("asetpts", "PTS-STARTPTS"))

        streams.extend([v_stream, a_stream])
        segment_count += 1

    if segment_count == 0:
        print("No valid video/audio streams found to merge")
        return

    joined = ffmpeg.concat(*streams, v=1, a=1, n=segment_count).node

    out = ffmpeg.output(joined[0],joined[1],out_file,vcodec="libx264",acodec="aac",pix_fmt="yuv420p")
    ffmpeg.run(out, overwrite_output=True, quiet=False)
    print("Videos and Voice Merged Successfully!!")
    return out_file

# %%
import glob
import threading
def Main(USER_INPUT):
    sects,title=scrptGen(USER_INPUT)
    print("Script Made!!")
    ths=[]
    for n,sect in enumerate(sects):
        t=threading.Thread(target=voice, args=(sect,n))
        ths.append(t)
        t.start()
    for t in ths:
        t.join()
    for n, sect in enumerate(sects):
        if "voiceoverLen" not in sect or not sect.get("voiceoverp"):
            print(f"Error: Voiceover for section {n} failed to generate.")
            voice(sect,n)
            if "voiceoverLen" not in sect or not sect.get("voiceoverp"):
                print("Voice Generation Failed! Exiting..")
                sys.exit()
    print("Voice Done!!")
    ths=[]
    
    for n,sect in enumerate(sects):
        t=threading.Thread(target=RenderVid, args=(sect,n))
        ths.append(t)
        t.start()
    for t in ths:
        t.join()
    valid_sects = 0
    for s in sects:
        vids = glob.glob(os.path.join(s["path"], "**", "*.mp4"),
        recursive=True)
        vids = [p for p in vids if "partial_movie_files" not in p]
        if vids:
            valid_sects += 1

    if valid_sects < max(1, len(sects) // 2):
        print("The Video Gen Failed try again!")
        sys.exit()
    print("Animation Done!!")
    Mergevidsandvoice(sects,title)

# %%
# TODO : Merge the Vids => Done
# TODO : Verify Video By sending Screenshots => Mght not be needed
# TODO : Strip the Error logs => Done
# TODO : Add Voice to the Video => Done
# TODO : Try to Implement some System to get imgs from Net => not needed
# TODO : Determin the exit pts cuz rn even failing voice exits => Done
# TODO : Set time Limitation for each section => Done
# TODO : The Model Generates Long scenes and Just forgets about the Existing text etc making quality less so Maybe chnage prompt => Done

# %% [markdown]
# # Testing

# %%
if __name__ == "__main__":
    USER_INPUT="Tell me About Backpropagation"
    Main(USER_INPUT)

# %%
# title="The Mathematical Foundations of Neural Networks",
# sects=[{
#       "section_number": 1,
#       "topic": "The Atomic Unit: Linear Algebra & The Perceptron",
#       "subtopic": "Vector Dot Products, Weight Matrices, and Affine Transformations",
#       "estimated_duration_seconds": 25,
#       "narration_script": "At the core, a neuron is just an affine transformation followed by a non-linearity. Mathematically, for an input vector x in R^n, we compute the dot product with a weight vector w, add a bias scalar b, yielding the pre-activation z = w^T x + b. In a layer, this scales to matrix multiplication: Z = X W^T + b. This is a linear map from input space to feature space. Without the next step, stacking these layers would collapse into a single linear model.",
#       "animation_vision": "1. Fade in a column vector 'x' (blue) on the left. 2. Fade in a matrix 'W' (gold) in the center. 3. Animate the matrix-vector multiplication: rows of W light up sequentially, dots connecting to elements of x, summing into a new column vector 'z' (green) on the right. 4. Show a broadcasted bias vector 'b' (red) adding element-wise to 'z'. 5. Display the equation 'z = Wx + b' beneath the animation. 6. Transform the 2D vectors into a 3D grid representing a batch matrix X (batch_size x features) multiplying W (neurons x features) to output Z."
#     },
#     {
#       "section_number": 2,
#       "topic": "Non-Linearity: Activation Functions & Universal Approximation",
#       "subtopic": "ReLU, Sigmoid, Tanh, and the Cybenko-Hornik Theorem",
#       "estimated_duration_seconds": 25,
#       "narration_script": "Linear maps preserve linear subspaces. To approximate arbitrary continuous functions — the Universal Approximation Theorem — we need non-linearities. We apply an element-wise function sigma: R -> R. ReLU, sigma(z) = max(0, z), is the standard: it introduces piece-wise linearity, sparse gradients, and mitigates vanishing gradients compared to saturating functions like Sigmoid or Tanh. Critically, the derivative is simple: 1 for z > 0, 0 otherwise. This piece-wise linear nature allows deep networks to partition input space into convex polytopes.",
#       "animation_vision": "1. Draw a 2D coordinate plane. Plot the Sigmoid curve (S-shape) in dashed grey. Plot Tanh in dashed blue. 2. Draw the ReLU function (hard kink at 0, linear 45 deg after) in thick solid green. 3. Animate a point sliding along the x-axis (input z); show the tangent line (derivative) changing: Sigmoid/Tanh derivatives shrink to zero at extremes (vanishing), ReLU derivative stays constant 1. 4. Visualize 'Partitioning Input Space': Show a 2D input grid. Apply ReLU neurons sequentially. Show decision boundaries (lines) carving the space into polygons. Label: 'Deep ReLU Net = Partitioning into Convex Polytopes'."
#     },
#     {
#       "section_number": 3,
#       "topic": "The Objective: Loss Functions & Probabilistic Interpretation",
#       "subtopic": "Cross-Entropy, MSE, and Maximum Likelihood Estimation",
#       "estimated_duration_seconds": 20,
#       "narration_script": "Training is optimization. We define a loss L(y_hat, y). For regression, Mean Squared Error: L = 1/N ||y_hat - y||^2. This assumes Gaussian noise on the output. For classification, we use Cross-Entropy: L = - sum(y_i log(y_hat_i)). This isn't arbitrary; it is the Negative Log-Likelihood of the Categorical distribution. Minimizing Cross-Entropy is exactly Maximum Likelihood Estimation. The Softmax denominator ensures outputs form a valid probability simplex. The gradient of Cross-Entropy w.r.t logits simplifies beautifully to y_hat - y.",
#       "animation_vision": "1. Show a Gaussian bell curve centered on target 'y'; slide prediction 'y_hat' along x-axis; shade area representing MSE (distance squared). 2. Transition to Classification: Show a vector of logits 'z'. Apply Softmax (exponentiate, normalize) -> probabilities 'p'. 3. Show target one-hot vector 'y'. 4. Animate the Cross-Entropy calculation: -log(p_correct). 5. **Key Derivation Visual**: Show the gradient formula dL/dz = p - y. Highlight that the gradient is simply the 'error' vector (predicted prob minus target). No chain rule expansion needed visually, just the clean result."
#     },
#     {
#       "section_number": 4,
#       "topic": "Optimization: Gradient Descent & Backpropagation",
#       "subtopic": "Chain Rule, Computational Graphs, and Vector-Jacobian Products",
#       "estimated_duration_seconds": 30,
#       "narration_script": "We need dL/dW. Backpropagation is just the chain rule applied efficiently on a Directed Acyclic Graph (DAG). Forward pass computes values; backward pass computes gradients. For a layer z = Wx, the upstream gradient dL/dz arrives. We need dL/dW and dL/dx. By matrix calculus: dL/dW = (dL/dz)^T x. dL/dx = W^T (dL/dz). Notice the transpose swap. This is a Vector-Jacobian Product (VJP). Modern autodiff engines (PyTorch, JAX) build the graph dynamically. We update weights: W <- W - eta * dL/dW. Stochastic Gradient Descent (SGD) approximates the true gradient using mini-batches, adding noise that helps escape sharp minima.",
#       "animation_vision": "1. Draw a Computational Graph: Nodes for x, W, b, z=Wx+b, a=ReLU(z), L. 2. Forward Pass: Animate values flowing left-to-right (colors: blue inputs, gold weights, green outputs). 3. Backward Pass: Animate gradients flowing right-to-left (red arrows). 4. Zoom into the Linear Node: Show incoming gradient 'g' (dL/dz). Visualize Outer Product: g (column) times x (row) -> Gradient Matrix dL/dW. Show g multiplied by W^T -> dL/dx. 5. Show Weight Update: W_new = W_old - lr * Grad. Visualize a 3D Loss Landscape (bowl); show a ball rolling down (SGD step), jittering due to batch noise."
#     },
#     {
#       "section_number": 5,
#       "topic": "Advanced Optimization: Momentum, Adam, & Second Order",
#       "subtopic": "Exponential Moving Averages, Adaptive Learning Rates, and Hessian Approximation",
#       "estimated_duration_seconds": 25,
#       "narration_script": "Vanilla SGD oscillates in ravines. Momentum adds velocity: v = gamma * v + eta * g; W -= v. This dampens oscillations and accelerates along consistent gradients. Adam (Adaptive Moment Estimation) maintains per-parameter learning rates. It tracks the first moment (mean) m = beta1*m + (1-beta1)*g and second moment (uncentered variance) v = beta2*v + (1-beta2)*g^2. Bias correction fixes initialization at zero. Update: W -= lr * m_hat / (sqrt(v_hat) + eps). This approximates a diagonal Hessian (Newton's method), scaling steps by curvature. It handles sparse gradients (NLP) and non-stationary objectives natively.",
#       "animation_vision": "1. Loss Landscape Contour Plot: Long narrow valley (ravine). 2. SGD Path: Zig-zagging down walls (red path). 3. Momentum Path: Heavy ball rolling, smoothing turns, crossing valley floor faster (blue path). 4. Adam Path: Show per-dimension scaling. Visualize two axes: Steep axis (large grad -> large v -> small step). Shallow axis (small grad -> small v -> large step). Path goes straight to minimum (green path). 5. Overlay equations for m_t, v_t, m_hat, v_hat updating in real-time next to the animation."
#     },
#     {
#       "section_number": 6,
#       "topic": "Regularization & Generalization Theory",
#       "subtopic": "Weight Decay (L2), Dropout, Batch Norm, and Implicit Regularization",
#       "estimated_duration_seconds": 25,
#       "narration_script": "Generalization gap is controlled by capacity constraints. L2 Regularization adds lambda||W||^2 to loss. Gradient becomes dL/dW + 2*lambda*W. This is Weight Decay: W <- (1 - 2*lambda*lr)W - lr*dL/dW. It penalizes large weights, effectively smoothing the function (Lipschitz constraint). Dropout randomly zeros activations (Bernoulli mask) during training, scaling by 1/p at inference. This approximates an ensemble of sub-networks. Batch Norm standardizes layer inputs: x_hat = (x - mu_B) / sqrt(var_B + eps), then scales/shifts: y = gamma*x_hat + beta. It reduces Internal Covariate Shift and acts as a regularizer via batch noise. Implicitly, SGD itself biases toward flat minima (low Hessian trace), which generalize better.",
#       "animation_vision": "1. L2/Weight Decay: Show weight vector W shrinking radially toward origin every step before gradient step. Plot Loss vs Weight: parabola widening. 2. Dropout: Show a dense layer. Animate a random binary mask (checkboxes) zeroing out 50% of neurons per step. Show 'Ensemble' ghost networks fading in/out. 3. Batch Norm: Show a batch of activations (dots on number line). Animate Mean subtraction (centering) -> Variance division (scaling to unit Gaussian) -> Gamma/Beta affine transform (stretching/shifting). 4. Flat vs Sharp Minima: 1D Loss curve. Sharp narrow well (bad generalization) vs Wide flat basin (good). Show SGD ball settling in flat basin."
#     },
#     {
#       "section_number": 7,
#       "topic": "Architecture Inductive Biases: Convolutions & Attention",
#       "subtopic": "Weight Sharing (Translation Equivariance) and Softmax Attention (Q,K,V)",
#       "estimated_duration_seconds": 30,
#       "narration_script": "Fully connected layers ignore structure. Conutions enforce Translation Equivariance: f(Tx) = T f(x). The filter kernel K slides across input: (x * K)[i] = sum_j x[i+j] K[j]. This is a Toeplitz matrix multiplication — massive parameter sharing. Attention is different. It computes pairwise interactions. Query Q, Key K, Value V matrices. Attention = Softmax(Q K^T / sqrt(d_k)) V. The QK^T dot product measures token similarity (alignment). Softmax normalizes to a convex combination. Multi-head runs this in parallel subspaces. This is permutation equivariant (set processing) and global receptive field by design. Transformers stack this with residuals and LayerNorm.",
#       "animation_vision": "1. Convolution: Show 1D input signal. Show small Kernel sliding window. Animate element-wise multiply and sum -> single output scalar. Repeat slide. Show Toeplitz Matrix structure (diagonals constant) representing the same op. 2. Attention: Show 3 Matrices Q, K, V (Seq_Len x d_model). 3. Animate Q @ K^T -> Scores Matrix (Seq_Len x Seq_Len). Highlight one row: 'Query token attending to all Keys'. 4. Apply Softmax row-wise -> Attention Weights (rows sum to 1). 5. Animate Weights @ V -> Output. 6. Multi-Head: Split Q,K,V into 'h' heads (color coded). Process independently -> Concat -> Project. 7. Residual Connection: Show 'x + Sublayer(x)' highway path."
#     }]

# %%
# ths=[]
# for n,sect in enumerate(sects):
#     t=threading.Thread(target=voice, args=(sect,n))
#     ths.append(t)
#     t.start()
# for t in ths:
#     t.join()
# for n, sect in enumerate(sects):
#     if "voiceoverLen" not in sect or not sect.get("voiceoverp"):
#         print(f"Error: Voiceover for section {n} failed to generate.")
#         sys.exit(1)
# print("Voice Done!!")


# %%
# # ths=[]
# for n,sect in enumerate(sects):
#     print(f"===============Starting Section {n}===============")
#     # t=threading.Thread(target=RenderVid, args=(sect,n))
#     # ths.append(t)
#     # t.start()
#     RenderVid(sect,n)
# # for t in ths:
# #     t.join()
# # pathl=(s for s in sects if glob.glob(os.path.join(s["path"],'**.mp4')))
# # num=sum([1 for path in pathl if not "partial_movie_files" in path])
# # if num<len(sects)//2:
# #     print("The Video Gen Failed try again!")
# #     sys.exit()
# print("Animation Done!!")


# %%
# Mergevidsandvoice(sects,title)

# %%



