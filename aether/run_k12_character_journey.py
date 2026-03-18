#!/usr/bin/env python3.11
"""
AETHER K-12 Journey with Character Development

Complete educational journey with:
- Increasing proficiency requirements within each grade
- Character and discipline development
- Solid foundation in early years
- Progressive difficulty for research readiness
"""

import sys
import os
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple

sys.path.append('/home/ubuntu/aether/core')

from k12_curriculum import (
    K12_CURRICULUM, EDUCATION_ORDER, get_next_level, 
    get_graduation_milestones, get_level_index
)
from character_development import (
    CharacterDevelopmentTracker, DisciplineExercise,
    calculate_grade_requirements, CHARACTER_TRAITS,
    PROFICIENCY_PHASES
)
from fun_breaks import get_break_manager, get_motivation

# Try to import OpenAI
try:
    from openai import OpenAI
    client = OpenAI()
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False
    client = None


class CharacterAwareStudent:
    """A student with character development tracking."""
    
    def __init__(self, name: str, storage_dir: str = "/home/ubuntu/aether/memory"):
        self.name = name
        self.storage_dir = storage_dir
        self.storage_path = os.path.join(storage_dir, f"{name.lower()}_full_record.json")
        
        # Academic record
        self.current_level = "K"
        self.current_phase = "entry"  # entry, developing, proficient, mastery
        self.enrolled_date = datetime.now().isoformat()
        self.level_history: Dict[str, Dict] = {}
        
        # Progress tracking
        self.total_questions = 0
        self.total_quizzes = 0
        self.group_projects = 0
        
        # Current level progress
        self.level_questions = 0
        self.level_scores: List[float] = []
        self.level_quizzes = 0
        self.phase_questions = 0
        self.phase_scores: List[float] = []
        
        # Graduations
        self.graduations: List[str] = []
        
        # Character tracker
        self.character = CharacterDevelopmentTracker(name, storage_dir)
        
        os.makedirs(storage_dir, exist_ok=True)
        self._load()
    
    def _load(self):
        """Load student record."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.current_level = data.get("current_level", "K")
                    self.current_phase = data.get("current_phase", "entry")
                    self.enrolled_date = data.get("enrolled_date", self.enrolled_date)
                    self.level_history = data.get("level_history", {})
                    self.total_questions = data.get("total_questions", 0)
                    self.total_quizzes = data.get("total_quizzes", 0)
                    self.group_projects = data.get("group_projects", 0)
                    self.level_questions = data.get("level_questions", 0)
                    self.level_scores = data.get("level_scores", [])
                    self.level_quizzes = data.get("level_quizzes", 0)
                    self.phase_questions = data.get("phase_questions", 0)
                    self.phase_scores = data.get("phase_scores", [])
                    self.graduations = data.get("graduations", [])
            except:
                pass
    
    def save(self):
        """Save student record."""
        data = {
            "name": self.name,
            "current_level": self.current_level,
            "current_phase": self.current_phase,
            "enrolled_date": self.enrolled_date,
            "level_history": self.level_history,
            "total_questions": self.total_questions,
            "total_quizzes": self.total_quizzes,
            "group_projects": self.group_projects,
            "level_questions": self.level_questions,
            "level_scores": self.level_scores,
            "level_quizzes": self.level_quizzes,
            "phase_questions": self.phase_questions,
            "phase_scores": self.phase_scores,
            "graduations": self.graduations,
            "last_updated": datetime.now().isoformat()
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @property
    def level_average(self) -> float:
        if not self.level_scores:
            return 0
        return sum(self.level_scores) / len(self.level_scores)
    
    @property
    def phase_average(self) -> float:
        if not self.phase_scores:
            return 0
        return sum(self.phase_scores) / len(self.phase_scores)
    
    @property
    def recent_average(self) -> float:
        if len(self.level_scores) < 10:
            return self.level_average
        return sum(self.level_scores[-10:]) / 10
    
    def get_current_requirements(self) -> Dict:
        """Get current phase requirements."""
        grade_idx = get_level_index(self.current_level)
        reqs = calculate_grade_requirements(self.current_level, grade_idx)
        
        phase_thresholds = {
            "entry": reqs.entry_threshold,
            "developing": reqs.developing_threshold,
            "proficient": reqs.proficient_threshold,
            "mastery": reqs.mastery_threshold
        }
        
        phase_questions = {
            "entry": reqs.min_questions_entry,
            "developing": reqs.min_questions_developing,
            "proficient": reqs.min_questions_proficient,
            "mastery": reqs.min_questions_mastery
        }
        
        return {
            "phase": self.current_phase,
            "threshold": phase_thresholds[self.current_phase],
            "min_questions": phase_questions[self.current_phase],
            "primary_traits": reqs.primary_traits,
            "secondary_traits": reqs.secondary_traits
        }
    
    def can_advance_phase(self) -> Tuple[bool, str]:
        """Check if ready to advance to next phase."""
        reqs = self.get_current_requirements()
        
        # Need minimum questions
        if self.phase_questions < reqs["min_questions"]:
            return (False, f"Need {reqs['min_questions'] - self.phase_questions} more questions")
        
        # Need to meet threshold
        if self.phase_average < reqs["threshold"]:
            return (False, f"Need {reqs['threshold']:.0f}% avg (currently {self.phase_average:.0f}%)")
        
        # Check character for phase advancement
        grade_idx = get_level_index(self.current_level)
        char_ready, char_msg = self.character.is_ready_for_graduation(self.current_level, grade_idx)
        
        # For early phases, character is less strict
        if self.current_phase in ["entry", "developing"]:
            return (True, "Ready to advance phase")
        
        # For proficient and mastery, character matters more
        if not char_ready and self.current_phase == "mastery":
            return (False, char_msg)
        
        return (True, "Ready to advance phase")
    
    def advance_phase(self) -> Optional[str]:
        """Advance to next phase or graduate level."""
        can_advance, msg = self.can_advance_phase()
        if not can_advance:
            return None
        
        phase_order = ["entry", "developing", "proficient", "mastery"]
        current_idx = phase_order.index(self.current_phase)
        
        if current_idx < len(phase_order) - 1:
            # Advance to next phase
            self.current_phase = phase_order[current_idx + 1]
            self.phase_questions = 0
            self.phase_scores = []
            self.save()
            return self.current_phase
        else:
            # At mastery - check if can graduate level
            return self._graduate_level()
    
    def _graduate_level(self) -> Optional[str]:
        """Graduate from current level to next."""
        grade_idx = get_level_index(self.current_level)
        
        # Final character check
        char_ready, char_msg = self.character.is_ready_for_graduation(self.current_level, grade_idx)
        if not char_ready:
            return None
        
        # Save level history
        self.level_history[self.current_level] = {
            "questions": self.level_questions,
            "average": self.level_average,
            "quizzes": self.level_quizzes,
            "character_at_graduation": self.character.get_character_summary(),
            "completed": datetime.now().isoformat()
        }
        
        # Check for graduation milestone
        milestones = get_graduation_milestones()
        if self.current_level in milestones:
            self.graduations.append(milestones[self.current_level])
        
        # Advance to next level
        next_level = get_next_level(self.current_level)
        if next_level:
            self.current_level = next_level
            self.current_phase = "entry"
            self.level_questions = 0
            self.level_scores = []
            self.level_quizzes = 0
            self.phase_questions = 0
            self.phase_scores = []
            self.save()
            return next_level
        
        return None
    
    def record_score(self, score: float, completed: bool = True, 
                     was_difficult: bool = False, on_topic: bool = True):
        """Record a score and update character."""
        self.level_scores.append(score)
        self.phase_scores.append(score)
        self.level_questions += 1
        self.phase_questions += 1
        self.total_questions += 1
        
        # Update character
        self.character.record_quiz_behavior(
            completed=completed,
            score=score,
            was_difficult=was_difficult,
            on_topic=on_topic
        )
        
        self.save()


def quick_answer(question: str, student_name: str, level: str, phase: str) -> str:
    """Get answer from AI with phase-appropriate context."""
    if not AI_AVAILABLE:
        return f"[{student_name}] Answer for {level} ({phase}): {question[:30]}..."
    
    try:
        curriculum = K12_CURRICULUM.get(level)
        phase_context = {
            "entry": "You are just starting to learn this material. Give your best attempt.",
            "developing": "You are building your understanding. Show your reasoning.",
            "proficient": "You have solid knowledge. Demonstrate clear understanding.",
            "mastery": "You are mastering this material. Show deep comprehension."
        }
        
        context = f"You are {student_name}, a {curriculum.name} student ({curriculum.real_world_age}). {phase_context.get(phase, '')} Answer clearly."
        
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": question}
            ],
            max_tokens=400,
            temperature=0.6
        )
        return response.choices[0].message.content
    except:
        return f"[{student_name}] Attempting: {question[:30]}..."


def quick_grade(question: str, answer: str, difficulty: str, 
                level: str, phase: str, reqs: Dict) -> int:
    """Grade with phase-appropriate expectations."""
    if not AI_AVAILABLE:
        # Base score varies by phase
        phase_base = {"entry": 60, "developing": 65, "proficient": 70, "mastery": 75}
        diff_mod = {"easy": 15, "medium": 5, "hard": -5}
        base = phase_base.get(phase, 65) + diff_mod.get(difficulty, 0)
        return base + random.randint(-10, 15)
    
    try:
        threshold = reqs.get("threshold", 70)
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": f"Grade this {level} level {difficulty} question 0-100. Phase: {phase} (threshold: {threshold}%). Be fair but rigorous. Minimum 30."},
                {"role": "user", "content": f"Q: {question[:300]}\nA: {answer[:300]}\nScore (number only):"}
            ],
            max_tokens=10,
            temperature=0.3
        )
        import re
        text = response.choices[0].message.content.strip()
        match = re.search(r'\d+', text)
        return max(30, min(100, int(match.group()))) if match else 60
    except:
        phase_base = {"entry": 60, "developing": 65, "proficient": 70, "mastery": 75}
        return phase_base.get(phase, 65) + random.randint(-5, 15)


def generate_phase_quiz(student: CharacterAwareStudent, num_questions: int) -> List[Dict]:
    """Generate quiz appropriate for current phase."""
    curriculum = K12_CURRICULUM.get(student.current_level)
    if not curriculum:
        return []
    
    questions = []
    
    # Difficulty distribution based on phase
    phase_difficulty = {
        "entry": {"easy": 0.6, "medium": 0.3, "hard": 0.1},
        "developing": {"easy": 0.4, "medium": 0.4, "hard": 0.2},
        "proficient": {"easy": 0.2, "medium": 0.5, "hard": 0.3},
        "mastery": {"easy": 0.1, "medium": 0.4, "hard": 0.5}
    }
    
    dist = phase_difficulty.get(student.current_phase, phase_difficulty["developing"])
    
    for i in range(num_questions):
        # Select difficulty based on distribution
        r = random.random()
        if r < dist["easy"]:
            difficulty = "easy"
        elif r < dist["easy"] + dist["medium"]:
            difficulty = "medium"
        else:
            difficulty = "hard"
        
        concept = random.choice(curriculum.core_concepts)
        subject = random.choice(curriculum.subjects)
        
        questions.append({
            "id": f"{student.current_level}_{student.current_phase}_Q{i+1}",
            "subject": subject,
            "concept": concept,
            "difficulty": difficulty,
            "question": create_phase_question(concept, subject, difficulty, student.current_phase)
        })
    
    return questions


def create_phase_question(concept: str, subject: str, difficulty: str, phase: str) -> str:
    """Create question appropriate for phase."""
    templates = {
        "entry": {
            "easy": [
                f"What is {concept}? Give a simple explanation.",
                f"Give one example of {concept}.",
            ],
            "medium": [
                f"Explain {concept} and why it's useful.",
                f"How would you use {concept} in {subject}?",
            ],
            "hard": [
                f"Compare {concept} to something you already know.",
                f"What questions do you have about {concept}?",
            ]
        },
        "developing": {
            "easy": [
                f"Explain {concept} in your own words.",
                f"List the key parts of {concept}.",
            ],
            "medium": [
                f"Solve a basic problem using {concept}.",
                f"How does {concept} connect to {subject}?",
            ],
            "hard": [
                f"What are common mistakes when working with {concept}?",
                f"Create your own example involving {concept}.",
            ]
        },
        "proficient": {
            "easy": [
                f"Demonstrate your understanding of {concept} with an example.",
            ],
            "medium": [
                f"Apply {concept} to solve this problem and explain your steps.",
                f"How would you teach {concept} to someone new to {subject}?",
            ],
            "hard": [
                f"Analyze a complex situation involving {concept}.",
                f"What are the limitations of {concept}?",
            ]
        },
        "mastery": {
            "easy": [
                f"Give a comprehensive explanation of {concept}.",
            ],
            "medium": [
                f"Solve a challenging problem using {concept} and justify each step.",
                f"How does {concept} prepare you for more advanced topics?",
            ],
            "hard": [
                f"Create and solve an original problem involving {concept}.",
                f"Explain the deeper significance of {concept} in {subject}.",
                f"How would you extend {concept} to a new situation?",
            ]
        }
    }
    
    phase_templates = templates.get(phase, templates["developing"])
    diff_templates = phase_templates.get(difficulty, phase_templates["medium"])
    return random.choice(diff_templates)


def print_status(student: CharacterAwareStudent):
    """Print student status."""
    curriculum = K12_CURRICULUM.get(student.current_level)
    reqs = student.get_current_requirements()
    char_summary = student.character.get_character_summary()
    
    phase_emoji = {"entry": "🌱", "developing": "📈", "proficient": "⭐", "mastery": "🏆"}
    
    print(f"\n  {student.name} Status:")
    print(f"     Level: {curriculum.name} ({student.current_level})")
    print(f"     Phase: {phase_emoji.get(student.current_phase, '📚')} {student.current_phase.title()}")
    print(f"     Threshold: {reqs['threshold']:.0f}% | Current: {student.phase_average:.0f}%")
    print(f"     Questions: {student.phase_questions}/{reqs['min_questions']}")
    print(f"     Character: {char_summary['overall_score']:.0f}/100")
    print(f"     Discipline: {char_summary['discipline_score']:.0f}/100")


def run_character_journey(students: List[str] = None, max_sessions: int = 25):
    """
    Run K-12 journey with character development.
    """
    
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*5 + "AETHER K-12 WITH CHARACTER DEVELOPMENT" + " "*10 + "║")
    print("║" + " "*3 + "Building Discipline • Increasing Requirements" + " "*6 + "║")
    print("╚" + "="*58 + "╝")
    
    if students is None:
        students = ["Stratify", "Principia"]
    
    # Initialize
    k12_students = {name: CharacterAwareStudent(name) for name in students}
    break_manager = get_break_manager()
    
    # Show initial status
    print("\n📚 Initial Status:")
    for name, student in k12_students.items():
        print_status(student)
    
    # Main learning loop
    for session in range(1, max_sessions + 1):
        print(f"\n{'─'*60}")
        print(f"  SESSION {session}/{max_sessions}")
        print(f"{'─'*60}")
        
        for name, student in k12_students.items():
            curriculum = K12_CURRICULUM.get(student.current_level)
            reqs = student.get_current_requirements()
            
            # Check if at research level
            if student.current_level == "RES":
                print(f"\n  🚀 {name} is at Research Level!")
                continue
            
            # Determine quiz length (10-50 based on phase and performance)
            base_length = 10
            if student.phase_average >= 80:
                base_length = 20
            elif student.phase_average >= 70:
                base_length = 15
            
            # Add variation
            quiz_length = base_length + random.randint(-3, 7)
            quiz_length = max(10, min(50, quiz_length))
            
            # Generate quiz
            questions = generate_phase_quiz(student, quiz_length)
            
            print(f"\n  📝 {name}'s Quiz ({quiz_length} questions)")
            print(f"     {curriculum.name} | Phase: {student.current_phase.title()}")
            print(f"     Target: {reqs['threshold']:.0f}% | Current: {student.phase_average:.0f}%")
            
            # Character exercise if needed
            char_summary = student.character.get_character_summary()
            if char_summary['overall_score'] < 55:
                trait, exercise = DisciplineExercise.get_exercise_for_weak_trait(student.character)
                print(f"     📋 Character Exercise: {exercise['name']}")
                print(f"        (Building {trait})")
            
            # Take quiz
            quiz_scores = []
            for i, q in enumerate(questions):
                answer = quick_answer(q["question"], name, student.current_level, student.current_phase)
                score = quick_grade(q["question"], answer, q["difficulty"], 
                                   student.current_level, student.current_phase, reqs)
                quiz_scores.append(score)
                
                # Record with character tracking
                was_difficult = q["difficulty"] == "hard" or score < 60
                student.record_score(score, completed=True, was_difficult=was_difficult)
                
                # Progress every 5 questions
                if (i + 1) % 5 == 0 or i == len(questions) - 1:
                    avg = sum(quiz_scores) / len(quiz_scores)
                    bar_len = int(30 * (i + 1) / len(questions))
                    bar = "█" * bar_len + "░" * (30 - bar_len)
                    
                    # Emoji based on meeting threshold
                    if avg >= reqs['threshold']:
                        emoji = "🌟"
                    elif avg >= reqs['threshold'] - 10:
                        emoji = "📈"
                    else:
                        emoji = "🌱"
                    
                    print(f"     [{bar}] {i+1}/{quiz_length} {emoji} {avg:.0f}%")
            
            # Quiz complete
            student.level_quizzes += 1
            student.total_quizzes += 1
            quiz_avg = sum(quiz_scores) / len(quiz_scores)
            
            print(f"\n     Quiz: {quiz_avg:.0f}% | Phase avg: {student.phase_average:.0f}%")
            
            # Check for phase advancement
            can_advance, msg = student.can_advance_phase()
            if can_advance:
                result = student.advance_phase()
                if result:
                    if result in EDUCATION_ORDER:
                        # Graduated to new level
                        new_curriculum = K12_CURRICULUM.get(result)
                        print(f"\n     🎓 GRADUATED to {new_curriculum.name}!")
                        
                        # Check milestone
                        milestones = get_graduation_milestones()
                        prev_level = EDUCATION_ORDER[EDUCATION_ORDER.index(result) - 1]
                        if prev_level in milestones:
                            print(f"     🎉 MILESTONE: {milestones[prev_level]}!")
                    else:
                        # Advanced phase
                        print(f"\n     ⬆️ Advanced to {result.title()} phase!")
            else:
                print(f"     📊 {msg}")
            
            # Character update
            char_summary = student.character.get_character_summary()
            top_trait = char_summary['top_traits'][0] if char_summary['top_traits'] else ("none", 0)
            print(f"     💪 Character: {char_summary['overall_score']:.0f} | Top: {top_trait[0]} ({top_trait[1]:.0f})")
            
            # Break if needed
            if break_manager.should_take_break(student.phase_questions, quiz_scores):
                break_info = break_manager.take_break(name)
                print(f"     🎮 Break: {break_info['activity']['name']}")
            
            student.save()
        
        # Session summary
        print(f"\n  📊 Session Summary:")
        for name, student in k12_students.items():
            curriculum = K12_CURRICULUM.get(student.current_level)
            level_idx = get_level_index(student.current_level)
            progress = (level_idx / len(EDUCATION_ORDER)) * 100
            print(f"     {name}: {curriculum.name} ({student.current_phase}) - {progress:.0f}% to Yang-Mills")
        
        # Motivation
        if session % 4 == 0:
            print(f"\n  💫 {get_motivation()}")
    
    # Final report
    print("\n" + "="*60)
    print("  JOURNEY PROGRESS REPORT")
    print("="*60)
    
    for name, student in k12_students.items():
        curriculum = K12_CURRICULUM.get(student.current_level)
        char_summary = student.character.get_character_summary()
        
        print(f"\n  📜 {name}'s Record:")
        print(f"     Level: {curriculum.name} | Phase: {student.current_phase.title()}")
        print(f"     Total Questions: {student.total_questions}")
        print(f"     Graduations: {', '.join(student.graduations) if student.graduations else 'None yet'}")
        
        print(f"\n     Character Development:")
        print(f"       Overall: {char_summary['overall_score']:.0f}/100")
        print(f"       Discipline: {char_summary['discipline_score']:.0f}/100")
        print(f"       Completion Rate: {char_summary['completion_rate']*100:.0f}%")
        
        print(f"       Top Traits:")
        for trait, score in char_summary['top_traits']:
            print(f"         • {trait.replace('_', ' ').title()}: {score:.0f}")
        
        if char_summary['weak_traits']:
            print(f"       Areas to Develop:")
            for trait in char_summary['weak_traits'][:2]:
                print(f"         • {trait.replace('_', ' ').title()}")
        
        # Progress bar
        level_idx = get_level_index(student.current_level)
        progress = (level_idx / len(EDUCATION_ORDER)) * 100
        bar_len = int(40 * level_idx / len(EDUCATION_ORDER))
        bar = "█" * bar_len + "░" * (40 - bar_len)
        print(f"\n     Progress: [{bar}] {progress:.0f}%")
    
    return k12_students


if __name__ == "__main__":
    run_character_journey(max_sessions=20)
