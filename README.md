# LearnAnything

A Video generator Project for Visual Learners to See Animations on different topics!!

Basically how it works:
1. Takes a topic (like "how backpropagation works" or "binary search")
2. Contacts an LLM to Write The script planning how to put together the Video
3. Generates Manim Code for each part
4. Makes voiceovers.
5. Renders each sceneand stitches everything into a final mp4 file!

There is also a simple self healing loop so if manim throws syntax/runtime errors it feeds the error back to the model to fix itself.

## Setup / Running

Needs python 3.10+, ffmpeg and manim installed on your system.

```bash
git clone <repo-url>
cd LearnAnything
pip install -r requirements.txt # or install manim, edge-tts, mutagen, openai, fastapi, etc
```

Set your openrouter api key:
```bash
export OPENROUTER_API_KEY="your-key"
```

To run generation directly:
```bash
python Main.py
```

Or run the web interface:
```bash
cd website
python server.py
```

then open http://localhost:8000 in your browser.

## Notes / caveats
- Rendering can take a bit depending on your cpu
- Uses free tier models on openrouter by default (gemma / nemotron)
- ffmpeg needs to be in your PATH

## Made By 
L0stsky ;)
