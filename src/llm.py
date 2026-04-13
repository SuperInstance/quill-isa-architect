"""
Quill LLM Module — Multi-Provider Model Router
==============================================
Routes requests to any OpenAI-compatible API.
Auto-detects provider from base URL and sets appropriate parameters.
Implements fallback chain on errors.

Zero dependencies — uses only stdlib (urllib, json).

Providers supported:
  - OpenAI (gpt-4o, gpt-4-turbo, etc.)
  - Anthropic (claude-sonnet, claude-opus, etc.)
  - DeepSeek (deepseek-chat, deepseek-reasoner)
  - Google (gemini-pro, gemini-ultra)
  - Z.AI (glm-4, glm-5)
  - Local (Ollama, LM Studio, vLLM, llama.cpp)
  - Any OpenAI-compatible endpoint
"""

import json
import urllib.request
import urllib.error
from typing import Optional
from datetime import datetime, timezone


# Provider detection patterns
PROVIDERS = {
    "openai": {
        "patterns": ["api.openai.com", "openai"],
        "default_model": "gpt-4o",
        "temperature_range": (0.0, 2.0),
        "max_context": 128000,
    },
    "anthropic": {
        "patterns": ["anthropic", "claude"],
        "default_model": "claude-sonnet-4-20250514",
        "temperature_range": (0.0, 1.0),
        "max_context": 200000,
    },
    "deepseek": {
        "patterns": ["deepseek"],
        "default_model": "deepseek-chat",
        "temperature_range": (0.0, 2.0),
        "max_context": 64000,
    },
    "google": {
        "patterns": ["generativelanguage.googleapis", "gemini"],
        "default_model": "gemini-2.5-pro",
        "temperature_range": (0.0, 2.0),
        "max_context": 1000000,
    },
    "zai": {
        "patterns": ["z.ai", "glm", "chatglm"],
        "default_model": "glm-5",
        "temperature_range": (0.0, 1.0),
        "max_context": 128000,
    },
    "local": {
        "patterns": ["localhost", "127.0.0.1", "lmstudio", "ollama", "vllm"],
        "default_model": "local-model",
        "temperature_range": (0.0, 2.0),
        "max_context": 32768,
    },
}


def detect_provider(base_url: str) -> str:
    """Auto-detect provider from base URL. Returns provider key."""
    url_lower = base_url.lower()
    for provider, info in PROVIDERS.items():
        for pattern in info["patterns"]:
            if pattern in url_lower:
                return provider
    return "openai"  # Default: assume OpenAI-compatible


def route_model(model: str, base_url: str) -> dict:
    """
    Route a model request to the appropriate provider configuration.
    
    Returns a dict with:
      - provider: detected provider name
      - model: model name to send
      - temperature: recommended temperature
      - max_tokens: recommended max tokens
      - headers: provider-specific headers
    
    This is the core routing function — inspired by Lucineer/git-agent's
    routeModel() pattern but extended with auto-detection and defaults.
    """
    provider = detect_provider(base_url)
    info = PROVIDERS.get(provider, PROVIDERS["openai"])

    headers = {
        "Content-Type": "application/json",
        "Authorization": None,  # Set by caller with actual API key
    }

    return {
        "provider": provider,
        "model": model or info["default_model"],
        "temperature": info["temperature_range"][1] * 0.35,  # 35% of max
        "max_tokens": min(4096, info["max_context"] // 4),
        "max_context": info["max_context"],
        "headers": headers,
    }


def chat(
    base_url: str,
    api_key: str,
    model: str,
    message: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    timeout: int = 120,
) -> dict:
    """
    Send a chat completion request.
    
    Returns dict with:
      - content: str — the model's response text
      - model: str — actual model used
      - provider: str — detected provider
      - usage: dict — token usage if available
      - latency_ms: int — round-trip time
    
    Raises:
      RuntimeError: On API errors (with status code and body)
      urllib.error.URLError: On network errors
    """
    routing = route_model(model, base_url)
    start = datetime.now(timezone.utc)

    payload = {
        "model": routing["model"],
        "messages": [],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    if system_prompt:
        payload["messages"].append({
            "role": "system",
            "content": system_prompt,
        })

    payload["messages"].append({
        "role": "user",
        "content": message,
    })

    url = f"{base_url}/chat/completions"
    data = json.dumps(payload).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            latency = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)

            return {
                "content": result["choices"][0]["message"]["content"],
                "model": result.get("model", routing["model"]),
                "provider": routing["provider"],
                "usage": result.get("usage", {}),
                "latency_ms": latency,
                "status": "success",
            }

    except urllib.error.HTTPError as e:
        latency = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
        body = e.read().decode("utf-8", errors="replace")[:500]
        return {
            "content": "",
            "model": routing["model"],
            "provider": routing["provider"],
            "usage": {},
            "latency_ms": latency,
            "status": f"http_error_{e.code}",
            "error": f"HTTP {e.code}: {body}",
        }

    except urllib.error.URLError as e:
        latency = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
        return {
            "content": "",
            "model": routing["model"],
            "provider": routing["provider"],
            "usage": {},
            "latency_ms": latency,
            "status": "unreachable",
            "error": f"Cannot reach {base_url}: {e.reason}",
        }


def chat_with_fallback(
    base_url: str,
    api_key: str,
    model: str,
    message: str,
    system_prompt: Optional[str] = None,
    fallback_models: Optional[list] = None,
    **kwargs,
) -> dict:
    """
    Try primary model, fall back to alternatives on failure.
    
    Args:
        fallback_models: List of (base_url, model) tuples to try on failure.
                        If None, no fallback.
    
    Returns the first successful response, or the last error.
    """
    result = chat(base_url, api_key, model, message, system_prompt, **kwargs)
    
    if result["status"] == "success" or not fallback_models:
        return result

    # Try fallbacks
    for fb_url, fb_model in fallback_models:
        result = chat(fb_url, api_key, fb_model, message, system_prompt, **kwargs)
        if result["status"] == "success":
            result["fallback_from"] = f"{model}@{base_url}"
            return result

    return result  # Return last error
