import streamlit as st

from summarizer import transcribe_audio, summarize_text
from speech import text_to_speech


st.set_page_config(
    page_title="VoxNote AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(
            circle at 5% 0%,
            rgba(100, 70, 220, 0.15),
            transparent 35%
        ),
        linear-gradient(
            135deg,
            #0b1020 0%,
            #111827 55%,
            #15112a 100%
        );
    color: #f8fafc;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    padding: 30px;
    border-radius: 24px;
    background: linear-gradient(
        120deg,
        #312e81,
        #4c1d95,
        #164e63
    );
    border: 1px solid rgba(255,255,255,0.15);
    margin-bottom: 24px;
}

.hero h1 {
    color: white;
    font-size: 42px;
    margin-bottom: 8px;
}

.hero p {
    color: #e0e7ff;
    font-size: 17px;
}

.panel {
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 16px;
}

div.stButton > button {
    background: linear-gradient(90deg, #7c3aed, #2563eb);
    color: white;
    border: none;
    border-radius: 12px;
    min-height: 46px;
    font-weight: 600;
}

div.stButton > button:hover {
    border: 1px solid #a5b4fc;
    color: white;
}
</style>
""", unsafe_allow_html=True)


if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "speech_audio" not in st.session_state:
    st.session_state.speech_audio = None


st.markdown("""
<div class="hero">
    <h1>VoxNote AI</h1>
    <p>
        Turn conversations into clear notes.
        Transcribe audio, summarize important ideas,
        and listen to your summary with AI voice.
    </p>
    <p>
        Whisper | LangChain | Groq | Streamlit
    </p>
</div>
""", unsafe_allow_html=True)


with st.sidebar:
    st.title("AI Settings")

    summary_style = st.selectbox(
        "Summary length",
        ["Short", "Detailed", "Meeting Notes"],
        index=1
    )

    voice_gender = st.selectbox(
        "Narrator voice",
        ["Female", "Male"]
    )

    speech_rate = st.slider(
        "Speaking speed",
        min_value=120,
        max_value=220,
        value=165,
        step=5
    )

    st.divider()

    st.caption("Processing pipeline")
    st.write("1. Whisper transcription")
    st.write("2. LangChain and Groq summary")
    st.write("3. Local text-to-speech")

    st.caption(
        "Audio transcription and summarization require "
        "an internet connection and a valid Groq API key."
    )


audio_tab, text_tab, about_tab = st.tabs([
    "Audio Summarizer",
    "Text to Voice",
    "How It Works"
])


with audio_tab:
    st.markdown("## Transform your voice into notes")

    st.write(
        "Upload a recording or record a message with your microphone."
    )

    upload_col, record_col = st.columns(2)

    with upload_col:
        st.markdown(
            '<div class="panel">',
            unsafe_allow_html=True
        )

        st.subheader("Upload audio")

        uploaded_audio = st.file_uploader(
            "Choose an audio file",
            type=[
                "wav", "mp3", "m4a", "mp4",
                "mpeg", "mpga", "webm", "ogg"
            ],
            key="audio_upload"
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    with record_col:
        st.markdown(
            '<div class="panel">',
            unsafe_allow_html=True
        )

        st.subheader("Record your voice")

        recorded_audio = st.audio_input(
            "Record a voice message",
            key="microphone_recording"
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    selected_audio = recorded_audio or uploaded_audio

    if selected_audio:
        st.success("Audio is ready for processing.")
        st.audio(selected_audio)

    if st.button(
        "Transcribe and Summarize",
        type="primary",
        use_container_width=True,
        disabled=selected_audio is None
    ):
        try:
            audio_bytes = selected_audio.getvalue()

            if not audio_bytes:
                st.error("The selected audio file is empty.")
                st.stop()

            if len(audio_bytes) > 25 * 1024 * 1024:
                st.error(
                    "Please use an audio file smaller than 25 MB."
                )
                st.stop()

            filename = getattr(
                selected_audio,
                "name",
                "recording.wav"
            )

            mime_type = getattr(
                selected_audio,
                "type",
                None
            ) or "audio/wav"

            with st.spinner(
                "Whisper is transcribing your audio..."
            ):
                transcript = transcribe_audio(
                    audio_bytes,
                    filename,
                    mime_type
                )

            st.session_state.transcript = transcript
            st.session_state.summary = ""
            st.session_state.speech_audio = None

            with st.spinner(
                "Groq is creating your summary..."
            ):
                summary = summarize_text(
                    transcript,
                    summary_style
                )

            st.session_state.summary = summary

            st.success(
                "Your transcript and summary are ready!"
            )

        except Exception as error:
            st.error(f"Processing failed: {error}")

    if st.session_state.transcript:
        st.divider()

        st.markdown("## Transcript")

        edited_transcript = st.text_area(
            "Review or edit the recognized text",
            value=st.session_state.transcript,
            height=220,
            key="edited_transcript"
        )

        st.download_button(
            "Download transcript",
            data=edited_transcript,
            file_name="transcript.txt",
            mime="text/plain",
            use_container_width=True
        )

        if st.button(
            "Summarize edited transcript",
            use_container_width=True
        ):
            try:
                with st.spinner(
                    "Creating a new summary..."
                ):
                    st.session_state.summary = summarize_text(
                        edited_transcript,
                        summary_style
                    )

                    st.session_state.speech_audio = None

                st.success("Updated summary created!")

            except Exception as error:
                st.error(
                    f"Summarization failed: {error}"
                )

    if st.session_state.summary:
        st.divider()

        st.markdown("## AI Summary")

        st.markdown(
            '<div class="panel">',
            unsafe_allow_html=True
        )

        st.markdown(st.session_state.summary)

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

        st.download_button(
            "Download summary",
            data=st.session_state.summary,
            file_name="ai_summary.txt",
            mime="text/plain",
            use_container_width=True
        )

        if st.button(
            "Generate spoken summary",
            use_container_width=True
        ):
            try:
                with st.spinner(
                    "Generating your AI voice..."
                ):
                    st.session_state.speech_audio = text_to_speech(
                        st.session_state.summary,
                        voice_gender,
                        speech_rate
                    )

                st.success("Speech audio is ready!")

            except Exception as error:
                st.error(
                    f"Text-to-speech failed: {error}"
                )

        if st.session_state.speech_audio:
            st.audio(
                st.session_state.speech_audio,
                format="audio/wav"
            )

            st.download_button(
                "Download spoken summary",
                data=st.session_state.speech_audio,
                file_name="spoken_summary.wav",
                mime="audio/wav",
                use_container_width=True
            )


with text_tab:
    st.markdown("## Convert text into speech")

    text_for_speech = st.text_area(
        "Enter the text you want the application to speak",
        height=220,
        placeholder=(
            "Enter a meeting summary, study notes, "
            "or any text here..."
        ),
        key="standalone_text"
    )

    text_voice = st.selectbox(
        "Choose voice",
        ["Female", "Male"],
        key="text_voice"
    )

    text_rate = st.slider(
        "Choose speaking speed",
        120,
        220,
        165,
        5,
        key="text_rate"
    )

    if st.button(
        "Convert text to voice",
        use_container_width=True
    ):
        if not text_for_speech.strip():
            st.warning("Please enter some text first.")
        else:
            try:
                with st.spinner(
                    "Generating spoken audio..."
                ):
                    audio = text_to_speech(
                        text_for_speech,
                        text_voice,
                        text_rate
                    )

                st.success(
                    "Speech generated successfully."
                )

                st.audio(audio, format="audio/wav")

                st.download_button(
                    "Download speech",
                    data=audio,
                    file_name="text_to_speech.wav",
                    mime="audio/wav",
                    use_container_width=True
                )

            except Exception as error:
                st.error(
                    f"Speech generation failed: {error}"
                )


with about_tab:
    st.markdown("## How this project works")

    st.markdown("""
    **1. Audio input:** The user uploads a recording or records
    a voice message.

    **2. Speech recognition:** Whisper converts the audio
    into a text transcript.

    **3. Language processing:** LangChain prepares the prompt
    and connects it to the Groq-hosted language model.

    **4. Summarization:** The model extracts the important
    information and presents it in readable language.

    **5. Speech generation:** The local text-to-speech engine
    reads the summary aloud.

    **6. Downloads:** The user can save the transcript,
    summary, and generated audio.
    """)

    st.info(
        "Avoid uploading confidential meetings, passwords, "
        "personal records, or sensitive company audio unless "
        "you have authorization to process them."
    )


st.divider()

st.caption(
    "VoxNote AI | Built with Python, Streamlit, Whisper, "
    "LangChain, Groq and pyttsx3"
)