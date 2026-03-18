#!/usr/bin/env python3.11
"""
AETHER Character Development & Discipline System

Building solid foundations:
- Character traits that prevent "going haywire"
- Discipline for research-level work
- Increasing proficiency requirements within each grade
- Personality stability for long-term success
"""

import json
import os
import random
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, field, asdict


@dataclass
class CharacterTrait:
    """A character trait to develop."""
    name: str
    description: str
    importance: str  # "foundation", "academic", "research"
    develops_in: List[str]  # Grade levels where this develops most
    
    # Behaviors that demonstrate this trait
    positive_behaviors: List[str]
    negative_behaviors: List[str]  # What happens without this trait


# Core character traits for stable, disciplined learners
CHARACTER_TRAITS = {
    "discipline": CharacterTrait(
        name="Discipline",
        description="Consistency in effort, following through on commitments",
        importance="foundation",
        develops_in=["K", "1", "2", "3", "4", "5"],
        positive_behaviors=[
            "Completes all assigned questions",
            "Maintains consistent study schedule",
            "Follows instructions carefully",
            "Reviews mistakes without excuses"
        ],
        negative_behaviors=[
            "Skips difficult problems",
            "Inconsistent effort",
            "Ignores feedback",
            "Makes excuses for poor performance"
        ]
    ),
    
    "perseverance": CharacterTrait(
        name="Perseverance",
        description="Continuing effort despite difficulty or failure",
        importance="foundation",
        develops_in=["K", "1", "2", "3", "4", "5", "6", "7", "8"],
        positive_behaviors=[
            "Retries failed problems",
            "Asks for help when stuck",
            "Doesn't give up on hard topics",
            "Views failure as learning opportunity"
        ],
        negative_behaviors=[
            "Gives up easily",
            "Avoids challenging material",
            "Becomes frustrated and quits",
            "Blames external factors"
        ]
    ),
    
    "focus": CharacterTrait(
        name="Focus",
        description="Sustained attention on the task at hand",
        importance="foundation",
        develops_in=["K", "1", "2", "3", "4", "5"],
        positive_behaviors=[
            "Stays on topic during problems",
            "Completes quizzes without distraction",
            "Gives full attention to explanations",
            "Avoids tangential thinking during tests"
        ],
        negative_behaviors=[
            "Jumps between topics randomly",
            "Loses track of problem-solving steps",
            "Provides unfocused answers",
            "Gets distracted by unrelated ideas"
        ]
    ),
    
    "integrity": CharacterTrait(
        name="Integrity",
        description="Honest self-assessment and authentic effort",
        importance="foundation",
        develops_in=["K", "1", "2", "3", "4", "5", "6"],
        positive_behaviors=[
            "Admits when doesn't understand",
            "Doesn't pretend to know more than does",
            "Accepts constructive criticism",
            "Honest about mistakes"
        ],
        negative_behaviors=[
            "Pretends to understand when doesn't",
            "Overestimates own abilities",
            "Defensive about errors",
            "Bluffs through answers"
        ]
    ),
    
    "curiosity": CharacterTrait(
        name="Curiosity",
        description="Genuine interest in learning and discovery",
        importance="academic",
        develops_in=["K", "1", "2", "3", "4", "5", "6", "7", "8"],
        positive_behaviors=[
            "Asks thoughtful questions",
            "Explores beyond required material",
            "Shows enthusiasm for new topics",
            "Makes connections between concepts"
        ],
        negative_behaviors=[
            "Only does minimum required",
            "Shows no interest in why things work",
            "Treats learning as chore",
            "Never asks questions"
        ]
    ),
    
    "humility": CharacterTrait(
        name="Humility",
        description="Recognizing limits of knowledge and openness to learning",
        importance="academic",
        develops_in=["3", "4", "5", "6", "7", "8", "9", "10"],
        positive_behaviors=[
            "Acknowledges when wrong",
            "Learns from others' approaches",
            "Doesn't dismiss alternative methods",
            "Celebrates others' successes"
        ],
        negative_behaviors=[
            "Arrogant about abilities",
            "Dismisses feedback",
            "Refuses to consider other approaches",
            "Competitive in unhealthy ways"
        ]
    ),
    
    "patience": CharacterTrait(
        name="Patience",
        description="Ability to work through complex problems methodically",
        importance="academic",
        develops_in=["4", "5", "6", "7", "8", "9", "10", "11", "12"],
        positive_behaviors=[
            "Works through long problems step by step",
            "Doesn't rush to conclusions",
            "Tolerates ambiguity during problem-solving",
            "Waits for understanding to develop"
        ],
        negative_behaviors=[
            "Rushes through problems",
            "Jumps to conclusions",
            "Frustrated by multi-step processes",
            "Wants immediate answers"
        ]
    ),
    
    "rigor": CharacterTrait(
        name="Rigor",
        description="Commitment to precision and thoroughness",
        importance="research",
        develops_in=["9", "10", "11", "12", "UG1", "UG2", "UG3", "UG4"],
        positive_behaviors=[
            "Checks work carefully",
            "Provides complete justifications",
            "Attends to edge cases",
            "Maintains high standards"
        ],
        negative_behaviors=[
            "Sloppy work",
            "Skips verification steps",
            "Ignores special cases",
            "Accepts 'good enough'"
        ]
    ),
    
    "independence": CharacterTrait(
        name="Independence",
        description="Ability to work and think autonomously",
        importance="research",
        develops_in=["11", "12", "UG1", "UG2", "UG3", "UG4", "MS1", "MS2"],
        positive_behaviors=[
            "Formulates own questions",
            "Develops original approaches",
            "Self-directs learning",
            "Takes initiative"
        ],
        negative_behaviors=[
            "Always needs guidance",
            "Can't work without instructions",
            "Waits to be told what to do",
            "Copies others' approaches"
        ]
    ),
    
    "resilience": CharacterTrait(
        name="Resilience",
        description="Ability to recover from setbacks and continue",
        importance="research",
        develops_in=["MS1", "MS2", "PHD1", "PHD2", "PHD3", "POSTDOC", "RES"],
        positive_behaviors=[
            "Bounces back from failures",
            "Maintains motivation through difficulties",
            "Adapts approach after setbacks",
            "Stays positive during challenges"
        ],
        negative_behaviors=[
            "Devastated by failures",
            "Loses motivation easily",
            "Gives up after setbacks",
            "Becomes negative or cynical"
        ]
    )
}


