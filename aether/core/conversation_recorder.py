"""
AETHER Conversation Recording System
- Records ALL conversations
- Special handling for different score ranges
- Flags potential discoveries for Manus review
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import os
from datetime import datetime
from pathlib import Path


class ScoreCategory(Enum):
    """Score categories for recording"""
    PERFECT = "perfect"           # 100%
    EXCELLENT = "excellent"       # 95-99%
    HIGH = "high"                 # 75-94%
    MEDIUM = "medium"             # 50-74%
    LOW = "low"                   # 35-49%
    CRITICAL = "critical"         # 0-34%


@dataclass
class ConversationRecord:
    """A recorded conversation"""
    id: str
    timestamp: str
    student: str
    level: str
    topic: str
    question: str
    answer: str
    score: int
    category: ScoreCategory
    reasoning_analysis: Dict[str, Any]
    has_new_math: bool
    new_math_details: Optional[Dict[str, Any]]
    flagged_for_review: bool
    review_reason: Optional[str]
    metadata: Dict[str, Any]


class ConversationRecorder:
    """
    Records all conversations with special handling based on score ranges.
    Flags potential discoveries for Manus review.
    """
    
    # Directories for different record types
    RECORD_DIRS = {
        "all": "all_conversations",
        "high_score": "high_score_75_plus",
        "low_score": "low_score_74_minus",
        "new_math": "new_math_discoveries",
        "flagged": "flagged_for_review",
        "perfect": "perfect_scores"
    }
    
    def __init__(self, base_dir: str = "/home/ubuntu/aether/records"):
        self.base_dir = Path(base_dir)
        self._setup_directories()
        self.record_count = 0
        self.flagged_count = 0
        self.new_math_count = 0
        
    def _setup_directories(self):
        """Create all necessary directories"""
        for dir_name in self.RECORD_DIRS.values():
            (self.base_dir / dir_name).mkdir(parents=True, exist_ok=True)
            
    def _categorize_score(self, score: int) -> ScoreCategory:
        """Categorize a score"""
        if score == 100:
            return ScoreCategory.PERFECT
        elif score >= 95:
            return ScoreCategory.EXCELLENT
        elif score >= 75:
            return ScoreCategory.HIGH
        elif score >= 50:
            return ScoreCategory.MEDIUM
        elif score >= 35:
            return ScoreCategory.LOW
        else:
            return ScoreCategory.CRITICAL
            
    def record_conversation(self,
                           student: str,
                           level: str,
                           topic: str,
                           question: str,
                           answer: str,
                           score: int,
                           reasoning_analysis: Dict[str, Any] = None,
                           metadata: Dict[str, Any] = None) -> ConversationRecord:
        """
        Record a conversation and categorize it appropriately.
        """
        self.record_count += 1
        timestamp = datetime.now().isoformat()
        record_id = f"{student}_{level}_{self.record_count}_{timestamp[:10]}"
        
        category = self._categorize_score(score)
        
        # Check for new mathematical content
        has_new_math, new_math_details = self._check_for_new_math(answer, score)
        
        # Determine if should be flagged for Manus review
        flagged, review_reason = self._should_flag_for_review(
            score, has_new_math, category, reasoning_analysis
        )
        
        record = ConversationRecord(
            id=record_id,
            timestamp=timestamp,
            student=student,
            level=level,
            topic=topic,
            question=question,
            answer=answer,
            score=score,
            category=category,
            reasoning_analysis=reasoning_analysis or {},
            has_new_math=has_new_math,
            new_math_details=new_math_details,
            flagged_for_review=flagged,
            review_reason=review_reason,
            metadata=metadata or {}
        )
        
        # Save to appropriate files
        self._save_record(record)
        
        if flagged:
            self.flagged_count += 1
        if has_new_math:
            self.new_math_count += 1
            
        return record
    
    def _check_for_new_math(self, answer: str, score: int) -> tuple:
        """
        Check if the answer contains potentially new mathematical content.
        Returns (has_new_math, details)
        """
        answer_lower = answer.lower()
        
        # Indicators of potentially new mathematical content
        new_math_indicators = [
            "new formula",
            "novel approach",
            "i discovered",
            "new relationship",
            "previously unknown",
            "new theorem",
            "new proof",
            "alternative proof",
            "generalization",
            "new connection",
            "i propose",
            "conjecture",
            "new method",
            "original solution"
        ]
        
        # Check for mathematical notation that might indicate new formulas
        math_notation_patterns = [
            "∀", "∃", "∈", "⊂", "∪", "∩",  # Set theory
            "→", "↔", "⇒", "⇔",  # Logic
            "∫", "∑", "∏", "∂",  # Calculus
            "≡", "≈", "≠", "≤", "≥",  # Relations
        ]
        
        found_indicators = []
        
        for indicator in new_math_indicators:
            if indicator in answer_lower:
                found_indicators.append(indicator)
                
        has_math_notation = any(sym in answer for sym in math_notation_patterns)
        
        # Consider it potentially new math if:
        # 1. Has new math indicators, OR
        # 2. Has math notation AND is a medium-to-high score (35-100%)
        has_new_math = (
            len(found_indicators) > 0 or
            (has_math_notation and score >= 35)
        )
        
        if has_new_math:
            details = {
                "indicators_found": found_indicators,
                "has_math_notation": has_math_notation,
                "score": score,
                "potential_type": self._classify_new_math_type(answer, found_indicators)
            }
            return True, details
        
        return False, None
    
    def _classify_new_math_type(self, answer: str, indicators: List[str]) -> str:
        """Classify the type of potential new mathematics"""
        answer_lower = answer.lower()
        
        if any(w in answer_lower for w in ["theorem", "prove", "proof"]):
            return "potential_theorem"
        elif any(w in answer_lower for w in ["formula", "equation"]):
            return "potential_formula"
        elif any(w in answer_lower for w in ["method", "algorithm", "approach"]):
            return "potential_method"
        elif any(w in answer_lower for w in ["conjecture", "hypothesis"]):
            return "potential_conjecture"
        elif any(w in answer_lower for w in ["connection", "relationship"]):
            return "potential_connection"
        else:
            return "potential_insight"
    
    def _should_flag_for_review(self, 
                                 score: int, 
                                 has_new_math: bool,
                                 category: ScoreCategory,
                                 reasoning_analysis: Dict) -> tuple:
        """
        Determine if conversation should be flagged for Manus review.
        
        Flag conditions:
        1. Score 35-74% AND has new math → Flag for review
        2. Score 75-100% AND has new math → Flag for review
        3. Perfect score (100%) → Flag for review (exceptional)
        """
        reasons = []
        
        # Condition 1 & 2: New math at any passing score
        if has_new_math and score >= 35:
            reasons.append(f"New mathematical content detected at {score}% score")
            
        # Condition 3: Perfect score
        if score == 100:
            reasons.append("Perfect score achieved - exceptional performance")
            
        # Additional: Very high reasoning quality with insights
        if reasoning_analysis:
            quality = reasoning_analysis.get("quality", "")
            if quality == "genuine" and score >= 90:
                reasons.append("Genuine high-quality reasoning demonstrated")
                
        should_flag = len(reasons) > 0
        review_reason = "; ".join(reasons) if reasons else None
        
        return should_flag, review_reason
    
    def _save_record(self, record: ConversationRecord):
        """Save record to appropriate files"""
        record_dict = {
            "id": record.id,
            "timestamp": record.timestamp,
            "student": record.student,
            "level": record.level,
            "topic": record.topic,
            "question": record.question,
            "answer": record.answer,
            "score": record.score,
            "category": record.category.value,
            "reasoning_analysis": record.reasoning_analysis,
            "has_new_math": record.has_new_math,
            "new_math_details": record.new_math_details,
            "flagged_for_review": record.flagged_for_review,
            "review_reason": record.review_reason,
            "metadata": record.metadata
        }
        
        # Always save to all_conversations
        self._append_to_file(
            self.base_dir / self.RECORD_DIRS["all"] / "conversations.jsonl",
            record_dict
        )
        
        # Save to score-based directories
        if record.score >= 75:
            self._append_to_file(
                self.base_dir / self.RECORD_DIRS["high_score"] / "conversations.jsonl",
                record_dict
            )
        else:
            self._append_to_file(
                self.base_dir / self.RECORD_DIRS["low_score"] / "conversations.jsonl",
                record_dict
            )
            
        # Save to new_math if applicable
        if record.has_new_math:
            self._append_to_file(
                self.base_dir / self.RECORD_DIRS["new_math"] / "discoveries.jsonl",
                record_dict
            )
            
        # Save to flagged if applicable
        if record.flagged_for_review:
            self._append_to_file(
                self.base_dir / self.RECORD_DIRS["flagged"] / "for_review.jsonl",
                record_dict
            )
            # Also save a summary for quick review
            self._save_review_summary(record)
            
        # Save perfect scores separately
        if record.score == 100:
            self._append_to_file(
                self.base_dir / self.RECORD_DIRS["perfect"] / "perfect_scores.jsonl",
                record_dict
            )
    
    def _append_to_file(self, filepath: Path, data: Dict):
        """Append a record to a JSONL file"""
        with open(filepath, "a") as f:
            f.write(json.dumps(data) + "\n")
            
    def _save_review_summary(self, record: ConversationRecord):
        """Save a summary for Manus review"""
        summary = {
            "id": record.id,
            "timestamp": record.timestamp,
            "student": record.student,
            "level": record.level,
            "score": record.score,
            "review_reason": record.review_reason,
            "has_new_math": record.has_new_math,
            "new_math_type": record.new_math_details.get("potential_type") if record.new_math_details else None,
            "answer_preview": record.answer[:500] + "..." if len(record.answer) > 500 else record.answer,
            "status": "PENDING_REVIEW"
        }
        
        self._append_to_file(
            self.base_dir / self.RECORD_DIRS["flagged"] / "review_queue.jsonl",
            summary
        )
    
    def get_pending_reviews(self) -> List[Dict]:
        """Get all pending reviews for Manus"""
        reviews = []
        review_file = self.base_dir / self.RECORD_DIRS["flagged"] / "review_queue.jsonl"
        
        if review_file.exists():
            with open(review_file, "r") as f:
                for line in f:
                    if line.strip():
                        review = json.loads(line)
                        if review.get("status") == "PENDING_REVIEW":
                            reviews.append(review)
                            
        return reviews
    
    def mark_reviewed(self, record_id: str, review_result: Dict):
        """Mark a record as reviewed by Manus"""
        # This would update the review status
        review_log = {
            "record_id": record_id,
            "reviewed_at": datetime.now().isoformat(),
            "result": review_result
        }
        
        self._append_to_file(
            self.base_dir / self.RECORD_DIRS["flagged"] / "review_log.jsonl",
            review_log
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get recording statistics"""
        stats = {
            "total_records": self.record_count,
            "flagged_for_review": self.flagged_count,
            "new_math_detected": self.new_math_count,
            "directories": {}
        }
        
        for name, dir_name in self.RECORD_DIRS.items():
            dir_path = self.base_dir / dir_name
            if dir_path.exists():
                files = list(dir_path.glob("*.jsonl"))
                total_lines = 0
                for f in files:
                    with open(f, "r") as fp:
                        total_lines += sum(1 for _ in fp)
                stats["directories"][name] = {
                    "files": len(files),
                    "records": total_lines
                }
                
        return stats
    
    def get_new_math_discoveries(self) -> List[Dict]:
        """Get all potential new math discoveries"""
        discoveries = []
        discovery_file = self.base_dir / self.RECORD_DIRS["new_math"] / "discoveries.jsonl"
        
        if discovery_file.exists():
            with open(discovery_file, "r") as f:
                for line in f:
                    if line.strip():
                        discoveries.append(json.loads(line))
                        
        return discoveries


