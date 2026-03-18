# vLLM Codebase Audit for AETHER Integration

## Available Code We Can Leverage (No Need to Recreate)

### 1. Reasoning Parsers (`vllm/reasoning/`)
- **DeepSeek R1 Parser**: Extracts `<think>...</think>` reasoning chains
- **Qwen3 Parser**: Alternative reasoning format
- **Granite Parser**: IBM's reasoning format
- **Use for AETHER**: Parse and analyze the AI's step-by-step mathematical reasoning

### 2. PagedAttention (`vllm/attention/`)
- Full implementation of PagedAttention with multiple backends
- FlashAttention integration
- **Use for AETHER**: Efficient memory management for long proof sequences

### 3. Prefix Caching (`vllm/core/block_manager.py`)
- `ComputedBlocksTracker` and `LastAccessBlocksTracker`
- Automatic prefix caching for repeated prompt prefixes
- **Use for AETHER**: Cache common math problem structures, theorem statements

### 4. Multi-LoRA (`vllm/lora/`)
- Full LoRA weight management (`LoRALayerWeights`)
- Worker manager for serving multiple LoRA adapters simultaneously
- Quantization + LoRA support
- **Use for AETHER**: Separate LoRA adapters for Stratify (creative) vs Principia (rigorous)

### 5. Speculative Decoding (`vllm/spec_decode/`)
- Draft model runner, MLP speculator, ngram worker
- Top-1 proposer, batch expansion
- **Use for AETHER**: Faster solution generation during training

### 6. Quantization (`vllm/model_executor/layers/quantization/`)
- GPTQ, AWQ, AutoRound, INT4, INT8, FP8, BitsAndBytes
- 20+ quantization methods available
- **Use for AETHER**: Run larger math models on limited hardware

### 7. OpenAI-Compatible Server (`vllm/entrypoints/openai/`)
- Full OpenAI API compatibility (chat, completions, embeddings)
- Streaming support
- Tool calling support
- **Use for AETHER**: Drop-in replacement for current OpenAI API calls

### 8. Continuous Batching (`vllm/core/scheduler.py`)
- Request scheduling and batching
- **Use for AETHER**: Process both frameworks simultaneously

### 9. Streaming (`vllm/entrypoints/openai/serving_chat.py`)
- Real-time token streaming
- **Use for AETHER**: Monitor solution generation in real-time

### 10. HuggingFace Integration (`vllm/transformers_utils/`)
- Tokenizer management, model configs, chat templates
- **Use for AETHER**: Easy access to math-specialized models

## Example Code Available
- `examples/offline_inference/basic/` - Basic LLM inference
- `examples/offline_inference/automatic_prefix_caching.py` - Prefix caching
- `examples/offline_inference/lora_with_quantization_inference.py` - LoRA + quantization
- `examples/online_serving/openai_chat_completion_with_reasoning.py` - Reasoning models
- `examples/online_serving/openai_chat_completion_with_reasoning_streaming.py` - Streaming reasoning

## Integration Plan
1. Create `aether/vllm_integration/` module
2. Wrap vLLM's reasoning parsers for math solution analysis
3. Create config for self-hosted math model serving
4. Build LoRA adapter configs for Stratify vs Principia
5. Integrate prefix caching for math problem patterns
