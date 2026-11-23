# AGENTS.md

## Project
Pipecat voice agent (repository/deployment name `pcat-assistant`; Python project name
`pipecat-quickstart`). The active cascade pipeline is:
local Whisper MLX STT → OpenAI-compatible chat completions (default `step-3.7-flash`) →
local Pocket TTS (`alba` voice). Transports are SmallWebRTC and Daily.

The system prompt defines a concise, tool-first personal voice assistant. Window and app
control tools remain vehicle-style stubs, but the active prompt is no longer vehicle-specific.

## Entry points
- **Bot runtime**: `bot.py` — run with `uv run bot.py`. This is the real entrypoint:
  `pipecat.runner.run.main()` → `bot()` → `run_bot(transport, runner_args)`.
- `main.py` is a leftover `Hello from ...` stub. **Not** the entrypoint; ignore it.
- `pcc-deploy.toml` is the Pipecat Cloud deploy config (`agent_name = "pcat-assistant"`,
  `secret_set = "12345678"`, `agent_profile = "agent-1x"`, `min_agents = 1`).

## Tooling
- `pyproject.toml` requires Python `>=3.11`. There is no committed `.python-version`.
- Package manager is **uv**. Use `uv sync`; `uv.lock` is committed.
- Dev dependencies (`pyright`, `ruff`) live in `[dependency-groups] dev`.

## Commands
- Install: `uv sync`
- Run bot: `uv run bot.py` (the connecting web/mobile client selects SmallWebRTC or Daily)
- Lint: `uv run ruff check .` (config: `select = ["I", "UP"]`, `line-length = 100`)
- Typecheck: `uv run pyright`
- There is **no test suite** — do not invent one unless asked.

## Runtime configuration
- `bot.py:59` calls `load_dotenv(override=True)`, so `.env` values override shell variables.
- Active environment variables are `OPENAI_API_KEY`, `OPENAI_BASE_URL`,
  `OPENAI_LLM_MODEL`, `WEATHERAPI_API_KEY`, `TAVILY_API_KEY`, and the optional
  `WHISPER_MLX_MODEL_PATH` (default `mlx-community/whisper-large-v3-turbo`).
- `OPENAI_MODEL` is only printed by a log statement at `bot.py:116`; it does not select the
  model. The model setting reads `OPENAI_LLM_MODEL` at `bot.py:122`.
- Deepgram and Cartesia construction is commented out. Their API keys and voice settings
  are not required by the active pipeline.
- The default STT uses MLX and English, and therefore targets macOS on Apple Silicon.
  Pocket TTS runs locally with the hardcoded `alba` voice.

## Gotchas
- `bot.py:57` imports through a **bare** `from tools import ...`. Keep `tools.py` at the
  repository root with that exact module name, or runtime imports will break.
- `tools.py` defines six tools registered by `build_tools_list()` and `LLMContext`:
  `get_current_date`, `get_current_location`, `get_weather`, `open_window`, `launch_app`,
  and `general_web_search`.
- Location (`Chengdu`), window control, and app launching are stubs. Weather uses
  WeatherAPI; web search uses Tavily; the date tool uses local system time.
- The LLM system instruction is hardcoded at `bot.py:123`. It tells the assistant to prefer
  tools over built-in knowledge and reply concisely. `supports_developer_role` is disabled,
  although the client-ready greeting currently inserts a `developer` message.
- The `Dockerfile` only does `COPY ./bot.py bot.py`. **It does not copy `tools.py`.**
  Adding or renaming top-level Python modules requires updating the Dockerfile. The active
  local speech services also need a compatible deployment runtime; Whisper MLX is not
  suitable for a typical Linux Pipecat Cloud container.
- There is no `.env.example`. Create `.env` manually and keep documentation synchronized
  with the variables read by `bot.py` and `tools.py`.

## Things shall do
- Follow standard Python conventions.
- Define every LLM tool registered through `LLMContext` in `tools.py`.
- Make every change on a branch other than `master` or `main`.
