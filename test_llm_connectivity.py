import os
from dotenv import load_dotenv
load_dotenv()
from utils.llm_clients import get_llm_client

LLMS = [
    {"provider": "groq", "model": "llama3-70b-8192"},
    {"provider": "groq", "model": "moonshotai/kimi-k2-instruct"},
    {"provider": "openrouter", "model": "google/gemma-3-27b-it:free"},
    {"provider": "openrouter", "model": "mistralai/mistral-7b-instruct:free"}
]

PROMPT = "What is the capital of France?"

def mask_key(key):
    if not key or len(key) < 10:
        return key
    return key[:6] + '...' + key[-4:]

def main():
    print("Testing LLM connectivity and response:\n")
    print("Loaded API keys:")
    print("  GROQ_API_KEY:", mask_key(os.environ.get("GROQ_API_KEY")))
    print("  GOOGLE_GEMINI_API_KEY:", mask_key(os.environ.get("GOOGLE_GEMINI_API_KEY")))
    print("  OPENROUTER_API_KEY:", mask_key(os.environ.get("OPENROUTER_API_KEY")))
    print()
    for llm in LLMS:
        print(f"Testing {llm['provider']} | {llm['model']}...")
        try:
            client = get_llm_client(llm["provider"], llm["model"])
            response = client.generate(PROMPT)
            print(f"  Response: {response[:200]}\n")
        except Exception as e:
            print(f"  ERROR: {e}\n")

if __name__ == "__main__":
    main() 