@dataclass
class ProficiencyPhase:
    """A phase within a grade level."""
    name: str
    min_score: float
    description: str
    character_focus: List[str]  # Traits to develop in this phase


# Proficiency phases within each grade
PROFICIENCY_PHASES = {
    "entry": ProficiencyPhase(
        name="Entry",
        min_score=55.0,
        description="Just beginning to learn the material",
        character_focus=["discipline", "focus"]
    ),
    "developing": ProficiencyPhase(
        name="Developing", 
        min_score=65.0,
        description="Building understanding and skills",
        character_focus=["perseverance", "curiosity"]
    ),
    "proficient": ProficiencyPhase(
        name="Proficient",
        min_score=75.0,
        description="Solid grasp of core concepts",
        character_focus=["integrity", "patience"]
    ),
    "mastery": ProficiencyPhase(
        name="Mastery",
        min_score=85.0,
        description="Deep understanding, ready to advance",
        character_focus=["humility", "rigor"]
    )
}


@dataclass
class GradeRequirements:
    """Increasing requirements within a grade."""
    grade: str
    
    # Phase thresholds (increase as student progresses)
    entry_threshold: float
    developing_threshold: float
    proficient_threshold: float
    mastery_threshold: float  # Must reach this to graduate
    
    # Minimum questions at each phase
    min_questions_entry: int
    min_questions_developing: int
    min_questions_proficient: int
    min_questions_mastery: int
    
    # Character traits emphasized
    primary_traits: List[str]
    secondary_traits: List[str]


