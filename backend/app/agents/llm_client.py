import os
from typing import Optional, Dict, Any, List
from google import genai
from google.genai import types
from app.config import settings
from app.agents.tool_registry import get_gemini_tool_declarations

class GeminiClientWrapper:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        self.model = model or settings.GEMINI_MODEL or "gemini-3.1-flash-lite"
        self._client: Optional[genai.Client] = None
        if self.api_key:
            self._client = genai.Client(api_key=self.api_key)

    def is_configured(self) -> bool:
        return bool(self.api_key and self._client)

    def get_client(self) -> genai.Client:
        if not self._client:
            raise ValueError(
                "Gemini API Key is not configured. Please set the GEMINI_API_KEY in the Settings screen or .env file."
            )
        return self._client

    def build_tools_config(self) -> types.GenerateContentConfig:
        declarations = get_gemini_tool_declarations()
        gemini_decls = []
        for d in declarations:
            gemini_decls.append(types.FunctionDeclaration(
                name=d["name"],
                description=d["description"],
                parameters=d["parameters"]
            ))
            
        tool = types.Tool(function_declarations=gemini_decls)
        
        return types.GenerateContentConfig(
            tools=[tool],
            temperature=0.1,  # Low temperature for analytical precision
            max_output_tokens=2048,
        )

    def test_connection(self) -> Dict[str, Any]:
        """Test API key validity and model accessibility."""
        if not self.is_configured():
            return {"success": False, "message": "API Key is missing."}
        try:
            client = self.get_client()
            resp = client.models.generate_content(
                model=self.model,
                contents="Ping. Respond with 'InsightOps Ready'."
            )
            return {"success": True, "message": resp.text.strip(), "model": self.model}
        except Exception as e:
            return {"success": False, "message": str(e), "model": self.model}
