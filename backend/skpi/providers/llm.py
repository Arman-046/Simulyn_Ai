import json
from openai import OpenAI
from backend.config import FIREWORKS_API_KEY, FIREWORKS_BASE_URL, MODEL_NAME
from typing import Dict, Any, List

def call_llm(prompt: str, json_mode: bool = True) -> Dict[str, Any]:
    """
    Calls the Fireworks LLM. 
    Strictly follows the Zero Fake Functionality rule: all responses are dynamically computed.
    """
    if not FIREWORKS_API_KEY:
        raise ValueError("FIREWORKS_API_KEY is not set. Cannot execute dynamic LLM pipeline.")

    client = OpenAI(base_url=FIREWORKS_BASE_URL, api_key=FIREWORKS_API_KEY)
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"} if json_mode else None,
            max_tokens=4000,
            temperature=0.3,
            timeout=15.0,
        )
        content = response.choices[0].message.content.strip()
        if json_mode:
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            return json.loads(content)
        return {"text": content}
    except Exception as e:
        print(f"[SKPI LLM Error] {str(e)}")
        raise e
