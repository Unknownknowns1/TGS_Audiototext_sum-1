import os

from dotenv import load_dotenv
from groq import Groq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

load_dotenv()


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Add it to your .env file.")

    return Groq(api_key=api_key)


def transcribe_audio(audio_bytes, filename, mime_type):
    client = get_groq_client()

    response = client.audio.transcriptions.create(
        model="whisper-large-v3",
        file=(filename, audio_bytes, mime_type),
        response_format="text",
    )

    if isinstance(response, str):
        transcript = response
    else:
        transcript = getattr(response, "text", "")

    return transcript.strip()


def summarize_text(text, summary_style="Detailed"):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set. Add it to your .env file.")

    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0.2,
        max_tokens=1200,
        api_key=api_key,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are a professional meeting assistant.
                Summarize the transcript in simple, natural English.
                Preserve the original meaning.
                Do not invent facts, names, dates, or decisions.
                Identify the main ideas and action items.
                Use headings and bullet points.
                Do not repeat the entire transcript.
                """,
            ),
            (
                "human",
                """
                Summary style: {summary_style}

                Summarize this transcript:

                {transcript}
                """,
            ),
        ]
    )

    chain = prompt | llm | StrOutputParser()

    result = chain.invoke(
        {
            "summary_style": summary_style,
            "transcript": text,
        }
    )

    return result.strip()
