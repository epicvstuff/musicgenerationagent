import os
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import requests
from agno.agent import Agent
from agno.run.agent import RunOutput
from agno.models.openai import OpenAIChat
from agno.tools.models_labs import FileType, ModelsLabTools
from agno.utils.log import logger
import streamlit as st

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── Sidebar ──────────────────────────────────────────────
st.sidebar.title("Configuration")

openai_api_key = st.sidebar.text_input(
    "OpenAI API Key",
    value=os.getenv("OPENAI_API_KEY", ""),
    type="password",
)
models_lab_api_key = st.sidebar.text_input(
    "ModelsLab API Key",
    value=os.getenv("MODELSLAB_API_KEY", ""),
    type="password",
)

llm_choice = st.sidebar.radio(
    "Prompt Enhancement Model",
    ["GPT-4o", "Claude Sonnet 4.6", "Gemini 2.0 Flash", "None — send directly"],
)

anthropic_api_key = ""
if llm_choice == "Claude Sonnet 4.6":
    anthropic_api_key = st.sidebar.text_input(
        "Anthropic API Key",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        type="password",
    )

google_api_key = ""
if llm_choice == "Gemini 2.0 Flash":
    google_api_key = st.sidebar.text_input(
        "Google API Key",
        value=os.getenv("GOOGLE_API_KEY", ""),
        type="password",
    )

# ── Main UI ───────────────────────────────────────────────
st.title("🎶 AI Music Generator Agent")

TEMPLATES = {
    "Custom prompt...": "",
    "Epic orchestral battle theme": "Epic orchestral battle theme with dramatic strings and brass",
    "Rainy-day lo-fi study beats": "Rainy-day lo-fi study beats with soft piano and gentle rain sounds",
    "Upbeat jazz café music": "Upbeat jazz café background music with piano, bass, and light percussion",
    "Ambient electronic meditation": "Ambient electronic meditation soundscape with gentle synths and pads",
    "Cinematic thriller tension": "Cinematic tension build-up with staccato strings and low brass swells",
    "Cheerful acoustic folk": "Cheerful acoustic folk song with guitar, ukulele, and whistling melody",
    "Dark synthwave 80s": "Dark synthwave retro 80s track with pulsing bass and arpeggiated synths",
}

template_choice = st.selectbox("Quick-start template", list(TEMPLATES.keys()))

st.subheader("Prompt Builder")

col1, col2 = st.columns(2)
with col1:
    genre = st.selectbox(
        "Genre",
        ["Classical", "Jazz", "Lo-fi", "Electronic", "Cinematic", "Ambient",
         "Folk", "Rock", "Synthwave", "R&B", "Hip-hop", "Custom"],
    )
    mood = st.multiselect(
        "Mood",
        ["Relaxing", "Energetic", "Melancholic", "Uplifting",
         "Tense", "Playful", "Dark", "Romantic", "Mysterious"],
    )
with col2:
    tempo = st.select_slider(
        "Tempo",
        options=["Very Slow (40 BPM)", "Slow (70 BPM)", "Medium (100 BPM)",
                 "Fast (130 BPM)", "Very Fast (160 BPM)"],
        value="Medium (100 BPM)",
    )
    duration = st.select_slider(
        "Duration",
        options=["15 seconds", "30 seconds", "60 seconds", "90 seconds"],
        value="30 seconds",
    )

instruments = st.text_input(
    "Instruments (optional)",
    placeholder="e.g., piano, violin, acoustic guitar",
)

extra_details = st.text_area(
    "Additional details",
    value=TEMPLATES[template_choice],
    height=80,
    placeholder="Describe any extra qualities, structure, or vibe...",
)

num_variations = st.slider("Variations to generate", 1, 3, 1)

# ── Helpers ───────────────────────────────────────────────

def build_prompt() -> str:
    parts = []
    genre_label = genre if genre != "Custom" else "music"
    parts.append(f"Generate a {duration} {genre_label.lower()} piece")
    if mood:
        parts.append(f"with a {', '.join(mood).lower()} mood")
    parts.append(f"at {tempo.split('(')[0].strip().lower()} tempo")
    if instruments:
        parts.append(f"featuring {instruments}")
    if extra_details.strip():
        parts.append(extra_details.strip())
    return ". ".join(parts)


