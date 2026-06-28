# AGENTS.md

## Project
Pipecat voice agent (`pipecat-quickstart` / `pcat-assistant`). Cascade pipeline:
STT (Deepgram) → LLM (OpenAI-compatible, default `step-3.7-flash`) → TTS (Cartesia).
Transports: SmallWebRTC and Daily. Domain: in-vehicle voice assistant.

## Entry points
- **Bot runtime**: `bot.py` — run with `uv run bot.py`. This is the real entrypoint.
  `pipecat.runner.run.main()` → `bot()` → `run_bot(transport, runner_args)`.
- `main.py` is a leftover `Hello from ...` stub. **Not** the entrypoint — ignore it.
- `pcc-deploy.toml` is the Pipecat Cloud deploy config (`agent_name = "pcat-assistant"`,
  `secret_set = "12345678"`, `agent_profile = "agent-1x"`, `min_agents = 1`).

## Tooling
- Python 3.12 (`.python-version`); `requires-python = ">=3.11"`.
- Package manager is **uv**. `uv sync` to install; `uv.lock` is committed.
- Dev deps (`pyright`, `ruff`) live in `[dependency-groups] dev` in `pyproject.toml`.

## Commands
- Install: `uv sync`
- Run bot: `uv run bot.py` (transport is chosen by the connecting client;
  web/mobile pick at connect time, telephony connects to `/ws`)
- Lint: `uv run ruff check .` (config: `select = ["I", "UP"]`, `line-length = 100`)
- Typecheck: `uv run pyright`
- There is **no test suite** — do not invent one unless asked.

## Gotchas
- `bot.py:46` imports via a **bare** `from tools import ...`. `tools.py` must stay at the
  repo root with that exact module name, or the import will break at runtime.
- `tools.py` defines four function-call tools wired into `LLMContext`
  (`get_current_location`, `get_current_weather`, `open_window`, `launch_app`).
  The hardcoded return values are stubs — replace them when wiring real backends.
- The LLM system instruction is hardcoded at `bot.py:89`
  (`"You are a vehicle voice assistant. Your reply shall be concise."`) — domain-specific,
  not generic.
- `bot.py:54` calls `load_dotenv(override=True)`, so `.env` always wins over shell env vars.
- The `Dockerfile` only does `COPY ./bot.py bot.py`. **It does not copy `tools.py`.**
  Adding new top-level Python files requires updating the Dockerfile, otherwise Pipecat
  Cloud deploys will fail with `ModuleNotFoundError: tools`.
- `bot.py` imports both `OpenAIResponsesLLMService` (unused, line 41) and
  `OpenAILLMService` (used, line 45/84). Leftover from the scaffold; safe to drop the
  unused import when cleaning up.
- There is no `.env.example` despite the README referencing one. Keep `.env` keys in
  sync with what `bot.py` reads: `DEEPGRAM_API_KEY`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`,
  `OPENAI_LLM_MODEL`, `CARTESIA_API_KEY`. `CARTESIA_VOICE_ID` has a default in code.

## Things Shall Do

- The python code shall follow the python code convention.
- All the tools defintion used by LLM (set via LLMContext) shall be defined in tools.py.
- Every change shall be happened on a branch other than the "master" or "main" branch.