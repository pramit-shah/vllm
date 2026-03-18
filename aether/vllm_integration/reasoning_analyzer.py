"""
AETHER Reasoning Analyzer
Leverages vLLM's reasoning parser architecture (vllm/reasoning/) to analyze
mathematical reasoning chains from both frameworks.

This module wraps vLLM's existing DeepSeek R1, Qwen3, and Granite reasoning
parsers to extract and evaluate step-by-step mathematical proofs.

Reference code (already exists in vLLM, no need to recreate):
- vllm/reasoning/abs_reasoning_parsers.py
- vllm/reasoning/deepseek_r1_reasoning_parser.py
- vllm/reasoning/qwen3_reasoning_parser.py
"""

import re
import json
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class ReasoningStep:
    """A single step in a mathematical reasoning chain."""
    step_number: int
    content: str
    step_type: str  # "setup", "theorem", "calculation", "conclusion", "verification"
    confidence: float = 0.0
    is_valid: bool = True
    error_description: Optional[str] = None


@dataclass
class ReasoningChain:
    """Complete reasoning chain extracted from model output."""
    raw_thinking: str
    raw_answer: str
    steps: list = field(default_factory=list)
    total_steps: int = 0
    chain_quality: float = 0.0
    proof_complete: bool = False
    theorems_used: list = field(default_factory=list)
    

