## Setup (Q•Agent)

### Requirements

- Python 3.10+
- Windows (primary), Linux/Mac (planned)

### Install

```bash
git clone https://github.com/Q-YZX0/QarzAI
cd QarzAI
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py
```

### Configuration

Edit `core/config/qai_config.json`:

- `modo`: "texto" or "voz"
- `voz_engine`: "whisper" or "vosk"
- `reflejo_sistemico`: true/false for autonomous reflection
- `permissions_whitelist`: map of module_id -> list of permissions to auto-grant

### Generators (Multi-API)

Configure providers in `core/config/qai_config.json` under `generators.providers`:

```json
{
  "name": "openai-gpt",
  "type": "openai",
  "host": "https://api.openai.com/v1",
  "apiKeyEnv": "OPENAI_API_KEY",
  "model": "gpt-3.5-turbo",
  "priority": 1
}
```

Supported `type` values: `openai`, `ollama`, `lmstudio`. The assistant tries providers in ascending `priority` order; missing keys or failures automatically fall back to the next provider. Set env vars accordingly.


