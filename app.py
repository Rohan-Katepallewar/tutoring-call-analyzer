import os
import streamlit as st
import tempfile
from datetime import timedelta
from openai import OpenAI
from pydub import AudioSegment
from sarvamai import SarvamAI  # Sarvam's Python SDK
import json

# Page config with attractive theme
st.set_page_config(
    page_title="🎓 Tutoring Call Analyzer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for attractive UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .feature-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 0.5rem 0;
    }
    .stSelectbox > div > div {
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🎓 AI-Powered Tutoring Call Analyzer</h1>
    <p>Advanced speech-to-text analysis for educational effectiveness</p>
    <p><strong>🌏 Supports Kannada & English</strong></p>
</div>
""", unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Keys section
    st.markdown("### 🔑 API Keys")
    openai_key = st.text_input("🤖 OpenAI API Key", type="password", help="Required for GPT analysis")
    
    # STT Provider selection
    st.markdown("### 🎤 Speech-to-Text Provider")
    stt_provider = st.selectbox(
        "Choose STT Service",
        options=["Whisper (OpenAI)", "Sarvam STT (Batch)"],
        help="Whisper supports multiple languages, Sarvam specializes in Indian languages"
    )
    use_sarvam = (stt_provider == "Sarvam STT (Batch)")
    
    sarvam_key = ""
    if use_sarvam:
        sarvam_key = st.text_input("🎯 Sarvam API Key", type="password", help="Required for Sarvam STT")
    
    # Language selection
    st.markdown("### 🌐 Language Settings")
    if use_sarvam:
        language = st.selectbox(
            "Select Language",
            options=["Kannada", "English"],
            help="Language for speech recognition"
        )
        lang_code = "kn-IN" if language == "Kannada" else "en-IN"
    else:
        st.info("Whisper auto-detects language (Kannada & English supported)")
        lang_code = "auto"

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📁 Upload Audio File")
    uploaded = st.file_uploader(
        "",
        type=["wav", "mp3", "m4a", "flac"],
        help="Upload your tutoring call recording (WAV, MP3, M4A, or FLAC format)"
    )
    
    if uploaded:
        st.success(f"✅ File uploaded: {uploaded.name}")

with col2:
    st.markdown("### 📊 Quick Stats")
    if uploaded:
        # Display file info
        file_size = len(uploaded.getbuffer()) / 1024 / 1024
        st.metric("File Size", f"{file_size:.1f} MB")

# Processing section
if not openai_key or not uploaded:
    st.markdown("""
    <div class="feature-box">
        <h3>🚀 How it works:</h3>
        <ol>
            <li><strong>Upload</strong> your tutoring call recording</li>
            <li><strong>Select</strong> your preferred STT provider</li>
            <li><strong>Enter</strong> your API keys</li>
            <li><strong>Analyze</strong> teaching effectiveness and student engagement</li>
        </ol>
    </div>
    
    <div class="feature-box">
        <h3>✨ Features:</h3>
        <ul>
            <li>🎯 <strong>Smart Chunking</strong> - Analyzes key moments in the session</li>
            <li>🗣️ <strong>Speaker Diarization</strong> - Separates teacher and student speech</li>
            <li>📈 <strong>Learning Progress</strong> - Tracks student understanding</li>
            <li>💡 <strong>Teaching Tips</strong> - Suggestions for improvement</li>
            <li>🌏 <strong>Multi-language</strong> - Kannada and English support</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Initialize OpenAI client
client = OpenAI(api_key=openai_key)

# Processing starts here
with st.spinner('🎵 Loading audio file...'):
    # Save uploaded file
    audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    with open(audio_path, "wb") as f:
        f.write(uploaded.getbuffer())

    # Load and analyze audio
    audio = AudioSegment.from_file(audio_path)
    duration = len(audio) / 1000.0

# Display audio info
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("⏱️ Duration", f"{duration:.1f} seconds")
with col2:
    st.metric("🎵 Format", uploaded.type.split('/')[-1].upper())
with col3:
    st.metric("🔊 Size", f"{len(uploaded.getbuffer()) / 1024 / 1024:.1f} MB")

# Helper functions
def transcribe_whisper(path):
    with open(path, "rb") as f:
        resp = client.audio.transcriptions.create(model="whisper-1", file=f)
    return resp.text

def transcribe_sarvam(path, language_code):
    sa = SarvamAI(api_subscription_key=sarvam_key)
    job = sa.speech_to_text_job.create_job(
        language_code=language_code,
        model="saarika:v2.5",
        with_timestamps=True,
        with_diarization=True,
        num_speakers=2
    )
    job.upload_files(file_paths=[path])
    job.start()
    job.wait_until_complete(poll_interval=5)
    outdir = tempfile.mkdtemp()
    job.download_outputs(output_dir=outdir)
    import glob
    for file in sorted(glob.glob(os.path.join(outdir, "*"))):
        with open(file, "r") as f:
            data = json.load(f)
        return data
    return {}

# Updated chunk positions (30-40 second chunks)
long_chunk_end = min(180.0, duration)
chunks = {
    "opening": (0.0, long_chunk_end),
    "middle_segment": (max(0, duration/2 - 20), min(duration, duration/2 + 20)),
    "pre_checkpoint": (max(0, duration * 0.75 - 15), min(duration, duration * 0.75 + 15)),
    "closing": (max(0, duration - 35), duration),
}

# Processing chunks
st.markdown("### 🔄 Processing Audio Chunks")
progress_bar = st.progress(0)
status_text = st.empty()

snippet_texts = {}
speaker_map = {}

for i, (label, (start, end)) in enumerate(chunks.items()):
    chunk_duration = end - start
    progress_bar.progress((i + 1) / len(chunks))
    status_text.text(f"Processing {label} chunk: {timedelta(seconds=int(start))}-{timedelta(seconds=int(end))} ({chunk_duration:.1f}s)")
    
    # Extract chunk
    chunk = audio[int(start*1000):int(end*1000)]
    fn = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    chunk.export(fn, format="wav")
    
    # Transcribe
    if use_sarvam:
        data = transcribe_sarvam(fn, lang_code)
        entries = data.get("diarized_transcript", {}).get("entries", [])
        text = " ".join(e["transcript"] for e in entries)
        snippet_texts[label] = text
        for e in entries:
            speaker_map.setdefault(e["speaker_id"], []).append(e["transcript"])
    else:
        text = transcribe_whisper(fn)
        snippet_texts[label] = text
    
    # Clean up temp file
    try:
        os.unlink(fn)
    except:
        pass

progress_bar.progress(1.0)
status_text.text("✅ All chunks processed!")

# Detect operation from opening segment
opening_text = snippet_texts.get("opening", "")
detected_operation = "unknown"
operations = ["multiplication", "addition", "subtraction", "division", "fractions", "geometry", "algebra"]
for op in operations:
    if op in opening_text.lower():
        detected_operation = op
        break

# Prepare analysis
aggregated_text = f"Detected operation hint: {detected_operation}\n\n"
for label, text in snippet_texts.items():
    aggregated_text += f"=== {label.upper()} SEGMENT ===\n{text}\n\n"

# Enhanced analysis prompt
analysis_prompt = f"""You are an expert educational analyst reviewing a math tutoring session. 

AUDIO SEGMENTS FROM THE CALL:
{aggregated_text}

Please provide a comprehensive analysis in JSON format with these fields:

1. "operation": Primary mathematical concept/operation being taught
2. "operation_confidence": Confidence score (0.0-1.0) in the detected operation
3. "session_summary": 2-3 sentence overview of the entire session
4. "learning_progression": How the student's understanding evolved during the call
5. "teaching_methods": List of instructional strategies used by the tutor
6. "student_engagement_level": Scale of 1-10 with explanation
7. "key_learning_moments": 3-4 specific moments where significant learning occurred
8. "areas_mastered": Concepts the student understood well
9. "areas_needing_work": Concepts requiring more practice
10. "tutor_effectiveness": Assessment of teaching quality and approach
11. "recommended_next_steps": Specific suggestions for the next session
12. "session_highlights": Most valuable parts of the tutoring session

Focus on educational effectiveness, student comprehension patterns, and actionable insights for improvement."""

# Get GPT analysis
with st.spinner('🤖 Generating AI analysis...'):
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": analysis_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        analysis = json.loads(resp.choices[0].message.content)
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        analysis = {}

# Display results
st.markdown("---")
st.markdown("## 📊 Comprehensive Analysis Results")

if analysis:
    # Session overview
    if "session_summary" in analysis:
        st.markdown(f"""
        <div class="feature-box">
            <h3>📝 Session Summary</h3>
            <p>{analysis['session_summary']}</p>
        </div>
        """, unsafe_allow_html=True)

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if "operation" in analysis:
            confidence = analysis.get('operation_confidence', 0)
            st.metric("🎯 Detected Topic", analysis['operation'], f"{confidence:.0%} confidence")
    
    with col2:
        if "student_engagement_level" in analysis:
            engagement = analysis['student_engagement_level']
            if isinstance(engagement, str) and '/' in engagement:
                score = engagement.split('/')[0]
            else:
                score = str(engagement)
            st.metric("📈 Student Engagement", f"{score}/10")
    
    with col3:
        total_chunks = len(snippet_texts)
        st.metric("🔍 Segments Analyzed", total_chunks)
    
    with col4:
        st.metric("⏱️ Processing Time", f"{duration:.0f}s audio")

    # Detailed analysis
    tab1, tab2, tab3, tab4 = st.tabs(["📚 Learning Analysis", "👨‍🏫 Teaching Quality", "💡 Recommendations", "🗣️ Speaker Data"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            if "learning_progression" in analysis:
                st.markdown("**📈 Learning Progression:**")
                st.write(analysis['learning_progression'])
            
            if "areas_mastered" in analysis:
                st.markdown("**✅ Areas Mastered:**")
                for area in analysis['areas_mastered']:
                    st.write(f"• {area}")
        
        with col2:
            if "key_learning_moments" in analysis:
                st.markdown("**⭐ Key Learning Moments:**")
                for i, moment in enumerate(analysis['key_learning_moments'], 1):
                    st.write(f"{i}. {moment}")
            
            if "areas_needing_work" in analysis:
                st.markdown("**🎯 Areas Needing Work:**")
                for area in analysis['areas_needing_work']:
                    st.write(f"• {area}")

    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            if "teaching_methods" in analysis:
                st.markdown("**🎓 Teaching Methods Used:**")
                for method in analysis['teaching_methods']:
                    st.write(f"• {method}")
        
        with col2:
            if "tutor_effectiveness" in analysis:
                st.markdown("**👨‍🏫 Tutor Effectiveness:**")
                st.write(analysis['tutor_effectiveness'])
            
            if "session_highlights" in analysis:
                st.markdown("**🌟 Session Highlights:**")
                for highlight in analysis['session_highlights']:
                    st.write(f"• {highlight}")

    with tab3:
        if "recommended_next_steps" in analysis:
            st.markdown("**🚀 Recommended Next Steps:**")
            for step in analysis['recommended_next_steps']:
                st.write(f"• {step}")

    with tab4:
        if use_sarvam and speaker_map:
            st.markdown("**🗣️ Speaker Diarization Results:**")
            for speaker_id, segments in speaker_map.items():
                st.markdown(f"**{speaker_id} ({len(segments)} segments):**")
                # Show first few segments
                preview_segments = segments[:3]
                for segment in preview_segments:
                    st.write(f"• {segment[:100]}{'...' if len(segment) > 100 else ''}")
                if len(segments) > 3:
                    st.write(f"... and {len(segments) - 3} more segments")
        else:
            st.info("Speaker diarization is available with Sarvam STT option.")

# Cleanup
try:
    os.unlink(audio_path)
except:
    pass

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🎓 Built with ❤️ for better education • Supports Kannada & English</p>
    <p>Powered by OpenAI Whisper/GPT-4 & Sarvam AI</p>
</div>
""", unsafe_allow_html=True)