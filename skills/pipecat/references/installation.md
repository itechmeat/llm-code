# Installation (framework, extras, CLI, cloud SDK)

This skill assumes Pipecat is already installed.
Use this page only when you need to set up a fresh environment or add provider/feature extras.

## Prereqs

- Python 3.10+

## Framework: `pipecat-ai`

Base install:

- `pip install pipecat-ai`

Provider/feature extras (pattern used throughout the docs):

- `pip install "pipecat-ai[openai]"`
- `pip install "pipecat-ai[runner]"` (runner utilities)
- You can combine extras if needed (keep them explicit).

## CLI: `pipecat-ai-cli`

Recommended for scaffolding/ops (`pipecat init`, `pipecat tail`, `pipecat cloud ...`).

- `uv tool install pipecat-ai-cli`
  - or `pipx install pipecat-ai-cli`

## Pipecat Cloud SDK: `pipecatcloud`

Install when you want to start sessions via Python code:

- `pip install pipecatcloud`

## Verification

- CLI: `pipecat --version`
- Python import sanity check:
  - `python -c "import pipecat"`
