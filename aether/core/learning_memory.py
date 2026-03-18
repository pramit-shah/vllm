#!/usr/bin/env python3.11
"""
AETHER Learning Memory System

Persistent storage for learning progress, allowing:
- Resume from where you left off
- Build on previous successes
- Track long-term improvement
- Remember what works for each framework
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class ConceptMastery:
    """Track mastery of a specific concept."""
    concept: str
    attempts: int = 0
    successes: int = 0
    best_score: float = 0
    last_score: float = 0
    mastered: bool = False
    notes: List[str] = field(default_factory=list)
    
    def update(self, score: float, note: str = None):
        """Update mastery with new attempt."""
        self.attempts += 1
        self.last_score = score
        if score > self.best_score:
            self.best_score = score
        if score >= 70:
            self.successes += 1
        if self.successes >= 3 and self.best_score >= 80:
            self.mastered = True
        if note:
            self.notes.append(note)
    
    @property
    def success_rate(self) -> float:
        return (self.successes / self.attempts * 100) if self.attempts > 0 else 0


@dataclass
class LearningSession:
    """Record of a learning session."""
    session_id: str
    framework: str
    start_time: str
    end_time: str = None
    questions_answered: int = 0
    average_score: float = 0
    level_start: int = 1
    level_end: int = 1
    milestones: List[str] = field(default_factory=list)
    breaks_taken: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class FrameworkMemory:
    """Complete memory for a framework."""
    framework: str
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Progress tracking
    current_level: int = 1
    total_questions: int = 0
    total_score: float = 0
    all_scores: List[float] = field(default_factory=list)
    
    # Mastery tracking
    concepts: Dict[str, Dict] = field(default_factory=dict)
    
    # Session history
    sessions: List[Dict] = field(default_factory=list)
    
    # Achievements
    milestones: List[str] = field(default_factory=list)
    best_streak: int = 0
    current_streak: int = 0
    
    # Learning preferences (what works for this framework)
    preferred_hint_level: int = 2
    optimal_break_frequency: int = 10
    strongest_topics: List[str] = field(default_factory=list)
    weakest_topics: List[str] = field(default_factory=list)
    
    @property
    def average_score(self) -> float:
        return self.total_score / self.total_questions if self.total_questions > 0 else 0
    
    @property
    def improvement_rate(self) -> float:
        """Calculate improvement over time."""
        if len(self.all_scores) < 10:
            return 0
        first_10 = sum(self.all_scores[:10]) / 10
        last_10 = sum(self.all_scores[-10:]) / 10
        return last_10 - first_10
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FrameworkMemory':
        return cls(**data)


class LearningMemoryStore:
    """Persistent storage for learning memory."""
    
    def __init__(self, storage_dir: str = "/home/ubuntu/aether/memory"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.memories: Dict[str, FrameworkMemory] = {}
        self._load_all()
    
    def _get_path(self, framework: str) -> str:
        """Get storage path for a framework."""
        return os.path.join(self.storage_dir, f"{framework.lower()}_memory.json")
    
    def _load_all(self):
        """Load all existing memories."""
        for filename in os.listdir(self.storage_dir):
            if filename.endswith("_memory.json"):
                framework = filename.replace("_memory.json", "").title()
                self._load(framework)
    
    def _load(self, framework: str) -> Optional[FrameworkMemory]:
        """Load memory for a framework."""
        path = self._get_path(framework)
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    memory = FrameworkMemory.from_dict(data)
                    self.memories[framework] = memory
                    return memory
            except Exception as e:
                print(f"Error loading memory for {framework}: {e}")
        return None
    
    def _save(self, framework: str):
        """Save memory for a framework."""
        if framework in self.memories:
            path = self._get_path(framework)
            memory = self.memories[framework]
            memory.last_updated = datetime.now().isoformat()
            with open(path, 'w') as f:
                json.dump(memory.to_dict(), f, indent=2)
    
    def get_or_create(self, framework: str) -> FrameworkMemory:
        """Get existing memory or create new one."""
        if framework not in self.memories:
            self.memories[framework] = FrameworkMemory(framework=framework)
            self._save(framework)
        return self.memories[framework]
    
    def record_answer(self, framework: str, score: float, concept: str = None, 
                      question_id: str = None) -> Dict:
        """Record an answer and return progress info."""
        memory = self.get_or_create(framework)
        
        # Update totals
        memory.total_questions += 1
        memory.total_score += score
        memory.all_scores.append(score)
        
        # Update streak
        if score >= 70:
            memory.current_streak += 1
            if memory.current_streak > memory.best_streak:
                memory.best_streak = memory.current_streak
        else:
            memory.current_streak = 0
        
        # Update concept mastery
        if concept:
            if concept not in memory.concepts:
                memory.concepts[concept] = {
                    "attempts": 0, "successes": 0, 
                    "best_score": 0, "last_score": 0
                }
            c = memory.concepts[concept]
            c["attempts"] += 1
            c["last_score"] = score
            if score > c["best_score"]:
                c["best_score"] = score
            if score >= 70:
                c["successes"] += 1
        
        # Check for milestones
        milestones_earned = []
        if memory.total_questions == 10 and "10_questions" not in memory.milestones:
            memory.milestones.append("10_questions")
            milestones_earned.append("10_questions")
        if memory.total_questions == 50 and "50_questions" not in memory.milestones:
            memory.milestones.append("50_questions")
            milestones_earned.append("50_questions")
        if memory.total_questions == 100 and "100_questions" not in memory.milestones:
            memory.milestones.append("100_questions")
            milestones_earned.append("100_questions")
        if memory.best_streak >= 5 and "streak_5" not in memory.milestones:
            memory.milestones.append("streak_5")
            milestones_earned.append("streak_5")
        if memory.best_streak >= 10 and "streak_10" not in memory.milestones:
            memory.milestones.append("streak_10")
            milestones_earned.append("streak_10")
        if memory.average_score >= 70 and memory.total_questions >= 20 and "avg_70" not in memory.milestones:
            memory.milestones.append("avg_70")
            milestones_earned.append("avg_70")
        
        # Save
        self._save(framework)
        
        return {
            "total_questions": memory.total_questions,
            "average_score": memory.average_score,
            "current_streak": memory.current_streak,
            "best_streak": memory.best_streak,
            "improvement_rate": memory.improvement_rate,
            "milestones_earned": milestones_earned
        }
    
    def update_level(self, framework: str, new_level: int):
        """Update framework's current level."""
        memory = self.get_or_create(framework)
        if new_level > memory.current_level:
            memory.current_level = new_level
            if f"level_{new_level}" not in memory.milestones:
                memory.milestones.append(f"level_{new_level}")
        self._save(framework)
    
    def start_session(self, framework: str) -> str:
        """Start a new learning session."""
        memory = self.get_or_create(framework)
        session_id = f"session_{len(memory.sessions) + 1}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        session = LearningSession(
            session_id=session_id,
            framework=framework,
            start_time=datetime.now().isoformat(),
            level_start=memory.current_level
        )
        memory.sessions.append(session.to_dict())
        self._save(framework)
        return session_id
    
    def end_session(self, framework: str, session_id: str, stats: Dict):
        """End a learning session."""
        memory = self.get_or_create(framework)
        for session in memory.sessions:
            if session["session_id"] == session_id:
                session["end_time"] = datetime.now().isoformat()
                session["questions_answered"] = stats.get("questions", 0)
                session["average_score"] = stats.get("average", 0)
                session["level_end"] = memory.current_level
                session["breaks_taken"] = stats.get("breaks", 0)
                break
        self._save(framework)
    
    def get_summary(self, framework: str) -> Dict:
        """Get a summary of framework's learning progress."""
        memory = self.get_or_create(framework)
        
        # Find strongest and weakest topics
        if memory.concepts:
            sorted_concepts = sorted(
                memory.concepts.items(),
                key=lambda x: x[1].get("best_score", 0),
                reverse=True
            )
            memory.strongest_topics = [c[0] for c in sorted_concepts[:3]]
            memory.weakest_topics = [c[0] for c in sorted_concepts[-3:] if c[1].get("best_score", 0) < 70]
        
        return {
            "framework": framework,
            "current_level": memory.current_level,
            "total_questions": memory.total_questions,
            "average_score": memory.average_score,
            "improvement_rate": memory.improvement_rate,
            "best_streak": memory.best_streak,
            "milestones": memory.milestones,
            "strongest_topics": memory.strongest_topics,
            "weakest_topics": memory.weakest_topics,
            "sessions_completed": len([s for s in memory.sessions if s.get("end_time")]),
            "last_session": memory.sessions[-1] if memory.sessions else None
        }
    
    def get_recommendations(self, framework: str) -> List[str]:
        """Get personalized learning recommendations."""
        memory = self.get_or_create(framework)
        recommendations = []
        
        # Based on improvement rate
        if memory.improvement_rate < 0:
            recommendations.append("Consider reviewing earlier material to strengthen foundations")
        elif memory.improvement_rate > 10:
            recommendations.append("Great progress! You might be ready for more challenging material")
        
        # Based on weak topics
        if memory.weakest_topics:
            recommendations.append(f"Focus on: {', '.join(memory.weakest_topics[:2])}")
        
        # Based on streak
        if memory.current_streak >= 3:
            recommendations.append("You're on a roll! Keep the momentum going!")
        elif memory.current_streak == 0 and memory.total_questions > 5:
            recommendations.append("Take your time with each problem. Quality over speed!")
        
        # Based on average
        if memory.average_score < 50 and memory.total_questions > 10:
            recommendations.append("Consider more worked examples before attempting problems")
        elif memory.average_score >= 80:
            recommendations.append("Excellent understanding! Try some challenge problems")
        
        return recommendations if recommendations else ["Keep up the great work!"]


# Singleton
_memory_store = None

def get_memory_store() -> LearningMemoryStore:
    """Get the singleton memory store."""
    global _memory_store
    if _memory_store is None:
        _memory_store = LearningMemoryStore()
    return _memory_store
