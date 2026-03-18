"""
AETHER Prefix Cache Manager
Manages common mathematical prompt prefixes for efficient caching.

Uses existing vLLM code:
- vllm/core/block/prefix_caching_block.py (ComputedBlocksTracker)
- vllm/core/block_manager.py (SelfAttnBlockSpaceManager)

When running on a self-hosted vLLM server with --enable-prefix-caching,
this module organizes prompts to maximize cache hits by sharing
common prefixes across similar math problems.
"""

from typing import Optional


class PrefixCacheManager:
    """
    Organizes math prompts to maximize vLLM's automatic prefix caching.
    
    vLLM's prefix caching (already implemented) works by detecting
    shared prefixes in the KV cache. We optimize this by structuring
    our prompts so that similar problems share long common prefixes.
    """
    
    # System prompts are the longest shared prefixes - cached once, reused many times
    FRAMEWORK_PREFIXES = {
        "stratify": (
            "You are Stratify, a Theoretical Mathematician with strong creativity and intuition. "
            "Your character traits: intelligence=100, wisdom=100, creativity=100, discipline=100, "
            "perseverance=100, focus=100, curiosity=100, rigor=100. "
            "You approach mathematics with elegance and seek novel connections. "
            "Show your complete reasoning process step by step."
        ),
        "principia": (
            "You are Principia, a Rigorous Verifier with exceptional discipline and rigor. "
            "Your character traits: intelligence=100, wisdom=100, creativity=100, discipline=100, "
            "perseverance=100, focus=100, curiosity=100, rigor=100. "
            "You approach mathematics with formal precision and verify every step. "
            "Show your complete reasoning process step by step."
        ),
    }
    
    # Grade-level prefixes (shared across all problems in a grade)
    GRADE_PREFIXES = {
        10: (
            "You are working on Grade 10 Geometry. Topics include: "
            "geometric proofs, triangle congruence (SAS, SSS, ASA, AAS, HL), "
            "similarity (AA, SAS, SSS), and introductory trigonometry "
            "(sine, cosine, tangent, Law of Sines, Law of Cosines). "
        ),
        11: (
            "You are working on Grade 11 Algebra II. Topics include: "
            "polynomial functions, rational expressions, logarithms, "
            "exponential functions, sequences and series, and conic sections. "
        ),
        12: (
            "You are working on Grade 12 Pre-Calculus/Calculus. Topics include: "
            "limits, derivatives, integrals, trigonometric identities, "
            "polar coordinates, and parametric equations. "
        ),
    }
    
    # Topic-specific prefixes (shared across problems of the same type)
    TOPIC_PREFIXES = {
        "geometric_proofs": (
            "Solve the following geometric proof problem. "
            "Structure your answer as: Given, To Prove, Proof (with numbered steps), QED. "
            "Cite the specific theorem or postulate used in each step. "
        ),
        "triangle_congruence": (
            "Determine triangle congruence in the following problem. "
            "Identify the congruence criterion (SAS, SSS, ASA, AAS, or HL) "
            "and list the corresponding parts that satisfy it. "
        ),
        "similarity": (
            "Solve the following similarity problem. "
            "Identify the similarity criterion (AA, SAS, or SSS) "
            "and set up the correct proportions. "
        ),
        "trigonometry_intro": (
            "Solve the following trigonometry problem. "
            "Choose the appropriate trigonometric ratio or law "
            "(sine, cosine, tangent, Law of Sines, or Law of Cosines). "
            "Show all calculations clearly. "
        ),
    }
    
    def build_prompt(
        self,
        framework: str,
        grade: int,
        topic: str,
        question: str,
    ) -> list:
        """
        Build a prompt optimized for prefix caching.
        
        Structure: [framework_prefix] + [grade_prefix] + [topic_prefix] + [question]
        
        The first three parts are shared across many problems,
        so vLLM's prefix caching will cache them in the KV cache
        and only compute the unique question part.
        """
        system_content = self.FRAMEWORK_PREFIXES.get(framework.lower(), "")
        system_content += self.GRADE_PREFIXES.get(grade, "")
        system_content += self.TOPIC_PREFIXES.get(topic, "")
        
        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": question},
        ]
    
    def estimate_cache_savings(self, num_questions: int, grade: int, framework: str) -> dict:
        """
        Estimate token savings from prefix caching.
        
        With 12 questions per round, the system prompt (~200 tokens)
        is computed once and cached for all 12. That's ~2,200 tokens
        saved per round, or ~22,000 tokens per batch of 10 rounds.
        """
        prefix_tokens = len(self.FRAMEWORK_PREFIXES.get(framework.lower(), "").split()) * 1.3
        prefix_tokens += len(self.GRADE_PREFIXES.get(grade, "").split()) * 1.3
        
        # First question computes the prefix, rest use cache
        saved_tokens = prefix_tokens * (num_questions - 1)
        total_without_cache = prefix_tokens * num_questions
        
        return {
            "prefix_tokens": int(prefix_tokens),
            "total_without_cache": int(total_without_cache),
            "total_with_cache": int(prefix_tokens + (num_questions - 1) * 10),  # ~10 tokens overhead per cached hit
            "tokens_saved": int(saved_tokens),
            "speedup_factor": round(total_without_cache / (prefix_tokens + (num_questions - 1) * 10), 2),
        }