def make_agent() -> Agent:
    if llm_choice == "Claude Sonnet 4.6":
        try:
            from agno.models.anthropic import Claude
            model = Claude(id="claude-sonnet-4-6", api_key=anthropic_api_key)
        except ImportError:
            st.warning("Anthropic support not available. Falling back to GPT-4o.")
            model = OpenAIChat(id="gpt-4o", api_key=openai_api_key)
    elif llm_choice == "Gemini 2.0 Flash":
        try:
            from agno.models.google import Gemini
            model = Gemini(id="gemini-2.0-flash", api_key=google_api_key)
        except ImportError:
            st.warning("google-genai not installed. Falling back to GPT-4o.")
            model = OpenAIChat(id="gpt-4o", api_key=openai_api_key)
    else:
        model = OpenAIChat(id="gpt-4o", api_key=openai_api_key)

    if llm_choice == "None — send directly":
        instructions = [
            "Call generate_media with the user's prompt exactly as given, without any modification.",
        ]
    else:
        instructions = [
            "Enhance the user's music prompt with rich detail specifying:",
            "- Genre, style, and structure (intro, verses, chorus, bridge, outro)",
            "- Instruments, timbres, and sonic textures to include",
            "- Tempo, key, mood, and emotional arc",
            "Then call generate_media with this enhanced, descriptive prompt.",
            "Focus on high-quality, complete instrumental pieces.",
        ]

    return Agent(
        name="Music Generator Agent",
        agent_id="music_agent",
        model=model,
        tools=[ModelsLabTools(
            api_key=models_lab_api_key,
            wait_for_completion=True,
            file_type=FileType.MP3,
        )],
        description="You are an AI agent that generates music using the ModelsLab API.",
        instructions=instructions,
        markdown=True,
        debug_mode=False,
    )


def generate_track(prompt: str, idx: int):
    """Returns (idx, filename, agent_response_text) or raises."""
    agent = make_agent()
    result: RunOutput = agent.run(prompt)

    if not (result.audio and len(result.audio) > 0):
        raise ValueError("No audio returned from the agent.")

    url = result.audio[0].url
    resp = requests.get(url, timeout=60)
    if not resp.ok:
        raise ValueError(f"Audio download failed (HTTP {resp.status_code})")

    content_type = resp.headers.get("Content-Type", "")
    if "audio" not in content_type:
        raise ValueError(f"Unexpected content type returned: {content_type}")

    save_dir = "audio_generations"
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{save_dir}/music_{uuid4()}.mp3"
    with open(filename, "wb") as f:
        f.write(resp.content)

    return idx, filename, result.content


# ── Session state ─────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ── API key gate ──────────────────────────────────────────
keys_ready = bool(openai_api_key and models_lab_api_key)
if llm_choice == "Claude Sonnet 4.6":
    keys_ready = keys_ready and bool(anthropic_api_key)
elif llm_choice == "Gemini 2.0 Flash":
    keys_ready = keys_ready and bool(google_api_key)

if not keys_ready:
    st.info("Enter your API keys in the sidebar to get started.")
    st.stop()

# ── Generate button ───────────────────────────────────────
if st.button("Generate Music 🎵", type="primary"):
    prompt = build_prompt()
    variation_label = "variation" if num_variations == 1 else f"{num_variations} variations"

    with st.spinner(f"Generating {variation_label}... 🎵"):
        results, errors = [], []

        if num_variations == 1:
            try:
                results.append(generate_track(prompt, 0))
            except Exception as e:
                errors.append(str(e))
                logger.error(e)
        else:
            with ThreadPoolExecutor(max_workers=num_variations) as pool:
                futures = {pool.submit(generate_track, prompt, i): i for i in range(num_variations)}
                for fut, i in futures.items():
                    try:
                        results.append(fut.result())
                    except Exception as e:
                        errors.append(f"Variation {i + 1}: {e}")
                        logger.error(e)

    for err in errors:
        st.error(err)

    if results:
        st.success(f"Generated {len(results)} track(s)! 🎶")
        results.sort(key=lambda x: x[0])

        for i, (_, filename, agent_text) in enumerate(results):
            label = f"Variation {i + 1}" if len(results) > 1 else "Your track"
            st.markdown(f"**{label}**")

            audio_bytes = open(filename, "rb").read()
            st.audio(audio_bytes, format="audio/mp3")
            st.download_button(
                label=f"Download {label}",
                data=audio_bytes,
                file_name=f"generated_music_{i + 1}.mp3",
                mime="audio/mp3",
                key=f"dl_{uuid4()}",
            )

            if agent_text:
                with st.expander("View agent response"):
                    st.markdown(agent_text)

            st.session_state.history.append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "prompt": prompt,
                "filename": filename,
            })

# ── Session history ───────────────────────────────────────
if st.session_state.history:
    st.divider()
    with st.expander(f"Session history ({len(st.session_state.history)} track(s))"):
        for i, item in enumerate(reversed(st.session_state.history)):
            st.markdown(
                f"**[{item['timestamp']}]** "
                f"`{item['prompt'][:80]}{'…' if len(item['prompt']) > 80 else ''}`"
            )
            try:
                audio_bytes = open(item["filename"], "rb").read()
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button(
                    label="Download",
                    data=audio_bytes,
                    file_name=f"track_{i}.mp3",
                    mime="audio/mp3",
                    key=f"hist_{i}_{item['timestamp']}",
                )
            except FileNotFoundError:
                st.caption("File no longer available.")
            st.divider()
