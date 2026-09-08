import logging
from openai import OpenAI, APIConnectionError, APITimeoutError, InternalServerError
from app.config import get_settings

logger = logging.getLogger(__name__)

class NavigatorClient:
    """OpenAI-compatible client for UF NaviGator AI Toolkit."""
    
    def __init__(self):
        settings = get_settings()
        self.model = settings.navigator_model or "gpt-oss-20b"
        self.client = OpenAI(
            api_key=settings.navigator_toolkit_api_key,
            base_url=settings.navigator_base_url,
            timeout=30.0,
            max_retries=1,
        )
    
    def chat_completion(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        tool_choice: str | dict = "auto",
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> dict:
        """Send chat completion request with optional tool calling."""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice
        
        try:
            logger.info(f"Sending chat completion request to NaviGator API using model {self.model}")
            response = self.client.chat.completions.create(**kwargs)
            logger.info("Received chat completion response")
            return response
        except (APIConnectionError, APITimeoutError, InternalServerError) as e:
            logger.error(f"Transient error with NaviGator API: {e.__class__.__name__} - {str(e)}")
            raise
        except Exception as e:
            logger.error(f"NaviGator API error: {e.__class__.__name__} - {str(e)}")
            raise
    
    def is_configured(self) -> bool:
        """Check if API key is set."""
        settings = get_settings()
        return bool(settings.navigator_toolkit_api_key)
    
    def check_health(self) -> str:
        """Check if NaviGator API is reachable."""
        if not self.is_configured():
            return "unconfigured"
        try:
            models = self.client.models.list()
            return "ok"
        except Exception as e:
            logger.warning(f"NaviGator health check failed: {e.__class__.__name__} - {str(e)}")
            return "error"
