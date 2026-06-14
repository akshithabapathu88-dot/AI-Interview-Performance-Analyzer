import os
import re
import subprocess
import tempfile
import cv2
import numpy as np
import nltk
import speech_recognition as sr
from imageio_ffmpeg import get_ffmpeg_exe
from nltk.sentiment import SentimentIntensityAnalyzer

FILLER_WORDS = ["um", "uh", "like", "so", "you know", "actually", "basically"]


def save_uploaded_file(uploaded_file, destination_path):
    with open(destination_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return destination_path


def extract_audio_from_video(video_path: str, audio_path: str) -> str:
    ffmpeg_path = None
    try:
        ffmpeg_path = get_ffmpeg_exe()
    except Exception:
        pass

    if not ffmpeg_path or not os.path.exists(ffmpeg_path):
        raise FileNotFoundError(
            "FFmpeg binary not found. Install FFmpeg or ensure imageio-ffmpeg is available."
        )

    ffmpeg_cmd = [
        ffmpeg_path,
        "-y",
        "-i",
        video_path,
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        audio_path,
    ]
    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return audio_path


def transcribe_audio(audio_path: str):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)

    try:
        raw_result = recognizer.recognize_google(audio, show_all=True)
    except sr.RequestError:
        raw_result = {}
    except sr.UnknownValueError:
        raw_result = {}

    transcript = ""
    confidence = 0.0
    if isinstance(raw_result, dict) and raw_result.get("alternative"):
        alternatives = raw_result["alternative"]
        transcript = alternatives[0].get("transcript", "")
        confidence_values = [alt.get("confidence", 0.0) for alt in alternatives if alt.get("confidence") is not None]
        confidence = float(np.mean(confidence_values)) if confidence_values else 0.75
    elif isinstance(raw_result, str):
        transcript = raw_result
        confidence = 0.75
    else:
        transcript = ""
        confidence = 0.0

    transcript = transcript.strip()
    filler_count = _count_fillers(transcript)
    speaking_speed_wpm = _estimate_speaking_speed(transcript, audio_path)
    return transcript, confidence, filler_count, speaking_speed_wpm


def _count_fillers(transcript: str) -> int:
    lowered = transcript.lower()
    count = 0
    for filler in FILLER_WORDS:
        count += len(re.findall(r"\b" + re.escape(filler) + r"\b", lowered))
    return count


import wave


def _estimate_speaking_speed(transcript: str, audio_path: str) -> float:
    words = len(transcript.split())
    try:
        with wave.open(audio_path, "rb") as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            duration_seconds = frames / float(rate) if rate else 0.0
    except Exception:
        duration_seconds = max(1.0, len(transcript.split()) / 2.0)
    minutes = max(0.1, duration_seconds / 60.0)
    return words / minutes if minutes else 0.0


def get_sentiment_scores(transcript: str) -> float:
    _ensure_nltk_data()
    analyzer = SentimentIntensityAnalyzer()
    if not transcript:
        return 0.5
    scores = analyzer.polarity_scores(transcript)
    sentiment = (scores["pos"] + 0.5 * (1.0 - scores["neg"]))
    return float(np.clip(sentiment, 0.0, 1.0))


def _ensure_nltk_data():
    try:
        nltk.data.find("sentiment/vader_lexicon")
    except LookupError:
        nltk.download("vader_lexicon", quiet=True)


def analyze_facial_video(video_path: str, frame_sample_rate: float = 1.0) -> dict:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
    smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        raise ValueError("Unable to open video for facial analysis.")

    fps = capture.get(cv2.CAP_PROP_FPS) or 25
    frame_interval = max(1, int(round(fps * frame_sample_rate)))
    frame_index = 0
    detected_frames = 0
    expression_frames = 0
    eye_contact_frames = 0
    face_centers = []

    while True:
        ret, frame = capture.read()
        if not ret:
            break
        if frame_index % frame_interval != 0:
            frame_index += 1
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
        if len(faces) > 0:
            detected_frames += 1
            x, y, w, h = faces[0]
            face_region = gray[y : y + h, x : x + w]
            eyes = eye_cascade.detectMultiScale(face_region, scaleFactor=1.1, minNeighbors=8, minSize=(20, 20))
            smiles = smile_cascade.detectMultiScale(face_region, scaleFactor=1.7, minNeighbors=22, minSize=(25, 25))

            if len(smiles) > 0:
                expression_frames += 1
            if len(eyes) >= 1:
                # approximate eye contact by checking if face is centered in the frame
                frame_center = (frame.shape[1] / 2, frame.shape[0] / 2)
                face_center = (x + w / 2, y + h / 2)
                offset = np.linalg.norm(np.array(face_center) - np.array(frame_center))
                max_offset = np.linalg.norm(np.array(frame_center))
                if offset < max_offset * 0.5:
                    eye_contact_frames += 1
        frame_index += 1

    capture.release()

    if detected_frames == 0:
        return {
            "expression_score": 0.35,
            "eye_contact_score": 0.35,
            "frame_samples": 0,
            "filler_details": {},
        }

    expression_score = float(np.clip(expression_frames / detected_frames, 0.0, 1.0))
    eye_contact_score = float(np.clip(eye_contact_frames / detected_frames, 0.0, 1.0))

    return {
        "expression_score": expression_score,
        "eye_contact_score": eye_contact_score,
        "frame_samples": detected_frames,
        "filler_details": {},
    }
