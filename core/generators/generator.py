import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # opcional


class Generator:
    def __init__(self, config: Optional[Dict] = None):
        load_dotenv()
        self.config = config or {}
        self.providers: List[Dict] = sorted(
            (self.config.get("generators", {}).get("providers", []) or []),
            key=lambda p: p.get("priority", 999)
        )
        self.system_context = self._load_context()
        self.cache_ttl = int((self.config.get("generators", {}) or {}).get("cache_ttl_seconds", 120))
        self._cache: Dict[Tuple[str, str], Tuple[float, str]] = {}
        self._rate_usage: Dict[str, Tuple[int, float]] = {}  # provider_name -> (count, window_start)

    def _load_context(self) -> str:
        try:
            with open(self.context_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return "Eres Q•AI, el asistente simbólico central de Q.arz."

    def create(self, prompt: str) -> str:
        # Recorre proveedores por prioridad
        for p in self.providers:
            ptype = (p.get("type") or "").lower()
            model = p.get("model") or "gpt-3.5-turbo"
            host = p.get("host")
            key_env = p.get("apiKeyEnv")
            api_key = os.getenv(key_env) if key_env else None
            pname = p.get("name") or f"{ptype}:{model}"
            # rate limit
            if not self._allow_rate(pname, p):
                continue
            # cache lookup
            cached = self._get_cache(pname, prompt)
            if cached is not None:
                return cached
            try:
                if ptype == "openai":
                    if OpenAI is None:
                        raise RuntimeError("OpenAI SDK not available")
                    if not api_key:
                        raise RuntimeError("OPENAI_API_KEY not set")
                    client = OpenAI(api_key=api_key, base_url=host) if host else OpenAI(api_key=api_key)
                    resp = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": self.system_context},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.7,
                        max_tokens=300,
                    )
                    out = resp.choices[0].message.content.strip()
                    self._set_cache(pname, prompt, out)
                    return out
                elif ptype == "ollama":
                    # REST simple
                    import requests
                    url = f"{host}/api/generate"
                    payload = {"model": model, "prompt": f"{self.system_context}\n\n{prompt}", "stream": False}
                    r = requests.post(url, json=payload, timeout=60)
                    r.raise_for_status()
                    data = r.json()
                    out = (data.get("response") or "").strip() or self._respuesta_simulada(prompt)
                    self._set_cache(pname, prompt, out)
                    return out
                elif ptype == "lmstudio":
                    import requests
                    url = f"{host}/chat/completions"
                    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
                    payload = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": self.system_context},
                            {"role": "user", "content": prompt}
                        ]
                    }
                    r = requests.post(url, json=payload, headers=headers, timeout=60)
                    r.raise_for_status()
                    data = r.json()
                    choices = data.get("choices") or []
                    if choices:
                        out = (choices[0].get("message", {}).get("content") or "").strip()
                        self._set_cache(pname, prompt, out)
                        return out
                    return self._respuesta_simulada(prompt)
                else:
                    continue
            except Exception:
                # intenta siguiente proveedor
                continue
        # sin proveedores válidos: simulado
        return self._respuesta_simulada(prompt)

    # cache helpers
    def _cache_key(self, provider_name: str, prompt: str) -> Tuple[str, str]:
        return (provider_name, prompt.strip())

    def _get_cache(self, provider_name: str, prompt: str) -> Optional[str]:
        if self.cache_ttl <= 0:
            return None
        import time
        key = self._cache_key(provider_name, prompt)
        item = self._cache.get(key)
        if not item:
            return None
        ts, val = item
        if time.time() - ts <= self.cache_ttl:
            return val
        try:
            del self._cache[key]
        except Exception:
            pass
        return None

    def _set_cache(self, provider_name: str, prompt: str, value: str):
        if self.cache_ttl <= 0:
            return
        import time
        key = self._cache_key(provider_name, prompt)
        self._cache[key] = (time.time(), value)

    def _allow_rate(self, provider_name: str, provider: Dict) -> bool:
        import time
        rate = int(provider.get("ratePerMin", 60))
        if rate <= 0:
            return True
        count, window = self._rate_usage.get(provider_name, (0, time.time()))
        now = time.time()
        if now - window >= 60:
            self._rate_usage[provider_name] = (1, now)
            return True
        if count >= rate:
            return False
        self._rate_usage[provider_name] = (count + 1, window)
        return True

    def _respuesta_simulada(self, prompt: str, error_msg: str = "") -> str:
        print(f"[Error no conexion] ⚠️ Modo simulado activado.")
        print(error_msg)
        return f"[Q•AI] No puedo contactar con la fuente ahora."
