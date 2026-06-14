# AI Interview Performance Analyzer

A complete Python-based interview analysis project that evaluates candidate performance from video interviews.

## Features

- Upload interview video through a Streamlit dashboard
- Extract audio from uploaded video
- Generate transcript using SpeechRecognition and Google Web Speech API
- Estimate speech confidence, filler word usage, speaking speed
- Analyze facial expressions and eye contact with OpenCV
- Assess sentiment of answers using NLTK VADER
- Compute a communication score using a lightweight machine learning model
- Provide personalized suggestions for improvement

## Install

1. Create and activate a Python environment:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. If you do not have FFmpeg installed, install it so MoviePy can extract audio from video.

## Run

From the `ai_interview_performance_analyzer` folder:

```bash
streamlit run app.py
```

## Project Structure

- `app.py` — Streamlit dashboard and upload UI
- `analysis.py` — High-level interview analysis pipeline
- `utils.py` — Video/audio extraction, transcription, sentiment, facial metrics
- `model.py` — Machine learning communication score model
- `requirements.txt` — Python package dependencies

## Notes

- The transcription uses `recognize_google`; the machine learning model is trained on synthetic feature data as a demonstration of scoring.
- For best results, use a clear interview recording with visible face and understandable audio.
