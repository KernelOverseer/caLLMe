# caLLMe
<img width="1536" height="1024" alt="caLLMe Banner" src="https://github.com/user-attachments/assets/a22ddafd-a336-495f-a360-e7b5b65d4530" />

A tiny, **voice-first** assistant that turns your microphone into a real-time conversation with an LLM.  
caLLMe listens, transcribes, generates a response, speaks it back, and lets you interrupt at any time – all in just a few hundred lines of Python.

## Features

* **Silero Voice Activity Detection** – smartly starts/stops recording when you speak.
* **Groq Whisper STT** – high-quality speech-to-text.
* **Groq Llama 3 LLM** – streams replies token-by-token.
* **Groq PlayAI TTS** – natural, low-latency speech synthesis.
* **Async audio queue** – responses are played while the next ones are being generated; speak again to interrupt.
* Simple, hackable architecture – every component lives in `src/` and follows small base interfaces (VAD, STT, TTS, Gen, Player).

## Quick Start

```bash
# 1. Grab the code
$ git clone https://github.com/yourname/caLLMe.git
$ cd caLLMe

# 2. Create & activate a virtual env (optional but recommended)
$ python -m venv .venv
$ source .venv/bin/activate

# 3. Install Python dependencies
$ pip install -r requirements.txt

# 4. Set your Groq API key (required for STT, TTS & LLM)
$ export GROQ_API_KEY="sk_..."

# 5. Run the assistant 🎙️
$ python src/main.py
```

## Customising

* Change the **system prompt** & initial dialogue in `src/main.py`.
* Swap out models by tweaking default parameters in:
  * `src/gen/groq.py` (LLM)
  * `src/stt/groqWhisper.py` (STT)
  * `src/tts/groqPlayai.py` (TTS)
* Adjust VAD sensitivity in `src/vad/silerovad.py` (`on_threshold`, `off_threshold`, etc.).

## Troubleshooting

* PyAudio may require system packages (e.g. `portaudio`, `alsa-utils`). On Ubuntu:  
  `sudo apt install portaudio19-dev python3-pyaudio`
* If audio is choppy, lower `max_audio_queue` in `Conversation` or tweak model temperatures.

---

Built with ❤️ & open-source software. Enjoy hacking! 
