"""
AETHER Anti-Cheat System
- Verifies actual AI reasoning, not memorization
- Detects pattern matching vs true understanding
- Ensures honest learning
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
import re
from datetime import datetime


class ReasoningQuality(Enum):
    """Quality levels of reasoning"""
    GENUINE = "genuine"           # Real understanding demonstrated
    PARTIAL = "partial"           # Some understanding, some gaps
    SUPERFICIAL = "superficial"   # Surface-level, possibly memorized
    SUSPICIOUS = "suspicious"     # Likely cheating/memorization
    INVALID = "invalid"           # No real reasoning present


@dataclass
class ReasoningAnalysis:
    """Analysis of a student's reasoning"""
    quality: ReasoningQuality
    score: int  # 0-100
    genuine_elements: List[str]
    suspicious_elements: List[str]
    missing_elements: List[str]
    follow_up_questions: List[str]  # Questions to verify understanding
    confidence: float  # 0-1, how confident we are in this analysis
    explanation: str
    

@dataclass
class CheatDetection:
    """Result of cheat detection"""
    is_suspicious: bool
    cheat_indicators: List[str]
    confidence: float
    recommendation: str


class AntiCheatSystem:
    """
    System to verify actual AI reasoning and prevent cheating.
    Ensures students demonstrate genuine understanding.
    """
    
    # Indicators of genuine reasoning
    GENUINE_INDICATORS = [
        "step_by_step_logic",
        "explains_why_not_just_how",
        "connects_to_prerequisites",
        "identifies_edge_cases",
        "shows_verification",
        "acknowledges_uncertainty",
        "uses_multiple_approaches",
        "relates_to_real_world",
        "asks_clarifying_questions",
        "builds_on_previous_knowledge"
    ]
    
    # Indicators of memorization/cheating
    CHEAT_INDICATORS = [
        "generic_response",
        "missing_reasoning_steps",
        "cannot_explain_why",
        "inconsistent_with_previous",
        "keyword_triggered_response",
        "no_adaptation_to_context",
        "perfect_textbook_match",
        "fails_follow_up",
        "no_original_insight",
        "mechanical_pattern"
    ]
    
    # Required reasoning elements by level
    REQUIRED_REASONING = {
        "K": ["basic_logic", "simple_explanation"],
        "1-5": ["step_by_step", "why_explanation", "verification"],
        "6-8": ["logical_progression", "concept_connection", "error_checking"],
        "9-12": ["formal_reasoning", "proof_structure", "alternative_approaches"],
        "UG": ["rigorous_proof", "theorem_application", "generalization"],
        "GRAD": ["research_level_reasoning", "novel_connections", "deep_insight"],
        "PHD": ["original_thinking", "breakthrough_potential", "field_advancement"]
    }
    
    def __init__(self):
        self.verification_history: Dict[str, List[ReasoningAnalysis]] = {}
        self.cheat_flags: Dict[str, List[CheatDetection]] = {}
        
    def analyze_reasoning(self, 
                          student: str,
                          question: str,
                          answer: str,
                          level: str,
                          previous_answers: List[str] = None) -> ReasoningAnalysis:
        """
        Analyze a student's answer for genuine reasoning.
        """
        genuine_elements = []
        suspicious_elements = []
        missing_elements = []
        
        # Check for genuine reasoning indicators
        for indicator in self.GENUINE_INDICATORS:
            if self._check_indicator(answer, indicator, is_genuine=True):
                genuine_elements.append(indicator)
                
        # Check for cheat indicators
        for indicator in self.CHEAT_INDICATORS:
            if self._check_indicator(answer, indicator, is_genuine=False):
                suspicious_elements.append(indicator)
                
        # Check for required elements based on level
        required = self._get_required_elements(level)
        for element in required:
            if not self._has_element(answer, element):
                missing_elements.append(element)
                
        # Check consistency with previous answers
        if previous_answers:
            consistency = self._check_consistency(answer, previous_answers)
            if not consistency["is_consistent"]:
                suspicious_elements.append("inconsistent_with_previous")
                
        # Calculate quality and score
        quality, score = self._calculate_quality(
            genuine_elements, suspicious_elements, missing_elements
        )
        
        # Generate follow-up questions to verify understanding
        follow_ups = self._generate_follow_ups(question, answer, missing_elements)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            len(genuine_elements), len(suspicious_elements), len(missing_elements)
        )
        
        analysis = ReasoningAnalysis(
            quality=quality,
            score=score,
            genuine_elements=genuine_elements,
            suspicious_elements=suspicious_elements,
            missing_elements=missing_elements,
            follow_up_questions=follow_ups,
            confidence=confidence,
            explanation=self._generate_explanation(quality, genuine_elements, suspicious_elements, missing_elements)
        )
        
        # Store in history
        if student not in self.verification_history:
            self.verification_history[student] = []
        self.verification_history[student].append(analysis)
        
        return analysis
    
    def _check_indicator(self, answer: str, indicator: str, is_genuine: bool) -> bool:
        """Check if an indicator is present in the answer"""
        answer_lower = answer.lower()
        
        if is_genuine:
            # Genuine indicators
            checks = {
                "step_by_step_logic": any(w in answer_lower for w in ["first", "then", "next", "finally", "step"]),
                "explains_why_not_just_how": any(w in answer_lower for w in ["because", "since", "therefore", "thus", "reason"]),
                "connects_to_prerequisites": any(w in answer_lower for w in ["recall", "previously", "building on", "as we learned"]),
                "identifies_edge_cases": any(w in answer_lower for w in ["except", "unless", "edge case", "special case", "however"]),
                "shows_verification": any(w in answer_lower for w in ["verify", "check", "confirm", "let's see if", "this makes sense"]),
                "acknowledges_uncertainty": any(w in answer_lower for w in ["might", "possibly", "uncertain", "need to verify", "assuming"]),
                "uses_multiple_approaches": any(w in answer_lower for w in ["alternatively", "another way", "we could also", "different approach"]),
                "relates_to_real_world": any(w in answer_lower for w in ["example", "real world", "application", "in practice"]),
                "asks_clarifying_questions": "?" in answer and any(w in answer_lower for w in ["clarify", "mean", "specific"]),
                "builds_on_previous_knowledge": any(w in answer_lower for w in ["we know", "established", "from earlier", "recall that"])
            }
        else:
            # Cheat indicators
            checks = {
                "generic_response": len(answer.split()) < 20 and "the answer is" in answer_lower,
                "missing_reasoning_steps": "because" not in answer_lower and "therefore" not in answer_lower,
                "cannot_explain_why": answer_lower.count("because") == 0 and answer_lower.count("since") == 0,
                "inconsistent_with_previous": False,  # Checked separately
                "keyword_triggered_response": self._is_keyword_triggered(answer),
                "no_adaptation_to_context": len(set(answer.split())) < len(answer.split()) * 0.5,  # Too repetitive
                "perfect_textbook_match": self._is_textbook_match(answer),
                "fails_follow_up": False,  # Checked separately
                "no_original_insight": not any(w in answer_lower for w in ["i think", "i believe", "my understanding", "it seems"]),
                "mechanical_pattern": self._is_mechanical(answer)
            }
            
        return checks.get(indicator, False)
    
    def _is_keyword_triggered(self, answer: str) -> bool:
        """Check if response seems triggered by keywords rather than understanding"""
        # Very short answers that just repeat question keywords
        words = answer.lower().split()
        if len(words) < 15:
            return True
        return False
    
    def _is_textbook_match(self, answer: str) -> bool:
        """Check if answer is a perfect textbook reproduction"""
        # Textbook answers often have very formal structure
        formal_markers = ["definition:", "theorem:", "proof:", "q.e.d.", "hence proved"]
        return any(marker in answer.lower() for marker in formal_markers) and len(answer.split()) < 50
    
    def _is_mechanical(self, answer: str) -> bool:
        """Check if answer follows a mechanical pattern"""
        # Very uniform sentence lengths suggest mechanical generation
        sentences = answer.split('.')
        if len(sentences) < 3:
            return False
        lengths = [len(s.split()) for s in sentences if s.strip()]
        if lengths:
            avg = sum(lengths) / len(lengths)
            variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
            return variance < 2  # Very uniform = suspicious
        return False
    
    def _get_required_elements(self, level: str) -> List[str]:
        """Get required reasoning elements for a level"""
        if level in ["K"]:
            return self.REQUIRED_REASONING["K"]
        elif level in ["1", "2", "3", "4", "5"]:
            return self.REQUIRED_REASONING["1-5"]
        elif level in ["6", "7", "8"]:
            return self.REQUIRED_REASONING["6-8"]
        elif level in ["9", "10", "11", "12"]:
            return self.REQUIRED_REASONING["9-12"]
        elif level.startswith("UG"):
            return self.REQUIRED_REASONING["UG"]
        elif level.startswith("GRAD"):
            return self.REQUIRED_REASONING["GRAD"]
        else:
            return self.REQUIRED_REASONING["PHD"]
    
    def _has_element(self, answer: str, element: str) -> bool:
        """Check if answer has a required reasoning element"""
        answer_lower = answer.lower()
        
        element_checks = {
            "basic_logic": any(w in answer_lower for w in ["so", "because", "if", "then"]),
            "simple_explanation": len(answer.split()) > 10,
            "step_by_step": any(w in answer_lower for w in ["first", "then", "next", "step"]),
            "why_explanation": "because" in answer_lower or "since" in answer_lower,
            "verification": any(w in answer_lower for w in ["check", "verify", "confirm"]),
            "logical_progression": answer_lower.count("therefore") > 0 or answer_lower.count("thus") > 0,
            "concept_connection": any(w in answer_lower for w in ["relates to", "connects", "similar to"]),
            "error_checking": any(w in answer_lower for w in ["error", "mistake", "careful", "note that"]),
            "formal_reasoning": any(w in answer_lower for w in ["assume", "suppose", "let", "given"]),
            "proof_structure": any(w in answer_lower for w in ["prove", "show that", "demonstrate"]),
            "alternative_approaches": any(w in answer_lower for w in ["alternatively", "another way", "also"]),
            "rigorous_proof": any(w in answer_lower for w in ["by definition", "by theorem", "it follows"]),
            "theorem_application": any(w in answer_lower for w in ["theorem", "lemma", "corollary"]),
            "generalization": any(w in answer_lower for w in ["in general", "for all", "generalize"]),
            "research_level_reasoning": any(w in answer_lower for w in ["conjecture", "hypothesis", "novel"]),
            "novel_connections": any(w in answer_lower for w in ["new connection", "unexplored", "insight"]),
            "deep_insight": any(w in answer_lower for w in ["fundamental", "underlying", "essence"]),
            "original_thinking": any(w in answer_lower for w in ["i propose", "new approach", "original"]),
            "breakthrough_potential": any(w in answer_lower for w in ["breakthrough", "significant", "major"]),
            "field_advancement": any(w in answer_lower for w in ["advance", "contribute", "extend"])
        }
        
        return element_checks.get(element, False)
    
    def _check_consistency(self, answer: str, previous_answers: List[str]) -> Dict[str, Any]:
        """Check if answer is consistent with previous answers"""
        # Simple consistency check - more sophisticated version would use embeddings
        answer_words = set(answer.lower().split())
        
        for prev in previous_answers[-5:]:  # Check last 5 answers
            prev_words = set(prev.lower().split())
            overlap = len(answer_words & prev_words) / max(len(answer_words), 1)
            
            # If very high overlap but contradicting, that's suspicious
            if overlap > 0.8:
                # Check for contradictions
                if ("not" in answer.lower()) != ("not" in prev.lower()):
                    return {"is_consistent": False, "reason": "Contradicting previous answer"}
                    
        return {"is_consistent": True, "reason": "No contradictions detected"}
    
    def _calculate_quality(self, genuine: List[str], suspicious: List[str], missing: List[str]) -> Tuple[ReasoningQuality, int]:
        """Calculate reasoning quality and score"""
        genuine_score = len(genuine) * 15
        suspicious_penalty = len(suspicious) * 20
        missing_penalty = len(missing) * 10
        
        raw_score = max(0, min(100, 50 + genuine_score - suspicious_penalty - missing_penalty))
        
        if raw_score >= 90 and len(suspicious) == 0:
            return ReasoningQuality.GENUINE, raw_score
        elif raw_score >= 70 and len(suspicious) <= 1:
            return ReasoningQuality.PARTIAL, raw_score
        elif raw_score >= 50:
            return ReasoningQuality.SUPERFICIAL, raw_score
        elif len(suspicious) >= 3:
            return ReasoningQuality.SUSPICIOUS, raw_score
        else:
            return ReasoningQuality.INVALID, raw_score
    
    def _generate_follow_ups(self, question: str, answer: str, missing: List[str]) -> List[str]:
        """Generate follow-up questions to verify understanding"""
        follow_ups = []
        
        # Generic follow-ups
        follow_ups.append("Can you explain WHY this approach works, not just HOW?")
        follow_ups.append("What would happen if we changed one of the conditions?")
        follow_ups.append("Can you solve a similar problem with different numbers?")
        
        # Specific follow-ups based on missing elements
        if "why_explanation" in missing:
            follow_ups.append("You showed the steps, but WHY does each step follow from the previous?")
        if "verification" in missing:
            follow_ups.append("How can you verify that your answer is correct?")
        if "alternative_approaches" in missing:
            follow_ups.append("Is there another way to solve this problem?")
            
        return follow_ups[:5]  # Return at most 5 follow-ups
    
    def _calculate_confidence(self, genuine: int, suspicious: int, missing: int) -> float:
        """Calculate confidence in the analysis"""
        total_signals = genuine + suspicious + missing
        if total_signals == 0:
            return 0.5
        
        # More signals = more confidence
        base_confidence = min(0.9, 0.5 + total_signals * 0.05)
        
        # Adjust based on clarity
        if suspicious > genuine:
            return base_confidence * 0.9  # Less confident when suspicious
        elif genuine > suspicious + missing:
            return base_confidence * 1.1  # More confident when clearly genuine
            
        return min(1.0, base_confidence)
    
    def _generate_explanation(self, quality: ReasoningQuality, genuine: List[str], 
                              suspicious: List[str], missing: List[str]) -> str:
        """Generate human-readable explanation of the analysis"""
        parts = [f"Reasoning Quality: {quality.value.upper()}"]
        
        if genuine:
            parts.append(f"Genuine elements found: {', '.join(genuine[:3])}")
        if suspicious:
            parts.append(f"Suspicious elements: {', '.join(suspicious[:3])}")
        if missing:
            parts.append(f"Missing elements: {', '.join(missing[:3])}")
            
        return ". ".join(parts)
    
    def detect_cheating(self, student: str, answer: str, 
                        question_history: List[Dict] = None) -> CheatDetection:
        """
        Detect if a student is cheating or not demonstrating genuine understanding.
        """
        indicators = []
        
        # Check for copy-paste patterns
        if self._is_copy_paste(answer):
            indicators.append("Possible copy-paste detected")
            
        # Check for impossibly fast responses (would need timing data)
        # indicators.append("Response time suspiciously fast")
        
        # Check for pattern matching without understanding
        if self._is_pattern_matching(answer):
            indicators.append("Pattern matching without understanding")
            
        # Check consistency across questions
        if question_history:
            if not self._is_consistent_knowledge(answer, question_history):
                indicators.append("Inconsistent knowledge level")
                
        # Check for memorized responses
        if self._is_memorized(answer):
            indicators.append("Possibly memorized response")
            
        is_suspicious = len(indicators) >= 2
        confidence = min(1.0, len(indicators) * 0.3)
        
        if is_suspicious:
            recommendation = "Require follow-up questions to verify understanding"
        else:
            recommendation = "No cheating detected, proceed normally"
            
        detection = CheatDetection(
            is_suspicious=is_suspicious,
            cheat_indicators=indicators,
            confidence=confidence,
            recommendation=recommendation
        )
        
        # Store flag
        if student not in self.cheat_flags:
            self.cheat_flags[student] = []
        self.cheat_flags[student].append(detection)
        
        return detection
    
    def _is_copy_paste(self, answer: str) -> bool:
        """Check for copy-paste patterns"""
        # Check for unusual formatting that suggests copy-paste
        if "\t" in answer or "  " in answer:
            return True
        return False
    
    def _is_pattern_matching(self, answer: str) -> bool:
        """Check if response is just pattern matching"""
        # Very short, formulaic responses
        if len(answer.split()) < 20 and "=" in answer:
            return True
        return False
    
    def _is_consistent_knowledge(self, answer: str, history: List[Dict]) -> bool:
        """Check if knowledge level is consistent"""
        # If they suddenly know advanced concepts they didn't before
        # This would need more sophisticated analysis
        return True
    
    def _is_memorized(self, answer: str) -> bool:
        """Check if response appears memorized"""
        # Very formal, textbook-like language
        formal_phrases = ["by definition", "it is well known", "as stated in"]
        return sum(1 for p in formal_phrases if p in answer.lower()) >= 2
    
    def get_student_integrity_score(self, student: str) -> Dict[str, Any]:
        """Get overall integrity score for a student"""
        history = self.verification_history.get(student, [])
        flags = self.cheat_flags.get(student, [])
        
        if not history:
            return {"score": 100, "status": "No data", "analyses": 0}
            
        # Calculate average quality
        quality_scores = {
            ReasoningQuality.GENUINE: 100,
            ReasoningQuality.PARTIAL: 75,
            ReasoningQuality.SUPERFICIAL: 50,
            ReasoningQuality.SUSPICIOUS: 25,
            ReasoningQuality.INVALID: 0
        }
        
        avg_quality = sum(quality_scores[a.quality] for a in history) / len(history)
        
        # Penalty for cheat flags
        suspicious_flags = sum(1 for f in flags if f.is_suspicious)
        penalty = suspicious_flags * 10
        
        final_score = max(0, avg_quality - penalty)
        
        if final_score >= 90:
            status = "Excellent integrity"
        elif final_score >= 70:
            status = "Good integrity"
        elif final_score >= 50:
            status = "Needs improvement"
        else:
            status = "Integrity concerns"
            
        return {
            "score": final_score,
            "status": status,
            "analyses": len(history),
            "suspicious_flags": suspicious_flags,
            "average_reasoning_quality": avg_quality
        }


if __name__ == "__main__":
    # Test the anti-cheat system
    system = AntiCheatSystem()
    
    # Test with a genuine-looking answer
    genuine_answer = """
    First, let me understand the problem. We need to find the sum of 1 to 100.
    
    I recall that Gauss discovered a pattern here. If we pair numbers from opposite ends:
    1 + 100 = 101
    2 + 99 = 101
    3 + 98 = 101
    
    Since there are 50 such pairs, the sum is 50 × 101 = 5050.
    
    Let me verify: The formula n(n+1)/2 gives us 100(101)/2 = 5050. ✓
    
    This makes sense because we're essentially averaging the first and last term
    and multiplying by the count.
    """
    
    analysis = system.analyze_reasoning(
        student="Stratify",
        question="Find the sum of integers from 1 to 100",
        answer=genuine_answer,
        level="6"
    )
    
    print(f"Analysis: {analysis.quality.value}")
    print(f"Score: {analysis.score}")
    print(f"Genuine elements: {analysis.genuine_elements}")
    print(f"Suspicious elements: {analysis.suspicious_elements}")