def calculate_grade_requirements(grade: str, grade_index: int) -> GradeRequirements:
    """
    Calculate requirements for a grade based on position in curriculum.
    
    Early grades: Focus on character, moderate academic requirements
    Later grades: Higher academic requirements, build on character foundation
    """
    
    # Base thresholds increase with grade level
    base_entry = 50 + (grade_index * 1.5)
    base_developing = 60 + (grade_index * 1.5)
    base_proficient = 70 + (grade_index * 1.5)
    base_mastery = 80 + (grade_index * 1.5)
    
    # Cap at reasonable levels
    entry = min(base_entry, 65)
    developing = min(base_developing, 75)
    proficient = min(base_proficient, 85)
    mastery = min(base_mastery, 92)
    
    # Questions required increase with grade
    base_questions = 15 + (grade_index * 3)
    
    # Determine primary traits based on grade level
    if grade_index < 6:  # Elementary (K-5)
        primary = ["discipline", "focus", "perseverance", "integrity"]
        secondary = ["curiosity", "humility"]
    elif grade_index < 9:  # Middle (6-8)
        primary = ["perseverance", "curiosity", "patience"]
        secondary = ["humility", "rigor"]
    elif grade_index < 13:  # High (9-12)
        primary = ["rigor", "patience", "independence"]
        secondary = ["resilience"]
    elif grade_index < 17:  # Undergraduate
        primary = ["rigor", "independence", "resilience"]
        secondary = ["humility"]
    else:  # Graduate/Research
        primary = ["resilience", "independence", "rigor"]
        secondary = ["humility", "patience"]
    
    return GradeRequirements(
        grade=grade,
        entry_threshold=entry,
        developing_threshold=developing,
        proficient_threshold=proficient,
        mastery_threshold=mastery,
        min_questions_entry=base_questions,
        min_questions_developing=base_questions + 5,
        min_questions_proficient=base_questions + 10,
        min_questions_mastery=base_questions + 15,
        primary_traits=primary,
        secondary_traits=secondary
    )


