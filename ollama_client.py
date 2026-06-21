"""Wrapper for Ollama interactions with a safe fallback to CLI if needed."""
import subprocess
import json
import os

try:
    import ollama
    _HAS_OLLAMA_PY = True
except Exception:
    _HAS_OLLAMA_PY = False

class OllamaClient:
    def __init__(self):
        self.available = _HAS_OLLAMA_PY
        if self.available:
            try:
                # Newer ollama python client may expose a "create" or "Ollama" object; keep minimal
                # We'll use the high-level "chat" function if present.
                self.client = ollama
            except Exception:
                self.client = None
                self.available = False

    def chat(self, model: str, prompt: str, timeout: int = 60):
        """Chat with a local Ollama model. Returns string or None."""
        if self.available and hasattr(self.client, 'chat'):
            try:
                # Best-effort usage of ollama python client
                res = self.client.chat(model=model, messages=[{"role": "user", "content": prompt}])
                # The client may return a string or object
                if isinstance(res, str):
                    return res
                if isinstance(res, dict):
                    # try to extract text
                    return res.get('text') or json.dumps(res)
                # fallback to repr
                return str(res)
            except Exception as e:
                # fallback to CLI below
                pass
        # Fallback: call ollama CLI if installed
        try:
            p = subprocess.run(["ollama", "chat", model, "--stdin"], input=prompt.encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
            if p.returncode == 0:
                return p.stdout.decode('utf-8').strip()
            else:
                raise RuntimeError(p.stderr.decode('utf-8').strip())
        except FileNotFoundError:
            raise RuntimeError("Ollama not installed or ollama-python not available. Install ollama and/or ollama-python.")

    def list_models(self):
        try:
            if self.available and hasattr(self.client, 'list_models'):
                return self.client.list_models()
        except Exception:
            pass
        try:
            p = subprocess.run(["ollama", "list"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return p.stdout.decode('utf-8')
        except Exception:
            return None
