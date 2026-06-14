import os
import tempfile
import streamlit as st
import pandas as pd
from analysis import analyze_video
from utils import save_uploaded_file

app_icon_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "public", "favicon.ico")
)

st.set_page_config(
    page_title="AI Interview Performance Analyzer",
    page_icon=app_icon_path,
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@400;500;600;700&display=swap');
    .appview-container .main {
        background: linear-gradient(180deg,#07101a 0%, #0b1724 40%, #07101a 100%);
        color: #ffffff;
        font-family: 'Poppins', 'Inter', sans-serif;
    }
    .appview-container .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1320px;
    }
    .title {
        font-size: 3.2rem;
        font-weight: 800;
        color: #0b3d91;
        letter-spacing: -0.05rem;
        margin: 0 auto 0.6rem;
        text-align: center;
        display: block;
        width: 100%;
    }
    .subtitle {
        font-size: 1.05rem;
        color: #ffffff;
        line-height: 1.8;
        max-width: 760px;
        text-align: center;
        margin: 0 auto 1.2rem;
    }
    .header-block {
        display: block;
        max-width: 860px;
        margin: 0 auto 1.2rem;
        text-align: center;
        color: #ffffff;
        padding: 0 1rem;
    }
    .header-block .title,
    .header-block .subtitle {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    .hero-section {
        padding: 2rem;
        border-radius: 28px;
        background: linear-gradient(180deg,#0f172a 0%, #0b1220 100%);
        box-shadow: 0 10px 30px rgba(2,6,23,0.6);
        border: 1px solid rgba(255,255,255,0.04);
        margin-bottom: 2rem;
    }
    .hero-inner {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        align-items: stretch;
    }
    .hero-content {
        width: 100%;
    }
    .hero-badges {
        width: 100%;
    }
    .hero-badges .feature-title {
        margin-bottom: 1rem;
    }
    .card-grid {
        gap: 1.25rem;
    }
    .feature-card,
    .metric-card,
    .info-card,
    .upload-panel,
    .kpi-card {
        border-radius: 22px;
        background: linear-gradient(180deg,#0b1220 0%, #07101a 100%);
        border: 1px solid rgba(255,255,255,0.04);
        box-shadow: 0 10px 30px rgba(2,6,23,0.6);
        padding: 1.4rem;
    }
    /* Hide any empty card containers to avoid stray blank bars */
    .feature-card:empty, .metric-card:empty, .info-card:empty, .kpi-card:empty {
        display: none !important;
    }
    /* Tighter spacing for KPI row */
    .kpi-card { padding: 1rem; margin-bottom: 0.5rem; }
    .feature-title,
    .stat-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.45rem;
    }
    .feature-text,
    .stat-text,
    .subtitle,
    .footer-text {
        color: #cbd5e1;
    }
    .badge {
        display: inline-flex;
        align-items: center;
        background: rgba(51, 102, 187, 0.18);
        color: #ffffff;
        border-radius: 999px;
        padding: 0.45rem 0.8rem;
        margin-right: 0.55rem;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .summary-label {
        font-size: 0.95rem;
        font-weight: 700;
        color: #33475b;
        margin-bottom: 0.25rem;
    }
    .summary-value {
        font-size: 1.15rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.9rem;
    }
    .streamlit-expanderHeader {
        font-weight: 700;
    }
    .stButton>button {
        background: linear-gradient(135deg, #102a57 0%, #3367d6 100%);
        color: white;
        border: none;
        box-shadow: 0 12px 22px rgba(15, 23, 42, 0.12);
        border-radius: 16px;
        padding: 0.85rem 1.25rem;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
    }
    .stTextInput>div>div>input,
    .stFileUploader>div>button {
        border-radius: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("How it works")
    st.write(
        "1. Upload a candidate interview video.\n"
        "2. Click Analyze Interview.\n"
        "3. Review confidence, communication, sentiment, and face cues.\n"
        "4. Get tailored suggestions for improvement."
    )
    st.markdown("---")
    st.subheader("Why use this")
    st.write(
        "This tool blends audio, visual, and language signals to help candidates improve interview delivery."
    )

st.markdown(
    "<div class='header-block'><div class='title'>AI Interview Performance Analyzer</div>"
    "<p class='subtitle'>Upload an interview recording to analyze speech confidence, filler words, speaking speed, facial expressions, eye contact, sentiment, and receive actionable coaching suggestions.</p></div>",
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='hero-section'>"
    "<div class='hero-inner'>"
    "<div class='hero-content'>"
    "<p class='feature-title'>Practice smarter, faster, and with confidence.</p>"
    "<p class='feature-text'>Your personal interview coach analyzes audio, visual, and language signals to help you improve delivery, reduce filler words, and boost professional presence.</p>"
    "</div>"
    "<div class='hero-badges'>"
    "<div class='feature-title'>What you get</div>"
    "<p class='feature-text'>"
    "<span class='badge'>Confidence</span>"
    "<span class='badge'>Eye contact</span>"
    "<span class='badge'>Speaking pace</span>"
    "<span class='badge'>Positive tone</span>"
    "</p>"
    "</div>"
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)

st.markdown("---")

uploaded_file = st.file_uploader(
    "Upload interview video",
    type=["mp4", "mov", "avi", "mkv"],
    help="Choose a clear recording with visible face and audible speech.",
)

if uploaded_file:
    suffix = os.path.splitext(uploaded_file.name)[1]
    temp_fd, temp_path = tempfile.mkstemp(suffix=suffix)
    os.close(temp_fd)
    temp_path = save_uploaded_file(uploaded_file, temp_path)

    st.video(temp_path)

    if st.button("Analyze Interview"):
        with st.spinner("Analyzing interview, this may take a few moments..."):
            results = analyze_video(temp_path)

        scores = results["scores"]
        transcript = results["transcript"]
        suggestions = results["suggestions"]
        details = results["details"]

        st.markdown("---")
        st.subheader("Interview Insights")

        kpi_cols = st.columns(3, gap='large')
        kpi_cols[0].markdown(
            f"<div class='kpi-card'><div class='stat-title'>Confidence</div><div class='summary-value'>{scores['confidence']*100:.0f}%</div><div class='stat-text'>Steady delivery and vocal assurance.</div></div>",
            unsafe_allow_html=True,
        )
        kpi_cols[1].markdown(
            f"<div class='kpi-card'><div class='stat-title'>Communication</div><div class='summary-value'>{scores['communication']*100:.0f}%</div><div class='stat-text'>Clarity, structure, and idea flow.</div></div>",
            unsafe_allow_html=True,
        )
        kpi_cols[2].markdown(
            f"<div class='kpi-card'><div class='stat-title'>Sentiment</div><div class='summary-value'>{scores['sentiment']*100:.0f}%</div><div class='stat-text'>Tone and positivity of your answers.</div></div>",
            unsafe_allow_html=True,
        )

        score_data = {
            "Metric": [
                "Speech Confidence",
                "Facial Expression",
                "Eye Contact",
                "Sentiment",
                "Speaking Speed",
            ],
            "Score": [
                scores["confidence"] * 100,
                scores["facial_expression"] * 100,
                scores["eye_contact"] * 100,
                scores["sentiment"] * 100,
                min(details["speaking_speed_wpm"], 220) / 220 * 100,
            ],
        }

        chart_df = pd.DataFrame(score_data).set_index("Metric")
        with st.container():
            st.subheader("Performance overview")
            st.bar_chart(chart_df)

        with st.expander("Transcript"):
            st.text_area("Generated interview transcript", transcript, height=240)

        with st.expander("Suggestions for Improvement"):
            for suggestion in suggestions:
                st.markdown(f"- {suggestion}")

        with st.expander("Analysis Summary"):
            col1, col2 = st.columns(2, gap='large')
            with col1:
                st.markdown(f"**Speech confidence:** {scores['confidence']*100:.0f}%")
                st.markdown(f"**Facial expression strength:** {scores['facial_expression']*100:.0f}%")
                st.markdown(f"**Eye contact quality:** {scores['eye_contact']*100:.0f}%")
            with col2:
                st.markdown(f"**Sentiment score:** {scores['sentiment']*100:.0f}%")
                st.markdown(f"**Speaking speed:** {details['speaking_speed_wpm']:.1f} WPM")
                st.markdown(f"**Filler words:** {details['filler_count']}")
                st.markdown(f"**Sample frames analyzed:** {details.get('frame_samples', 'N/A')}")
