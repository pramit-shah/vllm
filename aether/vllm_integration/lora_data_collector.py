"""
AETHER LoRA Training Data Collector
Collects and formats training data from learning sessions to create
LoRA fine-tuning datasets for Stratify and Principia.

Uses existing vLLM LoRA support: vllm/lora/
The LoRA weights are served via vLLM's Multi-LoRA feature,
which already handles concurrent adapter loading and inference.

This module only handles DATA COLLECTION - the actual LoRA training
uses standard HuggingFace PEFT (which vLLM integrates with via
vllm/lora/peft_helper.py).
"""

import json
import os
from typing import Optional
from datetime import datetime


class LoRADataCollector:
    """
    Collects high-quality training examples from AETHER learning sessions
    to create LoRA fine-tuning datasets.
    
    Strategy:
    - Collect examples where score >= 90% (high quality solutions)
    - Separate by framework personality
    - Format as instruction-following pairs for LoRA training
    - Export in formats compatible with HuggingFace PEFT
    """
    
    def __init__(self, output_dir: str = "memory/lora_training_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.stratify_examples = []
        self.principia_examples = []
        
        # Load existing data if available
        self._load_existing()
    
    def _load_existing(self):
        """Load previously collected training data."""
        for name, examples in [("stratify", self.stratify_examples), 
                                ("principia", self.principia_examples)]:
            path = os.path.join(self.output_dir, f"{name}_train.jsonl")
            if os.path.exists(path):
                with open(path, 'r') as f:
                    for line in f:
                        if line.strip():
                            examples.append(json.loads(line))
    
    def add_example(
        self,
        framework: str,  # "stratify" or "principia"
        question: str,
        answer: str,
        score: float,
        topic: str,
        grade: int,
        feedback: str = "",
    ):
        """
        Add a training example if it meets quality threshold.
        Only high-scoring answers become training data.
        """
        if score < 90:
            return  # Only collect high-quality examples
        
        example = {
            "instruction": self._build_instruction(framework, topic, grade),
            "input": question,
            "output": answer,
            "metadata": {
                "framework": framework,
                "score": score,
                "topic": topic,
                "grade": grade,
                "feedback": feedback,
                "collected_at": datetime.now().isoformat(),
            }
        }
        
        if framework.lower() == "stratify":
            self.stratify_examples.append(example)
        else:
            self.principia_examples.append(example)
    
    def _build_instruction(self, framework: str, topic: str, grade: int) -> str:
        """Build the instruction prompt that encodes framework personality."""
        
        if framework.lower() == "stratify":
            return (
                f"You are Stratify, a creative and intuitive mathematician. "
                f"Solve this Grade {grade} {topic} problem with elegance and insight. "
                f"Show your creative reasoning process and find novel approaches."
            )
        else:
            return (
                f"You are Principia, a rigorous and disciplined verifier. "
                f"Solve this Grade {grade} {topic} problem with complete precision. "
                f"Show every step of your formal reasoning and verify your answer."
            )
    
    def save(self):
        """Save collected training data to JSONL files."""
        for name, examples in [("stratify", self.stratify_examples),
                                ("principia", self.principia_examples)]:
            path = os.path.join(self.output_dir, f"{name}_train.jsonl")
            with open(path, 'w') as f:
                for ex in examples:
                    f.write(json.dumps(ex) + "\n")
        
        # Also save stats
        stats = {
            "stratify_examples": len(self.stratify_examples),
            "principia_examples": len(self.principia_examples),
            "total_examples": len(self.stratify_examples) + len(self.principia_examples),
            "last_updated": datetime.now().isoformat(),
        }
        
        stats_path = os.path.join(self.output_dir, "collection_stats.json")
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return stats
    
    def export_for_peft(self, framework: str) -> str:
        """
        Export training data in HuggingFace PEFT format.
        
        This format is directly compatible with:
        - HuggingFace PEFT library for LoRA training
        - vLLM's LoRA loading (vllm/lora/peft_helper.py)
        """
        examples = self.stratify_examples if framework == "stratify" else self.principia_examples
        
        peft_data = []
        for ex in examples:
            peft_data.append({
                "messages": [
                    {"role": "system", "content": ex["instruction"]},
                    {"role": "user", "content": ex["input"]},
                    {"role": "assistant", "content": ex["output"]},
                ]
            })
        
        output_path = os.path.join(self.output_dir, f"{framework}_peft.jsonl")
        with open(output_path, 'w') as f:
            for item in peft_data:
                f.write(json.dumps(item) + "\n")
        
        return output_path
    
    def get_training_script(self, framework: str, base_model: str = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B") -> str:
        """
        Generate a LoRA fine-tuning script.
        
        After training, the adapter can be served via vLLM's
        Multi-LoRA feature (vllm/lora/) without any custom code.
        """
        data_path = os.path.join(self.output_dir, f"{framework}_peft.jsonl")
        
        return f'''
# AETHER LoRA Fine-Tuning Script for {framework.title()}
# After training, serve with vLLM: --enable-lora --lora-modules {framework}=./lora_adapters/{framework}

from peft import LoraConfig, get_peft_model, TaskType
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from trl import SFTTrainer
import json

# Load base model
model = AutoModelForCausalLM.from_pretrained("{base_model}", torch_dtype="auto")
tokenizer = AutoTokenizer.from_pretrained("{base_model}")

# LoRA config
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=64,                    # Rank
    lora_alpha=128,          # Alpha
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
)

# Load training data
with open("{data_path}") as f:
    train_data = [json.loads(line) for line in f]

# Train
trainer = SFTTrainer(
    model=model,
    train_dataset=train_data,
    peft_config=lora_config,
    args=TrainingArguments(
        output_dir=f"./lora_adapters/{framework}",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        learning_rate=2e-4,
        save_strategy="epoch",
    ),
)
trainer.train()
trainer.save_model(f"./lora_adapters/{framework}")

# Now serve with vLLM:
# vllm serve {base_model} --enable-lora --lora-modules {framework}=./lora_adapters/{framework}
'''
