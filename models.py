"""Model presets and provider configuration"""
MODEL_PRESETS = [
    {"name": "Ollama - llama2", "id": "llama2"},
    {"name": "Ollama - alpaca", "id": "alpaca"},
    {"name": "HuggingFace - distilgpt2", "id": "distilgpt2"},
    {"name": "HuggingFace - bloomz", "id": "bigscience/bloomz"},
]

PROVIDERS = ["ollama", "huggingface"]
