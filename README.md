# 🎶 AI Music Generator Agent

A Streamlit web app that generates original music tracks from natural language descriptions. Describe what you want — genre, mood, tempo, instruments — and the agent enhances your prompt with an LLM before sending it to the ModelsLab music generation API. Play and download the result directly in the browser.

## Features

- **Prompt Builder UI** — structured controls for genre, mood, tempo, duration, and instruments that assemble into a rich generation prompt automatically
- **Quick-start templates** — 7 curated presets (orchestral, lo-fi, jazz, ambient, etc.) to get started instantly
- **Multi-LLM prompt enhancement** — choose GPT-4o, Claude Sonnet 4.6, or Gemini 2.0 Flash to enrich your prompt before generation; or bypass the LLM and send your prompt directly
- **Multi-variation generation** — generate up to 3 parallel variations of the same prompt and pick the best one
- **Inline playback & download** — listen to generated tracks in the browser and download as MP3
- **Agent response viewer** — inspect the enhanced prompt the LLM sent to ModelsLab
- **Session history** — replay or re-download any track generated during the current session
- **`.env` support** — pre-fill API keys from environment variables so you don't re-enter them each session

## Prerequisites

You will need API keys for the following services:

| Key | Required | Get it |
|-----|----------|--------|
| OpenAI | Always (used as the agent backbone when Gemini/Claude aren't chosen) | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| ModelsLab | Always (music generation) | [modelslab.com/dashboard/api-keys](https://modelslab.com/dashboard/api-keys) |
| Anthropic | Only when "Claude Sonnet 4.6" is selected | [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys) |
| Google | Only when "Gemini 2.0 Flash" is selected | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |

## Installation

```bash
git clone https://github.com/your-username/ai-music-generator-agent
cd ai-music-generator-agent
pip install -r requirements.txt
```

**Optional:** copy `.env.example` to `.env` and fill in your API keys so the sidebar fields are pre-populated:

```bash
cp .env.example .env
```

## Running

```bash
streamlit run music_generator_agent.py
```

The app opens at `http://localhost:8501`.

## Usage

1. **Enter API keys** in the sidebar (or set them in `.env` beforehand).
2. **Choose a prompt enhancement model** — GPT-4o, Claude Sonnet 4.6, Gemini 2.0 Flash, or None.
3. **Pick a template** from the quick-start dropdown, or leave it on "Custom prompt…".
4. **Fill in the Prompt Builder** — genre, mood, tempo, duration, and instruments.
5. **Add any extra details** in the free-text area.
6. **Set variations** (1–3) if you want parallel alternatives.
7. Click **Generate Music 🎵** and wait for your track.
8. Play inline, expand "View agent response" to see the enhanced prompt, or download the MP3.

## Project Structure

```
ai_music_generator_agent/
├── music_generator_agent.py   # Streamlit app and agent logic
├── requirements.txt
├── .env.example
└── audio_generations/         # Created at runtime; holds generated MP3s
```

## Tech Stack

- [Streamlit](https://streamlit.io/) — web UI
- [Agno](https://github.com/agno-agi/agno) — agent framework
- [ModelsLab](https://modelslab.com/) — music generation API
- [OpenAI GPT-4o](https://platform.openai.com/) / [Anthropic Claude](https://anthropic.com/) / [Google Gemini](https://ai.google.dev/) — LLM prompt enhancement