# Manus Review Interface
class ManusReviewInterface:
    """
    Interface for Manus to review flagged conversations and discoveries.
    """
    
    def __init__(self, recorder: ConversationRecorder):
        self.recorder = recorder
        self.review_log = []
        
    def get_review_queue(self) -> List[Dict]:
        """Get items pending Manus review"""
        return self.recorder.get_pending_reviews()
    
    def review_item(self, record_id: str, 
                    is_valid_discovery: bool,
                    verification_notes: str,
                    action_taken: str) -> Dict:
        """
        Manus reviews an item.
        
        Args:
            record_id: ID of the record being reviewed
            is_valid_discovery: Whether this is a genuine new discovery
            verification_notes: Notes from verification against sources
            action_taken: What action was taken (e.g., "verified", "rejected", "needs_more_research")
        """
        review_result = {
            "record_id": record_id,
            "reviewed_by": "Manus",
            "reviewed_at": datetime.now().isoformat(),
            "is_valid_discovery": is_valid_discovery,
            "verification_notes": verification_notes,
            "action_taken": action_taken,
            "status": "REVIEWED"
        }
        
        self.recorder.mark_reviewed(record_id, review_result)
        self.review_log.append(review_result)
        
        return review_result
    
    def get_review_summary(self) -> Dict:
        """Get summary of all reviews"""
        return {
            "total_reviewed": len(self.review_log),
            "valid_discoveries": sum(1 for r in self.review_log if r.get("is_valid_discovery")),
            "rejected": sum(1 for r in self.review_log if not r.get("is_valid_discovery")),
            "pending": len(self.recorder.get_pending_reviews())
        }


if __name__ == "__main__":
    # Test the conversation recorder
    recorder = ConversationRecorder()
    
    # Test recording a conversation with potential new math
    record = recorder.record_conversation(
        student="Stratify",
        level="6",
        topic="algebra",
        question="Solve for x: 2x + 5 = 15",
        answer="""
        I'll solve this step by step.
        
        First, subtract 5 from both sides:
        2x + 5 - 5 = 15 - 5
        2x = 10
        
        Then divide both sides by 2:
        x = 5
        
        Verification: 2(5) + 5 = 10 + 5 = 15 ✓
        
        I also noticed a new relationship: for equations of form ax + b = c,
        the solution is always x = (c - b) / a. This is a generalization
        that could be useful.
        """,
        score=85,
        reasoning_analysis={"quality": "genuine"}
    )
    
    print(f"Record ID: {record.id}")
    print(f"Category: {record.category.value}")
    print(f"Has new math: {record.has_new_math}")
    print(f"Flagged for review: {record.flagged_for_review}")
    print(f"Review reason: {record.review_reason}")
    
    print(f"\nStatistics: {recorder.get_statistics()}")
