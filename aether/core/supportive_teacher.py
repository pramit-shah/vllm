#!/usr/bin/env python3.11
"""
AETHER Supportive Teacher Module

A hands-on, encouraging approach to teaching AI frameworks.
Like a patient teacher who guides students through difficulties
rather than just marking them right or wrong.
"""

import os
import yaml
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Try to import OpenAI
try:
    from openai import OpenAI
    client = OpenAI()
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False
    client = None


class TeachingStyle(Enum):
    HANDS_ON = "hands_on"
    TRADITIONAL = "traditional"
    ADAPTIVE = "adaptive"


class ScoreCategory(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    DEVELOPING = "developing"
    EMERGING = "emerging"
    BEGINNING = "beginning"


@dataclass
class LearnerProgress:
    """Track a learner's progress over time."""
    framework: str
    current_level: int = 1
    total_questions: int = 0
    scores: List[float] = field(default_factory=list)
    hints_used: int = 0
    attempts_used: int = 0
    milestones: List[str] = field(default_factory=list)
    streak: int = 0
    best_streak: int = 0
    improvements: List[Dict] = field(default_factory=list)
    
    def add_score(self, score: float) -> Dict:
        """Add a score and return progress info."""
        self.scores.append(score)
        self.total_questions += 1
        
        result = {
            "score": score,
            "total": self.total_questions,
            "average": sum(self.scores) / len(self.scores),
            "trend": self._calculate_trend(),
            "milestones_earned": []
        }
        
        # Track streak
        if score >= 70:
            self.streak += 1
            if self.streak > self.best_streak:
                self.best_streak = self.streak
            if self.streak == 3:
                self.milestones.append("streak_of_3_good")
                result["milestones_earned"].append("streak_of_3_good")
        else:
            self.streak = 0
        
        # Check for first good/excellent
        if score >= 85 and "first_excellent_score" not in self.milestones:
            self.milestones.append("first_excellent_score")
            result["milestones_earned"].append("first_excellent_score")
        elif score >= 70 and "first_good_score" not in self.milestones:
            self.milestones.append("first_good_score")
            result["milestones_earned"].append("first_good_score")
        
        return result
    
    def _calculate_trend(self) -> str:
        """Calculate if scores are improving."""
        if len(self.scores) < 5:
            return "building"
        
        recent = self.scores[-5:]
        earlier = self.scores[-10:-5] if len(self.scores) >= 10 else self.scores[:5]
        
        recent_avg = sum(recent) / len(recent)
        earlier_avg = sum(earlier) / len(earlier)
        
        if recent_avg > earlier_avg + 5:
            return "improving"
        elif recent_avg < earlier_avg - 5:
            return "needs_support"
        else:
            return "steady"


class TrainingConfig:
    """Load and manage training configuration."""
    
    def __init__(self, config_path: str = "/home/ubuntu/aether/config/training_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Return default configuration."""
        return {
            "teaching_style": "hands_on",
            "difficulty": {
                "starting_level": 1,
                "total_levels": 10,
                "advancement_threshold": 60,
                "questions_per_level": 5
            },
            "scoring": {
                "partial_credit": True,
                "minimum_score": 20,
                "reasoning_bonus": 10,
                "ranges": {
                    "excellent": 85,
                    "good": 70,
                    "developing": 50,
                    "emerging": 30
                }
            },
            "support": {
                "hints_enabled": True,
                "hints_per_question": 3,
                "examples_before_questions": True,
                "multiple_attempts": True,
                "max_attempts": 3,
                "encouragement": True
            },
            "feedback": {
                "tone": "encouraging",
                "positive_first": True,
                "celebrate_progress": True
            }
        }
    
    def get(self, *keys, default=None):
        """Get a nested config value."""
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def reload(self):
        """Reload configuration from file."""
        self.config = self._load_config()


class SupportiveTeacher:
    """
    A supportive, hands-on teacher for AI frameworks.
    
    Philosophy:
    - Start with what they know
    - Build understanding step by step
    - Celebrate progress, not just perfection
    - Provide support when struggling
    - Never discourage, always guide
    """
    
    def __init__(self, config: TrainingConfig = None, model: str = "gpt-4.1-nano"):
        self.config = config or TrainingConfig()
        self.model = model
        self.learners: Dict[str, LearnerProgress] = {}
        self.log_dir = "/home/ubuntu/aether/logs"
        os.makedirs(self.log_dir, exist_ok=True)
    
    def register_learner(self, framework: str) -> LearnerProgress:
        """Register a new learner."""
        progress = LearnerProgress(
            framework=framework,
            current_level=self.config.get("difficulty", "starting_level", default=1)
        )
        self.learners[framework] = progress
        print(f"  📚 Welcome, {framework}! Let's learn together.")
        return progress
    
    def get_learner(self, framework: str) -> Optional[LearnerProgress]:
        """Get a learner's progress."""
        return self.learners.get(framework)
    
    def categorize_score(self, score: float) -> ScoreCategory:
        """Categorize a score with encouraging labels."""
        ranges = self.config.get("scoring", "ranges", default={})
        
        if score >= ranges.get("excellent", 85):
            return ScoreCategory.EXCELLENT
        elif score >= ranges.get("good", 70):
            return ScoreCategory.GOOD
        elif score >= ranges.get("developing", 50):
            return ScoreCategory.DEVELOPING
        elif score >= ranges.get("emerging", 30):
            return ScoreCategory.EMERGING
        else:
            return ScoreCategory.BEGINNING
    
    def provide_worked_example(self, topic: str, level: int) -> Dict:
        """Provide a worked example before testing."""
        
        if not AI_AVAILABLE:
            return self._simulated_example(topic, level)
        
        prompt = f"""Create a worked example for teaching {topic} at difficulty level {level}/10.

Be a supportive teacher:
1. Start with a clear, simple problem
2. Show EVERY step of the solution
3. Explain WHY each step works
4. Point out common mistakes to avoid
5. End with a summary of key points

Format:
PROBLEM: [simple, clear problem]
STEP 1: [first step with explanation]
STEP 2: [next step with explanation]
...
KEY INSIGHT: [the main takeaway]
COMMON MISTAKE: [what to watch out for]
SUMMARY: [brief recap]
"""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a patient, encouraging math/physics teacher. Make concepts accessible and build confidence."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return {
                "topic": topic,
                "level": level,
                "example": content,
                "type": "worked_example"
            }
        except Exception as e:
            return {"error": str(e), "topic": topic}
    
    def _simulated_example(self, topic: str, level: int) -> Dict:
        """Simulated worked example."""
        return {
            "topic": topic,
            "level": level,
            "example": f"""
PROBLEM: Simple {topic} problem at level {level}

STEP 1: First, identify what we're working with...
STEP 2: Apply the basic principle...
STEP 3: Simplify and solve...

KEY INSIGHT: The key is understanding the underlying pattern.
COMMON MISTAKE: Don't rush - check each step.
SUMMARY: {topic} follows from basic principles when approached step by step.
""",
            "type": "worked_example"
        }
    
    def create_supportive_question(self, topic: str, level: int, learner: LearnerProgress) -> Dict:
        """Create a question with built-in support."""
        
        # Adjust level based on learner's trend
        adjusted_level = level
        if learner._calculate_trend() == "needs_support":
            adjusted_level = max(1, level - 1)
        
        if not AI_AVAILABLE:
            return self._simulated_question(topic, adjusted_level)
        
        prompt = f"""Create a supportive learning question about {topic} at level {adjusted_level}/10.

This learner has answered {learner.total_questions} questions with average {sum(learner.scores)/len(learner.scores) if learner.scores else 0:.0f}%.

Create a question that:
1. Is clear and unambiguous
2. Builds on fundamental concepts
3. Has a clear path to the answer
4. Includes helpful hints

Format:
QUESTION: [clear question]
CONTEXT: [helpful background]
HINT 1: [gentle nudge in right direction]
HINT 2: [more specific guidance]
HINT 3: [almost gives it away]
CONCEPTS: [list of concepts being tested]
DIFFICULTY: {adjusted_level}/10
"""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are creating educational content. Be clear, supportive, and build confidence."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.6
            )
            
            content = response.choices[0].message.content
            
            # Parse hints
            hints = []
            for i in range(1, 4):
                if f"HINT {i}:" in content:
                    hint = content.split(f"HINT {i}:")[1].split("\n")[0].strip()
                    hints.append(hint)
            
            return {
                "question_id": f"{topic[:3].upper()}_L{adjusted_level}_Q{learner.total_questions + 1}",
                "topic": topic,
                "level": adjusted_level,
                "content": content,
                "hints": hints,
                "attempts_allowed": self.config.get("support", "max_attempts", default=3)
            }
        except Exception as e:
            return self._simulated_question(topic, adjusted_level)
    
    def _simulated_question(self, topic: str, level: int) -> Dict:
        """Simulated question."""
        return {
            "question_id": f"{topic[:3].upper()}_L{level}_SIM",
            "topic": topic,
            "level": level,
            "content": f"Explain the key concepts of {topic} at a basic level.",
            "hints": [
                "Start by defining the basic terms",
                "Think about how this connects to what you know",
                "Consider a simple example first"
            ],
            "attempts_allowed": 3
        }
    
    def evaluate_with_support(self, question: Dict, answer: str, 
                              learner: LearnerProgress, attempt: int = 1) -> Dict:
        """Evaluate an answer with supportive feedback."""
        
        if not AI_AVAILABLE:
            return self._simulated_evaluation(question, answer, learner, attempt)
        
        prompt = f"""Evaluate this answer as a supportive teacher.

QUESTION: {question.get('content', '')[:1000]}
STUDENT'S ANSWER: {answer[:2000]}
ATTEMPT: {attempt} of {question.get('attempts_allowed', 3)}

Evaluate with encouragement:
1. First, identify what they got RIGHT
2. Give partial credit for good reasoning
3. Gently point out areas to improve
4. Provide specific, actionable feedback
5. End with encouragement

Scoring (be generous with partial credit):
- Start at {self.config.get('scoring', 'minimum_score', default=20)} minimum
- Add points for correct concepts
- Add {self.config.get('scoring', 'reasoning_bonus', default=10)} bonus for good reasoning
- Add {self.config.get('scoring', 'effort_bonus', default=5)} for effort/attempt

Format:
WHAT YOU DID WELL: [specific positives]
SCORE BREAKDOWN:
  - Base: [points]
  - Correct concepts: [points]
  - Reasoning bonus: [points]
  - Effort bonus: [points]
TOTAL SCORE: [0-100]
AREAS TO DEVELOP: [gentle suggestions]
ENCOURAGEMENT: [positive message]
NEXT STEP: [what to focus on next]
"""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an encouraging teacher. Find the good in every answer. Build confidence while guiding improvement."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.4
            )
            
            content = response.choices[0].message.content
            
            # Extract score
            import re
            score_match = re.search(r'TOTAL SCORE:\s*(\d+)', content)
            score = int(score_match.group(1)) if score_match else 50
            
            # Ensure minimum score
            min_score = self.config.get("scoring", "minimum_score", default=20)
            score = max(min_score, score)
            
            # Categorize
            category = self.categorize_score(score)
            
            # Get encouragement message
            messages = self.config.get("feedback", "messages", default={})
            encouragement = messages.get(category.value, "Keep going!")
            
            # Record progress
            progress_info = learner.add_score(score)
            
            return {
                "score": score,
                "category": category.value,
                "feedback": content,
                "encouragement": encouragement,
                "progress": progress_info,
                "attempt": attempt,
                "can_retry": attempt < question.get("attempts_allowed", 3) and score < 70
            }
            
        except Exception as e:
            return self._simulated_evaluation(question, answer, learner, attempt)
    
    def _simulated_evaluation(self, question: Dict, answer: str, 
                              learner: LearnerProgress, attempt: int) -> Dict:
        """Simulated evaluation."""
        import random
        
        # More generous scoring
        base = 40 + random.randint(0, 30)
        reasoning_bonus = random.randint(5, 15)
        effort_bonus = 5
        score = min(100, base + reasoning_bonus + effort_bonus)
        
        category = self.categorize_score(score)
        progress_info = learner.add_score(score)
        
        return {
            "score": score,
            "category": category.value,
            "feedback": f"""
WHAT YOU DID WELL: You attempted the problem and showed effort.

SCORE BREAKDOWN:
  - Base: {base}
  - Reasoning bonus: {reasoning_bonus}
  - Effort bonus: {effort_bonus}
TOTAL SCORE: {score}

AREAS TO DEVELOP: Continue building on these foundations.
ENCOURAGEMENT: Great effort! Every attempt helps you learn.
NEXT STEP: Review the worked example and try again.
""",
            "encouragement": "Keep going! You're making progress.",
            "progress": progress_info,
            "attempt": attempt,
            "can_retry": attempt < 3 and score < 70
        }
    
    def check_level_advancement(self, learner: LearnerProgress) -> Dict:
        """Check if learner should advance to next level."""
        
        questions_per_level = self.config.get("difficulty", "questions_per_level", default=5)
        advancement_threshold = self.config.get("difficulty", "advancement_threshold", default=60)
        skip_threshold = self.config.get("difficulty", "skip_threshold", default=85)
        
        # Get recent scores for current level
        recent = learner.scores[-questions_per_level:] if len(learner.scores) >= questions_per_level else learner.scores
        
        if not recent:
            return {"advance": False, "reason": "Need more questions"}
        
        avg = sum(recent) / len(recent)
        
        result = {
            "current_level": learner.current_level,
            "recent_average": avg,
            "questions_at_level": len(recent),
            "threshold": advancement_threshold,
            "advance": False,
            "skip": False
        }
        
        if len(recent) >= questions_per_level:
            if avg >= skip_threshold and self.config.get("difficulty", "allow_skip", default=True):
                result["advance"] = True
                result["skip"] = True
                result["new_level"] = min(learner.current_level + 2, 10)
                result["message"] = f"🌟 Excellent! Skipping ahead to level {result['new_level']}!"
                learner.current_level = result["new_level"]
                learner.milestones.append("level_advancement")
            elif avg >= advancement_threshold:
                result["advance"] = True
                result["new_level"] = min(learner.current_level + 1, 10)
                result["message"] = f"🎉 Great progress! Moving to level {result['new_level']}!"
                learner.current_level = result["new_level"]
                learner.milestones.append("level_advancement")
            else:
                result["message"] = f"Keep practicing at level {learner.current_level}. You're at {avg:.0f}%, need {advancement_threshold}%."
        else:
            result["message"] = f"Complete {questions_per_level - len(recent)} more questions at this level."
        
        return result
    
    def provide_support_if_struggling(self, learner: LearnerProgress) -> Optional[Dict]:
        """Provide extra support if learner is struggling."""
        
        struggle_threshold = self.config.get("support", "struggle_threshold", default=2)
        
        if len(learner.scores) < struggle_threshold:
            return None
        
        recent = learner.scores[-struggle_threshold:]
        if all(s < 50 for s in recent):
            return {
                "type": "extra_support",
                "message": "I notice you're finding this challenging. Let's take a step back and review the basics together.",
                "suggestions": [
                    "Review the worked examples again",
                    "Try a simpler version of this problem",
                    "Let's break this down into smaller steps",
                    "Would you like me to explain the concept differently?"
                ],
                "offer_simpler": self.config.get("support", "offer_simpler", default=True)
            }
        
        return None
    
    def log_session(self, learner: LearnerProgress, session_data: Dict):
        """Log a learning session."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "framework": learner.framework,
            "level": learner.current_level,
            "total_questions": learner.total_questions,
            "average_score": sum(learner.scores) / len(learner.scores) if learner.scores else 0,
            "trend": learner._calculate_trend(),
            "milestones": learner.milestones,
            "streak": learner.streak,
            "best_streak": learner.best_streak,
            **session_data
        }
        
        log_path = os.path.join(self.log_dir, "supportive_learning.jsonl")
        with open(log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        return log_entry


# Singleton instance
_teacher = None

def get_supportive_teacher() -> SupportiveTeacher:
    """Get the singleton supportive teacher instance."""
    global _teacher
    if _teacher is None:
        _teacher = SupportiveTeacher()
    return _teacher