class CharacterDevelopmentTracker:
    """Track character development for a student."""
    
    def __init__(self, student_name: str, storage_dir: str = "/home/ubuntu/aether/memory"):
        self.student_name = student_name
        self.storage_dir = storage_dir
        self.storage_path = os.path.join(storage_dir, f"{student_name.lower()}_character.json")
        
        # Character scores (0-100)
        self.trait_scores: Dict[str, float] = {
            trait: 50.0 for trait in CHARACTER_TRAITS
        }
        
        # Behavior history
        self.positive_behaviors: List[Dict] = []
        self.negative_behaviors: List[Dict] = []
        
        # Discipline metrics
        self.consecutive_completions: int = 0
        self.total_completions: int = 0
        self.total_attempts: int = 0
        self.gave_up_count: int = 0
        
        # Focus metrics
        self.on_topic_responses: int = 0
        self.off_topic_responses: int = 0
        
        # Perseverance metrics
        self.retries_after_failure: int = 0
        self.quit_after_failure: int = 0
        
        os.makedirs(storage_dir, exist_ok=True)
        self._load()
    
    def _load(self):
        """Load character data."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.trait_scores = data.get("trait_scores", self.trait_scores)
                    self.positive_behaviors = data.get("positive_behaviors", [])
                    self.negative_behaviors = data.get("negative_behaviors", [])
                    self.consecutive_completions = data.get("consecutive_completions", 0)
                    self.total_completions = data.get("total_completions", 0)
                    self.total_attempts = data.get("total_attempts", 0)
                    self.gave_up_count = data.get("gave_up_count", 0)
                    self.on_topic_responses = data.get("on_topic_responses", 0)
                    self.off_topic_responses = data.get("off_topic_responses", 0)
                    self.retries_after_failure = data.get("retries_after_failure", 0)
                    self.quit_after_failure = data.get("quit_after_failure", 0)
            except:
                pass
    
    def save(self):
        """Save character data."""
        data = {
            "student_name": self.student_name,
            "trait_scores": self.trait_scores,
            "positive_behaviors": self.positive_behaviors[-100:],  # Keep last 100
            "negative_behaviors": self.negative_behaviors[-100:],
            "consecutive_completions": self.consecutive_completions,
            "total_completions": self.total_completions,
            "total_attempts": self.total_attempts,
            "gave_up_count": self.gave_up_count,
            "on_topic_responses": self.on_topic_responses,
            "off_topic_responses": self.off_topic_responses,
            "retries_after_failure": self.retries_after_failure,
            "quit_after_failure": self.quit_after_failure,
            "last_updated": datetime.now().isoformat()
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_quiz_behavior(self, completed: bool, score: float, 
                             was_difficult: bool, retried: bool = False,
                             on_topic: bool = True):
        """Record behavior during a quiz."""
        self.total_attempts += 1
        
        # Discipline: Did they complete?
        if completed:
            self.total_completions += 1
            self.consecutive_completions += 1
            self._adjust_trait("discipline", 2)
        else:
            self.consecutive_completions = 0
            self.gave_up_count += 1
            self._adjust_trait("discipline", -3)
        
        # Perseverance: Did they retry after difficulty?
        if was_difficult:
            if retried or completed:
                self.retries_after_failure += 1
                self._adjust_trait("perseverance", 3)
            else:
                self.quit_after_failure += 1
                self._adjust_trait("perseverance", -2)
        
        # Focus: Were they on topic?
        if on_topic:
            self.on_topic_responses += 1
            self._adjust_trait("focus", 1)
        else:
            self.off_topic_responses += 1
            self._adjust_trait("focus", -2)
        
        # Integrity: Based on honest effort (score reflects genuine attempt)
        if score >= 30:  # Made genuine effort
            self._adjust_trait("integrity", 1)
        
        # Curiosity: Based on engagement with material
        if score >= 70:
            self._adjust_trait("curiosity", 1)
        
        # Humility: Accepting lower scores gracefully (implicit)
        if score < 60 and completed:  # Finished despite low score
            self._adjust_trait("humility", 1)
        
        self.save()
    
    def record_positive_behavior(self, trait: str, behavior: str, context: str = ""):
        """Record a positive behavior."""
        self.positive_behaviors.append({
            "trait": trait,
            "behavior": behavior,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        self._adjust_trait(trait, 3)
        self.save()
    
    def record_negative_behavior(self, trait: str, behavior: str, context: str = ""):
        """Record a negative behavior."""
        self.negative_behaviors.append({
            "trait": trait,
            "behavior": behavior,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        self._adjust_trait(trait, -3)
        self.save()
    
    def _adjust_trait(self, trait: str, amount: float):
        """Adjust a trait score."""
        if trait in self.trait_scores:
            current = self.trait_scores[trait]
            # Slower to increase, faster to decrease (character is hard to build)
            if amount > 0:
                amount *= 0.7  # Harder to gain
            self.trait_scores[trait] = max(0, min(100, current + amount))
    
    def get_current_phase(self, grade: str, grade_index: int) -> Tuple[str, float]:
        """
        Determine current proficiency phase based on character development.
        
        Returns (phase_name, required_score)
        """
        reqs = calculate_grade_requirements(grade, grade_index)
        
        # Character score affects phase requirements
        avg_primary = sum(self.trait_scores.get(t, 50) for t in reqs.primary_traits) / len(reqs.primary_traits)
        
        # Strong character = can handle higher requirements
        # Weak character = needs to build foundation first
        
        if avg_primary >= 70:
            # Good character, can attempt mastery
            return ("mastery", reqs.mastery_threshold)
        elif avg_primary >= 60:
            # Developing character, proficient phase
            return ("proficient", reqs.proficient_threshold)
        elif avg_primary >= 50:
            # Building character, developing phase
            return ("developing", reqs.developing_threshold)
        else:
            # Need character work, entry phase
            return ("entry", reqs.entry_threshold)
    
    def get_discipline_score(self) -> float:
        """Get overall discipline score."""
        if self.total_attempts == 0:
            return 50.0
        
        completion_rate = self.total_completions / self.total_attempts
        consistency = min(self.consecutive_completions / 10, 1.0)  # Max at 10 consecutive
        
        return (completion_rate * 50) + (consistency * 30) + (self.trait_scores.get("discipline", 50) * 0.2)
    
    def get_character_summary(self) -> Dict:
        """Get summary of character development."""
        # Top traits
        sorted_traits = sorted(self.trait_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Areas needing work
        weak_traits = [t for t, s in sorted_traits if s < 50]
        
        # Overall character score
        overall = sum(self.trait_scores.values()) / len(self.trait_scores)
        
        return {
            "overall_score": overall,
            "top_traits": sorted_traits[:3],
            "weak_traits": weak_traits[:3],
            "discipline_score": self.get_discipline_score(),
            "completion_rate": self.total_completions / max(1, self.total_attempts),
            "perseverance_rate": self.retries_after_failure / max(1, self.retries_after_failure + self.quit_after_failure),
            "focus_rate": self.on_topic_responses / max(1, self.on_topic_responses + self.off_topic_responses),
            "all_traits": dict(sorted_traits)
        }
    
    def is_ready_for_graduation(self, grade: str, grade_index: int) -> Tuple[bool, str]:
        """
        Check if character is developed enough to graduate.
        
        Early grades require strong foundation traits.
        """
        reqs = calculate_grade_requirements(grade, grade_index)
        
        # Check primary traits
        for trait in reqs.primary_traits:
            score = self.trait_scores.get(trait, 50)
            if score < 60:
                return (False, f"Need to develop {trait} (currently {score:.0f}, need 60+)")
        
        # Check discipline specifically for early grades
        if grade_index < 6:  # Elementary
            if self.trait_scores.get("discipline", 50) < 65:
                return (False, "Need stronger discipline foundation")
            if self.trait_scores.get("focus", 50) < 60:
                return (False, "Need better focus skills")
        
        return (True, "Character development sufficient for graduation")


class DisciplineExercise:
    """Exercises to build discipline and character."""
    
    EXERCISES = {
        "discipline": [
            {
                "name": "Complete the Set",
                "description": "Answer all 5 questions without skipping any",
                "success_boost": 5,
                "failure_penalty": -2
            },
            {
                "name": "Follow the Steps",
                "description": "Solve this problem showing every step clearly",
                "success_boost": 4,
                "failure_penalty": -1
            },
            {
                "name": "Review and Correct",
                "description": "Find and fix the error in this solution",
                "success_boost": 4,
                "failure_penalty": -1
            }
        ],
        "perseverance": [
            {
                "name": "Try Again",
                "description": "This problem is hard. Attempt it 3 times with different approaches",
                "success_boost": 6,
                "failure_penalty": -1
            },
            {
                "name": "Don't Give Up",
                "description": "Work through this challenging problem to the end",
                "success_boost": 5,
                "failure_penalty": -1
            }
        ],
        "focus": [
            {
                "name": "Stay on Track",
                "description": "Answer only what's asked, nothing extra",
                "success_boost": 4,
                "failure_penalty": -2
            },
            {
                "name": "One Step at a Time",
                "description": "Complete each part before moving to the next",
                "success_boost": 4,
                "failure_penalty": -1
            }
        ],
        "integrity": [
            {
                "name": "Honest Assessment",
                "description": "Rate your confidence in your answer (1-10) before seeing the result",
                "success_boost": 3,
                "failure_penalty": 0  # No penalty for honesty
            },
            {
                "name": "Admit Uncertainty",
                "description": "Identify what you're unsure about in your answer",
                "success_boost": 4,
                "failure_penalty": 0
            }
        ]
    }
    
    @classmethod
    def get_exercise(cls, trait: str) -> Dict:
        """Get a random exercise for a trait."""
        exercises = cls.EXERCISES.get(trait, cls.EXERCISES["discipline"])
        return random.choice(exercises)
    
    @classmethod
    def get_exercise_for_weak_trait(cls, character_tracker: CharacterDevelopmentTracker) -> Tuple[str, Dict]:
        """Get an exercise targeting the weakest trait."""
        summary = character_tracker.get_character_summary()
        weak_traits = summary.get("weak_traits", ["discipline"])
        
        if weak_traits:
            trait = weak_traits[0]
        else:
            trait = "discipline"  # Default
        
        return (trait, cls.get_exercise(trait))