class AetherReasoningAnalyzer:
    """
    Analyzes mathematical reasoning from model outputs.
    
    When running with vLLM self-hosted models, this uses the native
    reasoning parsers (DeepSeek R1 <think>...</think> format).
    When running with external APIs, it parses structured output.
    """
    
    # Patterns that indicate reasoning steps (from vLLM's parser architecture)
    THINK_PATTERNS = {
        "deepseek_r1": (r"<think>(.*?)</think>", r"</think>(.*)"),
        "qwen3": (r"<think>(.*?)</think>", r"</think>(.*)"),
        "generic": (r"(?:Step \d+|First|Then|Next|Finally|Therefore)[:\.](.+?)(?=Step \d+|First|Then|Next|Finally|Therefore|$)", None),
    }
    
    # Mathematical theorem patterns to detect
    THEOREM_PATTERNS = [
        r"(?:by|using|applying|from)\s+(?:the\s+)?(pythagorean\s+theorem)",
        r"(?:by|using|applying|from)\s+(?:the\s+)?(triangle\s+(?:inequality|congruence|similarity))",
        r"(?:by|using|applying|from)\s+(?:the\s+)?(SAS|SSS|ASA|AAS|HL)\s+(?:theorem|congruence|postulate)",
        r"(?:by|using|applying|from)\s+(?:the\s+)?(midpoint|midsegment)\s+theorem",
        r"(?:by|using|applying|from)\s+(?:the\s+)?(law\s+of\s+(?:sines|cosines))",
        r"(?:by|using|applying|from)\s+(?:the\s+)?(angle\s+bisector)\s+theorem",
        r"(?:by|using|applying|from)\s+(?:the\s+)?(parallel\s+lines?)\s+(?:theorem|postulate)",
        r"(?:by|using|applying|from)\s+(?:the\s+)?(similar\s+triangles?)",
        r"(?:by|using|applying|from)\s+(?:the\s+)?(CPCTC)",
        r"(?:by|using|applying|from)\s+(?:the\s+)?(AA|SAS|SSS)\s+similarity",
    ]
    
    # Proof structure patterns
    PROOF_MARKERS = {
        "given": r"(?:given|we\s+know|it\s+is\s+given|assume)",
        "claim": r"(?:prove|show|demonstrate|we\s+need\s+to\s+(?:prove|show))",
        "step": r"(?:therefore|thus|hence|so|it\s+follows|this\s+(?:means|implies))",
        "conclusion": r"(?:QED|proven|established|we\s+have\s+shown|this\s+completes)",
    }
    
    def __init__(self, parser_type: str = "generic"):
        self.parser_type = parser_type
    
    def extract_reasoning(self, model_output: str) -> ReasoningChain:
        """
        Extract reasoning chain from model output.
        
        When using vLLM with reasoning parser, the output already has
        separated thinking and content. When using external APIs,
        we parse the raw text.
        """
        thinking = ""
        answer = ""
        
        # Try DeepSeek R1 / Qwen3 format first
        think_match = re.search(r"<think>(.*?)</think>", model_output, re.DOTALL)
        if think_match:
            thinking = think_match.group(1).strip()
            answer = re.sub(r"<think>.*?</think>", "", model_output, flags=re.DOTALL).strip()
        else:
            # Fallback: treat entire output as combined reasoning + answer
            thinking = ""
            answer = model_output
        
        # Extract individual steps
        steps = self._extract_steps(thinking if thinking else answer)
        
        # Detect theorems used
        theorems = self._detect_theorems(model_output)
        
        # Assess proof completeness
        proof_complete = self._check_proof_completeness(model_output)
        
        # Calculate chain quality
        quality = self._assess_chain_quality(steps, theorems, proof_complete)
        
        return ReasoningChain(
            raw_thinking=thinking,
            raw_answer=answer,
            steps=steps,
            total_steps=len(steps),
            chain_quality=quality,
            proof_complete=proof_complete,
            theorems_used=theorems,
        )
    
    def _extract_steps(self, text: str) -> list:
        """Extract individual reasoning steps from text."""
        steps = []
        
        # Split by step markers
        sentences = re.split(r'(?<=[.!?])\s+', text)
        step_num = 0
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            step_num += 1
            step_type = self._classify_step(sentence)
            steps.append(ReasoningStep(
                step_number=step_num,
                content=sentence.strip(),
                step_type=step_type,
                confidence=0.8 if step_type != "unknown" else 0.5,
            ))
        
        return steps
    
    def _classify_step(self, text: str) -> str:
        """Classify a reasoning step by its type."""
        text_lower = text.lower()
        
        for marker_type, pattern in self.PROOF_MARKERS.items():
            if re.search(pattern, text_lower):
                return marker_type
        
        if re.search(r'\d+\s*[+\-*/=<>]\s*\d+', text):
            return "calculation"
        if re.search(r'theorem|lemma|corollary|postulate', text_lower):
            return "theorem"
        
        return "step"
    
    def _detect_theorems(self, text: str) -> list:
        """Detect which mathematical theorems were used."""
        theorems = []
        text_lower = text.lower()
        
        for pattern in self.THEOREM_PATTERNS:
            matches = re.findall(pattern, text_lower)
            theorems.extend(matches)
        
        return list(set(theorems))
    
    def _check_proof_completeness(self, text: str) -> bool:
        """Check if a proof has all required components."""
        text_lower = text.lower()
        
        has_given = bool(re.search(self.PROOF_MARKERS["given"], text_lower))
        has_conclusion = bool(re.search(self.PROOF_MARKERS["conclusion"], text_lower))
        has_steps = bool(re.search(self.PROOF_MARKERS["step"], text_lower))
        
        return has_given and has_conclusion and has_steps
    
    def _assess_chain_quality(self, steps: list, theorems: list, complete: bool) -> float:
        """Assess the overall quality of the reasoning chain."""
        score = 0.0
        
        # Points for having steps
        if len(steps) >= 3:
            score += 0.3
        elif len(steps) >= 1:
            score += 0.15
        
        # Points for using theorems
        if len(theorems) >= 2:
            score += 0.3
        elif len(theorems) >= 1:
            score += 0.15
        
        # Points for proof completeness
        if complete:
            score += 0.4
        
        return min(score, 1.0)
    
    def compare_frameworks(self, stratify_output: str, principia_output: str) -> dict:
        """
        Compare reasoning chains from both frameworks.
        Useful for identifying complementary strengths.
        """
        s_chain = self.extract_reasoning(stratify_output)
        p_chain = self.extract_reasoning(principia_output)
        
        return {
            "stratify": {
                "steps": s_chain.total_steps,
                "quality": s_chain.chain_quality,
                "theorems": s_chain.theorems_used,
                "complete": s_chain.proof_complete,
            },
            "principia": {
                "steps": p_chain.total_steps,
                "quality": p_chain.chain_quality,
                "theorems": p_chain.theorems_used,
                "complete": p_chain.proof_complete,
            },
            "complementary_theorems": list(
                set(s_chain.theorems_used) ^ set(p_chain.theorems_used)
            ),
            "shared_theorems": list(
                set(s_chain.theorems_used) & set(p_chain.theorems_used)
            ),
        }
