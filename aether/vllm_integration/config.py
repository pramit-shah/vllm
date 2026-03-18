"""
AETHER vLLM Configuration
Defines model serving configs for self-hosted inference.
Leverages existing vLLM code - no need to recreate.

Reference: vllm/config.py, vllm/entrypoints/openai/
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AetherModelConfig:
    """Configuration for the base math model served via vLLM."""
    
    # Model selection - math-specialized models ranked by capability
    RECOMMENDED_MODELS = {
        "small": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",   # 1.5B, runs on any GPU
        "medium": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",    # 7B, needs 16GB VRAM
        "large": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",    # 32B, needs 40GB+ VRAM
        "math_small": "Qwen/Qwen2.5-Math-1.5B-Instruct",       # Math-specialized
        "math_medium": "Qwen/Qwen2.5-Math-7B-Instruct",        # Math-specialized
        "math_large": "Qwen/Qwen2.5-Math-72B-Instruct",        # Math-specialized
    }
    
    model_name: str = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
    reasoning_parser: str = "deepseek_r1"  # Uses vllm/reasoning/deepseek_r1_reasoning_parser.py
    
    # Quantization - uses vllm/model_executor/layers/quantization/
    quantization: Optional[str] = None  # "awq", "gptq", "fp8", "int8", etc.
    
    # Serving config
    host: str = "0.0.0.0"
    port: int = 8000
    max_model_len: int = 8192  # Math proofs can be long
    
    # Performance features from vLLM (all existing code)
    enable_prefix_caching: bool = True   # vllm/core/block/prefix_caching_block.py
    enable_chunked_prefill: bool = True  # Reduces TTFT for long prompts
    
    # GPU memory utilization
    gpu_memory_utilization: float = 0.90
    
    def get_serve_command(self) -> str:
        """Generate the vllm serve command using existing vLLM CLI."""
        cmd = f"vllm serve {self.model_name}"
        cmd += f" --reasoning-parser {self.reasoning_parser}"
        cmd += f" --host {self.host} --port {self.port}"
        cmd += f" --max-model-len {self.max_model_len}"
        cmd += f" --gpu-memory-utilization {self.gpu_memory_utilization}"
        if self.enable_prefix_caching:
            cmd += " --enable-prefix-caching"
        if self.enable_chunked_prefill:
            cmd += " --enable-chunked-prefill"
        if self.quantization:
            cmd += f" --quantization {self.quantization}"
        return cmd


@dataclass
class AetherLoRAConfig:
    """
    LoRA adapter configuration for Stratify vs Principia.
    Uses existing vLLM Multi-LoRA support: vllm/lora/
    
    Each framework gets its own LoRA adapter trained on its personality:
    - Stratify: Creative, intuitive mathematical reasoning
    - Principia: Rigorous, disciplined verification
    """
    
    enable_lora: bool = True
    max_loras: int = 2  # Stratify + Principia
    max_lora_rank: int = 64
    
    # LoRA adapter paths (to be created during fine-tuning)
    stratify_adapter: Optional[str] = None
    principia_adapter: Optional[str] = None
    
    def get_lora_flags(self) -> str:
        """Generate vLLM LoRA flags for serving."""
        if not self.enable_lora:
            return ""
        return f" --enable-lora --max-loras {self.max_loras} --max-lora-rank {self.max_lora_rank}"


@dataclass
class AetherPrefixCacheConfig:
    """
    Prefix caching configuration for math problem patterns.
    Uses existing vLLM code: vllm/core/block/prefix_caching_block.py
    
    Math problems share common prefixes:
    - System prompts (framework personality)
    - Theorem statements
    - Problem type templates
    """
    
    enable: bool = True
    
    # Common prefixes to cache
    MATH_PREFIXES = {
        "proof_setup": "Given the following geometric configuration, prove that",
        "theorem_apply": "Using the theorem that states",
        "calculate": "Calculate the value of",
        "verify": "Verify that the following mathematical statement is correct",
    }


@dataclass 
class AetherServingConfig:
    """Complete serving configuration combining all vLLM features."""
    
    model: AetherModelConfig = field(default_factory=AetherModelConfig)
    lora: AetherLoRAConfig = field(default_factory=AetherLoRAConfig)
    prefix_cache: AetherPrefixCacheConfig = field(default_factory=AetherPrefixCacheConfig)
    
    # Continuous batching - uses vllm/core/scheduler.py
    max_num_seqs: int = 8  # Both frameworks + grader can run simultaneously
    
    # Streaming - uses vllm/entrypoints/openai/serving_chat.py
    enable_streaming: bool = True
    
    def get_full_serve_command(self) -> str:
        """Generate complete vllm serve command with all features."""
        cmd = self.model.get_serve_command()
        cmd += self.lora.get_lora_flags()
        cmd += f" --max-num-seqs {self.max_num_seqs}"
        return cmd
    
    def get_openai_base_url(self) -> str:
        """Get the OpenAI-compatible API base URL."""
        return f"http://{self.model.host}:{self.model.port}/v1"


# Provider configurations for different compute resources
COMPUTE_PROVIDERS = {
    "runpod": {
        "name": "RunPod",
        "gpu": "A100 80GB",
        "cost_per_hour": 0.74,
        "recommended_model": "medium",
        "quantization": None,
        "notes": "Best cost/performance ratio for research"
    },
    "lambda": {
        "name": "Lambda Lab",
        "gpu": "A100 80GB",
        "cost_per_hour": 1.10,
        "recommended_model": "large",
        "quantization": None,
        "notes": "Purpose-built for ML, simple setup"
    },
    "google_cloud": {
        "name": "Google Cloud",
        "gpu": "T4 16GB (free tier)",
        "cost_per_hour": 0.0,
        "recommended_model": "small",
        "quantization": "int8",
        "notes": "Free tier available, good for testing"
    },
    "local_consumer": {
        "name": "Local (RTX 3090/4090)",
        "gpu": "RTX 4090 24GB",
        "cost_per_hour": 0.0,
        "recommended_model": "medium",
        "quantization": "awq",
        "notes": "Free if you have the hardware"
    }
}
