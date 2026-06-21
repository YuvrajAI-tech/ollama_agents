"""Simple Hugging Face client to call a model or space for chat-like responses."""
import os
import requests
from huggingface_hub import InferenceApi

class HFClient:
    def __init__(self, hf_token=None):
        self.token = hf_token or os.environ.get('HUGGINGFACE_API_TOKEN')

    def chat(self, model_or_space: str, prompt: str):
        """If model_or_space looks like a model id, use InferenceApi; if a space (contains '/'), try the spaces inference endpoint."""
        if not model_or_space:
            raise ValueError("No Hugging Face model or space provided")
        # If it looks like a huggingface.co/spaces/ owner/space
        if '/' in model_or_space and not model_or_space.startswith('http'):
            # try model inference first
            try:
                inf = InferenceApi(repo_id=model_or_space, token=self.token)
                out = inf(inputs=prompt)
                if isinstance(out, dict) and 'error' in out:
                    raise RuntimeError(out['error'])
                if isinstance(out, str):
                    return out
                if isinstance(out, list):
                    return '\n'.join(map(str, out))
                if isinstance(out, dict):
                    return str(out)
            except Exception:
                pass
        # As a last resort, try the spaces inference URL
        # Note: Spaces may require a custom API; this attempt uses the public inference endpoint
        url = f"https://huggingface.co/api/spaces/{model_or_space}/run/predict"
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        try:
            r = requests.post(url, headers=headers, json={"data": [prompt]}, timeout=30)
            r.raise_for_status()
            j = r.json()
            # Spaces responses vary; try to extract a text result
            if isinstance(j, dict):
                # Many spaces return {'data': [...]}
                data = j.get('data') or j
                if isinstance(data, list):
                    return '\n'.join(map(str, data))
                return str(data)
            return str(j)
        except Exception as e:
            raise RuntimeError(f"Hugging Face call failed: {e}")
