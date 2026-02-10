# CLIProxyAPI Setup

[CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI) routes API calls through your Claude Max subscription instead of consuming pay-per-token API credits. The proxy exposes an OpenAI-compatible endpoint locally that DSPy/LiteLLM can target.

Full docs: https://help.router-for.me/

## Install

```bash
brew install cliproxyapi
```

## Authenticate

```bash
cliproxyapi --claude-login
```

This opens an OAuth flow in your browser and saves tokens to `~/.cli-proxy-api/`.

## Start the proxy

```bash
brew services start cliproxyapi
```

The proxy runs on `http://localhost:8317` by default. Config lives at `/opt/homebrew/etc/cliproxyapi.conf`.

## Verify

```bash
# Grab the API key from the config
grep 'api-keys' -A1 /opt/homebrew/etc/cliproxyapi.conf

# Test with curl
curl -X POST http://127.0.0.1:8317/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_API_KEY>" \
  -d '{"model":"claude-sonnet-4-5-20250929","messages":[{"role":"user","content":"Say hello"}]}'
```

## How it connects to DSPy

In `config.py`, all `dspy.LM` instances use the `openai/` model prefix (since the proxy is OpenAI-compatible) with `api_base` and `api_key` pointing at the local proxy:

```python
PROXY_BASE = "http://localhost:8317/v1"
PROXY_KEY = "<key from cliproxyapi.conf>"

GENERATOR_LM = dspy.LM(
    "openai/claude-haiku-4-5-20251001",
    api_base=PROXY_BASE,
    api_key=PROXY_KEY,
)
```

## Manage the service

```bash
brew services start cliproxyapi    # start
brew services stop cliproxyapi     # stop
brew services restart cliproxyapi  # restart
```
