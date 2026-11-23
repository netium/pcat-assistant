# pcat-assistant

A Pipecat personal voice assistant with local speech processing, an OpenAI-compatible
LLM, and function-calling tools.

## Architecture

- **Pipeline**: local Whisper MLX STT → OpenAI-compatible chat completions → local Pocket TTS
- **STT**: `WhisperSTTServiceMLX`, using English and defaulting to
  `mlx-community/whisper-large-v3-turbo`
- **LLM**: `OpenAILLMService`, defaulting to `step-3.7-flash`
- **TTS**: `PocketTTSService` with the `alba` voice
- **Turn detection**: Silero VAD with transcription-based user-turn start detection
- **Transports**: SmallWebRTC and Daily (WebRTC)

The assistant is instructed to prefer its registered tools over built-in knowledge and to
keep responses concise.

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/)
- macOS on Apple Silicon for the default MLX speech-to-text service
- An OpenAI-compatible LLM API key and endpoint

## Setup

1. **Install dependencies** from the repository root:

   ```bash
   uv sync
   ```

2. **Create a `.env` file** in the repository root:

   ```dotenv
   OPENAI_API_KEY=your-api-key
   OPENAI_BASE_URL=https://your-openai-compatible-endpoint
   OPENAI_LLM_MODEL=step-3.7-flash

   WEATHERAPI_API_KEY=your-weatherapi-key
   TAVILY_API_KEY=your-tavily-key

   WHISPER_MLX_MODEL_PATH=mlx-community/whisper-large-v3-turbo
   ```

   | Variable | Purpose |
   | --- | --- |
   | `OPENAI_API_KEY` | Authenticates the LLM service. |
   | `OPENAI_BASE_URL` | Selects the OpenAI-compatible endpoint; optional when using the provider default. |
   | `OPENAI_LLM_MODEL` | Selects the model; defaults to `step-3.7-flash`. |
   | `WEATHERAPI_API_KEY` | Required when the weather tool calls WeatherAPI. |
   | `TAVILY_API_KEY` | Required when the web-search tool calls Tavily. |
   | `WHISPER_MLX_MODEL_PATH` | Optional local Whisper model override. |

   `bot.py` loads `.env` with `override=True`, so its values take precedence over exported
   shell variables. Deepgram and Cartesia credentials are not used by the active pipeline.

3. **Run the bot**:

   ```bash
   uv run bot.py
   ```

   The connecting web or mobile client selects SmallWebRTC or Daily. The local speech
   libraries may download their models on first use.

## LLM tools

All tools are defined in `tools.py` and registered through `LLMContext`:

| Tool | Behavior |
| --- | --- |
| `get_current_date` | Returns the local date and weekday. |
| `get_current_location` | Returns a stubbed location (`Chengdu`). |
| `get_weather` | Retrieves current, forecast, or historical weather from WeatherAPI. |
| `general_web_search` | Searches the web through Tavily. |
| `open_window` | Simulates opening a window by a requested percentage. |
| `launch_app` | Simulates launching a named application. |

## Project structure

```text
pcat-assistant/
├── bot.py           # Bot runtime, pipeline, transports, and local speech services
├── tools.py         # LLM function-call tool definitions
├── main.py          # Unused scaffold stub; not the bot entry point
├── pyproject.toml   # Dependencies and Ruff configuration
├── uv.lock          # Locked dependency versions
├── Dockerfile       # Container build (currently incomplete; see below)
└── pcc-deploy.toml  # Pipecat Cloud deployment settings
```

## Development

```bash
uv run ruff check .
uv run pyright
```

There is currently no automated test suite.

## Deploying to Pipecat Cloud

`pcc-deploy.toml` contains deployment settings, but the current container configuration is
not ready to run the active bot: the `Dockerfile` copies only `bot.py`, while the bot also
imports `tools.py`. A deployment must also provide a runtime compatible with the selected
local STT/TTS services; in particular, the default Whisper MLX service requires Apple
Silicon and is not suitable for a typical Linux cloud container.

Before deploying, copy all required Python modules into the image and select speech
services supported by the deployment environment. For the general deployment workflow, see
the [Pipecat Quickstart Guide](https://docs.pipecat.ai/getting-started/quickstart#step-2-deploy-to-production)
and [Pipecat Cloud Documentation](https://docs.pipecat.ai/deployment/pipecat-cloud/introduction).

## Learn More

- [Pipecat Documentation](https://docs.pipecat.ai/)
- [Pipecat GitHub](https://github.com/pipecat-ai/pipecat)
- [Pipecat Examples](https://github.com/pipecat-ai/pipecat-examples)
- [Discord Community](https://discord.gg/pipecat)