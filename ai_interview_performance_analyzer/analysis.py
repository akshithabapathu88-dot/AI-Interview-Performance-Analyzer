import os
import tempfile
from model import CommunicationScorer
from utils import (
    analyze_facial_video,
    extract_audio_from_video,
    get_sentiment_scores,
    transcribe_audio,
)

scorer = CommunicationScorer()


def analyze_video(video_path: str) -> dict:
    audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    extract_audio_from_video(video_path, audio_file)

    transcript, confidence, filler_count, speaking_speed_wpm = transcribe_audio(audio_file)
    sentiment_score = get_sentiment_scores(transcript)
    facial_metrics = analyze_facial_video(video_path)

    features = {
        "speech_confidence": confidence,
        "filler_ratio": max(0.0, min(1.0, filler_count / 20.0)),
        "speaking_speed": max(0.0, min(1.0, speaking_speed_wpm / 190.0)),
        "facial_expression": facial_metrics["expression_score"],
        "eye_contact": facial_metrics["eye_contact_score"],
        "sentiment": sentiment_score,
    }

    communication_score = scorer.predict(features)

    scores = {
        "confidence": features["speech_confidence"],
        "communication": communication_score,
        "sentiment": features["sentiment"],
        "facial_expression": features["facial_expression"],
        "eye_contact": features["eye_contact"],
    }

    suggestions = []
    if features["speech_confidence"] < 0.6:
        suggestions.append("Practice speaking more clearly and with conviction to boost confidence.")
    if filler_count > 3:
        suggestions.append("Reduce filler words like 'um', 'uh', and 'like' by pausing and thinking before answering.")
    if speaking_speed_wpm < 120:
        suggestions.append("Try to speak a bit faster to maintain momentum in your answers.")
    elif speaking_speed_wpm > 180:
        suggestions.append("Slow down slightly to allow the interviewer to follow your ideas.")
    if facial_metrics["expression_score"] < 0.5:
        suggestions.append("Use more expressive facial gestures and smiles to appear engaged.")
    if facial_metrics["eye_contact_score"] < 0.5:
        suggestions.append("Keep your eyes focused on the camera when responding to improve eye contact.")
    if features["sentiment"] < 0.4:
        suggestions.append("Aim for more positive and confident language in your answers.")
    if not suggestions:
        suggestions.append("Great performance! Keep practicing to make your delivery even stronger.")

    return {
        "transcript": transcript,
        "scores": scores,
        "suggestions": suggestions,
        "details": {
            "speech_confidence": features["speech_confidence"],
            "filler_count": filler_count,
            "speaking_speed_wpm": speaking_speed_wpm,
            "facial_expression_score": facial_metrics["expression_score"],
            "eye_contact_score": facial_metrics["eye_contact_score"],
            "sentiment_score": sentiment_score,
            "filler_details": facial_metrics["filler_details"],
            "frame_samples": facial_metrics["frame_samples"],
        },
    }
