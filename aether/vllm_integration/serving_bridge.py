"""
AETHER Serving Bridge
Provides a unified interface that works with both:
1. External API (OpenAI/current approach) - for development
2. Self-hosted vLLM server - for production/continuous training

Uses existing vLLM code:
- vllm/entrypoints/openai/ (OpenAI-compatible server)
- vllm/entrypoints/llm.py (offline inference)
- vllm/lora/ (Multi-LoRA for framework personalities)

This is the bridge that lets AETHER seamlessly switch between
external APIs and self-hosted models without changing any training code.
"""

import os
import json
import subprocess
import time
from typing import Optional, Generator
from dataclasses import dataclass

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .config import AetherServingConfig, COMPUTE_PROVIDERS


class ServingBridge:
    """
    Unified serving interface for AETHER.
    
    Automatically detects whether a local vLLM server is running
    and routes requests accordingly. Falls back to external API.
    """
    
    def __init__(self, config: Optional[AetherServingConfig] = None):
        self.config = config or AetherServingConfig()
        self._client = None
        self._mode = None  # "local_vllm", "external_api"
        self._server_process = None
        
    @property
    def client(self) -> "OpenAI":
        if self._client is None:
            self._detect_and_connect()
        return self._client
    
    @property
    def mode(self) -> str:
        if self._mode is None:
            self._detect_and_connect()
        return self._mode
    
    def _detect_and_connect(self):
        """Detect available serving backend and connect."""
        
        # Try local vLLM server first
        local_url = self.config.get_openai_base_url()
        if self._check_server(local_url):
            self._client = OpenAI(
                api_key="EMPTY",
                base_url=local_url,
            )
            self._mode = "local_vllm"
            return
        
        # Fall back to external API
        api_key = os.environ.get("OPENAI_API_KEY")
        base_url = os.environ.get("OPENAI_BASE_URL")
        
        if api_key:
            kwargs = {"api_key": api_key}
            if base_url:
                kwargs["base_url"] = base_url
            self._client = OpenAI(**kwargs)
            self._mode = "external_api"
            return
        
        raise RuntimeError(
            "No serving backend available. Either start a vLLM server "
            "or set OPENAI_API_KEY environment variable."
        )
    
    def _check_server(self, base_url: str) -> bool:
        """Check if a vLLM server is running at the given URL."""
        try:
            import requests
            resp = requests.get(f"{base_url}/models", timeout=2)
            return resp.status_code == 200
        except Exception:
            return False
    
    def generate(
        self,
        messages: list,
        model: str = "gpt-4.1-nano",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        framework: Optional[str] = None,  # "stratify" or "principia"
        stream: bool = False,
    ) -> str:
        """
        Generate a response using the best available backend.
        
        When using local vLLM with Multi-LoRA:
        - framework="stratify" routes to Stratify's LoRA adapter
        - framework="principia" routes to Principia's LoRA adapter
        
        When using external API:
        - Framework personality is embedded in the system prompt
        """
        
        kwargs = {
            "model": model if self.mode == "external_api" else self._get_local_model(),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # Add LoRA adapter if using local vLLM with Multi-LoRA
        if self.mode == "local_vllm" and framework:
            adapter = self._get_lora_adapter(framework)
            if adapter:
                kwargs["extra_body"] = {"lora_request": adapter}
        
        if stream:
            return self._generate_stream(**kwargs)
        
        response = self.client.chat.completions.create(**kwargs)
        
        # Extract reasoning content if available (vLLM reasoning parser)
        choice = response.choices[0]
        reasoning = getattr(choice.message, 'reasoning_content', None)
        content = choice.message.content
        
        if reasoning:
            return f"<think>{reasoning}</think>\n{content}"
        return content
    
    def _generate_stream(self, **kwargs) -> Generator:
        """Stream responses for real-time monitoring."""
        kwargs["stream"] = True
        stream = self.client.chat.completions.create(**kwargs)
        
        full_text = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_text += text
                yield text
        
        return full_text
    
    def _get_local_model(self) -> str:
        """Get the model name from the local vLLM server."""
        try:
            models = self.client.models.list()
            return models.data[0].id
        except Exception:
            return self.config.model.model_name
    
    def _get_lora_adapter(self, framework: str) -> Optional[dict]:
        """Get LoRA adapter config for a framework."""
        if not self.config.lora.enable_lora:
            return None
        
        adapter_map = {
            "stratify": self.config.lora.stratify_adapter,
            "principia": self.config.lora.principia_adapter,
        }
        
        adapter_path = adapter_map.get(framework)
        if adapter_path:
            return {"lora_name": framework, "lora_path": adapter_path}
        return None
    
    def start_local_server(self) -> bool:
        """
        Start a local vLLM server using existing vLLM CLI.
        
        This uses vllm/entrypoints/cli/ which is already implemented.
        No need to recreate any serving code.
        """
        cmd = self.config.get_full_serve_command()
        print(f"Starting vLLM server: {cmd}")
        
        try:
            self._server_process = subprocess.Popen(
                cmd.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            # Wait for server to be ready
            for _ in range(60):
                if self._check_server(self.config.get_openai_base_url()):
                    self._mode = "local_vllm"
                    self._client = OpenAI(
                        api_key="EMPTY",
                        base_url=self.config.get_openai_base_url(),
                    )
                    print("vLLM server started successfully!")
                    return True
                time.sleep(2)
            
            print("Server failed to start within timeout")
            return False
            
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
    
    def stop_local_server(self):
        """Stop the local vLLM server."""
        if self._server_process:
            self._server_process.terminate()
            self._server_process.wait()
            self._server_process = None
            self._mode = None
            self._client = None
    
    def get_status(self) -> dict:
        """Get the current serving status."""
        return {
            "mode": self.mode,
            "model": self.config.model.model_name if self.mode == "local_vllm" else "external_api",
            "features": {
                "prefix_caching": self.config.prefix_cache.enable and self.mode == "local_vllm",
                "multi_lora": self.config.lora.enable_lora and self.mode == "local_vllm",
                "streaming": self.config.enable_streaming,
                "reasoning_parser": self.config.model.reasoning_parser if self.mode == "local_vllm" else "n/a",
                "continuous_batching": self.mode == "local_vllm",
            },
            "compute_provider": "local" if self.mode == "local_vllm" else "external",
        }


def get_deployment_guide(provider: str = "runpod") -> str:
    """
    Generate a deployment guide for a specific compute provider.
    All the serving code already exists in vLLM - we just configure it.
    """
    
    info = COMPUTE_PROVIDERS.get(provider, COMPUTE_PROVIDERS["runpod"])
    config = AetherServingConfig()
    model_key = info["recommended_model"]
    config.model.model_name = config.model.RECOMMENDED_MODELS.get(model_key, config.model.model_name)
    
    if info.get("quantization"):
        config.model.quantization = info["quantization"]
    
    guide = f"""
# AETHER Deployment Guide - {info['name']}

## Hardware: {info['gpu']}
## Cost: ${info['cost_per_hour']}/hr
## Model: {config.model.model_name}

## Step 1: Install vLLM
```bash
pip install vllm
```

## Step 2: Start the server
```bash
{config.get_full_serve_command()}
```

## Step 3: Point AETHER to the server
```python
from aether.vllm_integration.serving_bridge import ServingBridge
from aether.vllm_integration.config import AetherServingConfig

config = AetherServingConfig()
config.model.host = "your-server-ip"
bridge = ServingBridge(config)

# Now run training sessions as normal
# The bridge automatically uses the local vLLM server
```

## Notes
{info['notes']}
"""
    return guide
