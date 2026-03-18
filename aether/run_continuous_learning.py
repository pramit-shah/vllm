#!/usr/bin/env python3.11
"""
AETHER Continuous Learning System

- Runs sessions in batches
- Stores progress after each batch
- Resumes from stored progress
- Keeps updating the same files
"""

import sys
import os
import json
import random
import time
from datetime import datetime

sys.path.append('/home/ubuntu/aether/core')

from k12_curriculum import K12_CURRICULUM, EDUCATION_ORDER, get_next_level, get_level_index
from character_development import (
    CharacterDevelopmentTracker, DisciplineExercise,
    calculate_grade_requirements
)
from fun_breaks import get_break_manager, get_motivation
from group_projects import GroupProjectManager

# Import OpenAI
try:
    from openai import OpenAI
    client = OpenAI()
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False
    client = None

MEMORY_DIR = "/home/ubuntu/aether/memory"
PROGRESS_LOG = "/home/ubuntu/aether/logs/continuous_progress.jsonl"


class PersistentStudent:
    """Student with full persistence - loads and saves automatically."""
    
    def __init__(self, name: str):
        self.name = name
        self.storage_path = os.path.join(MEMORY_DIR, f"{name.lower()}_full_record.json")
        
        # Academic record
        self.current_level = "K"
        self.current_phase = "entry"
        self.enrolled_date = datetime.now().isoformat()
        self.level_history = {}
        
        # Progress
        self.total_questions = 0
        self.total_quizzes = 0
        self.total_sessions = 0
        self.group_projects = 0
        
        # Current level
        self.level_questions = 0
        self.level_scores = []
        self.level_quizzes = 0
        self.phase_questions = 0
        self.phase_scores = []
        
        # Graduations
        self.graduations = []
        
        # Character
        self.character = CharacterDevelopmentTracker(name, MEMORY_DIR)
        
        os.makedirs(MEMORY_DIR, exist_ok=True)
        self._load()
    
    def _load(self):
        """Load from disk."""
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
                    self.total_sessions = data.get("total_sessions", 0)
                    self.group_projects = data.get("group_projects", 0)
                    self.level_questions = data.get("level_questions", 0)
                    self.level_scores = data.get("level_scores", [])
                    self.level_quizzes = data.get("level_quizzes", 0)
                    self.phase_questions = data.get("phase_questions", 0)
                    self.phase_scores = data.get("phase_scores", [])
                    self.graduations = data.get("graduations", [])
                    print(f"  📂 Loaded {self.name}: {self.current_level} ({self.current_phase}), {self.total_questions} questions")
            except Exception as e:
                print(f"  ⚠️ Could not load {self.name}: {e}")
    
    def save(self):
        """Save to disk."""
        data = {
            "name": self.name,
            "current_level": self.current_level,
            "current_phase": self.current_phase,
            "enrolled_date": self.enrolled_date,
            "level_history": self.level_history,
            "total_questions": self.total_questions,
            "total_quizzes": self.total_quizzes,
            "total_sessions": self.total_sessions,
            "group_projects": self.group_projects,
            "level_questions": self.level_questions,
            "level_scores": self.level_scores[-100:],  # Keep last 100
            "level_quizzes": self.level_quizzes,
            "phase_questions": self.phase_questions,
            "phase_scores": self.phase_scores[-50:],  # Keep last 50
            "graduations": self.graduations,
            "last_updated": datetime.now().isoformat()
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
        self.character.save()
    
    @property
    def phase_average(self) -> float:
        if not self.phase_scores:
            return 0
        return sum(self.phase_scores) / len(self.phase_scores)
    
    @property
    def level_average(self) -> float:
        if not self.level_scores:
            return 0
        return sum(self.level_scores) / len(self.level_scores)
    
    def get_requirements(self):
        """Get current phase requirements."""
        grade_idx = get_level_index(self.current_level)
        reqs = calculate_grade_requirements(self.current_level, grade_idx)
        
        thresholds = {
            "entry": reqs.entry_threshold,
            "developing": reqs.developing_threshold,
            "proficient": reqs.proficient_threshold,
            "mastery": reqs.mastery_threshold
        }
        
        min_questions = {
            "entry": reqs.min_questions_entry,
            "developing": reqs.min_questions_developing,
            "proficient": reqs.min_questions_proficient,
            "mastery": reqs.min_questions_mastery
        }
        
        return {
            "threshold": thresholds[self.current_phase],
            "min_questions": min_questions[self.current_phase],
            "primary_traits": reqs.primary_traits
        }
    
    def record_score(self, score: float, was_difficult: bool = False):
        """Record a score."""
        self.level_scores.append(score)
        self.phase_scores.append(score)
        self.level_questions += 1
        self.phase_questions += 1
        self.total_questions += 1
        
        self.character.record_quiz_behavior(
            completed=True,
            score=score,
            was_difficult=was_difficult,
            on_topic=True
        )
    
    def try_advance(self) -> str:
        """Try to advance phase or graduate level."""
        reqs = self.get_requirements()
        
        # Check requirements
        if self.phase_questions < reqs["min_questions"]:
            return None
        if self.phase_average < reqs["threshold"]:
            return None
        
        # Advance phase
        phases = ["entry", "developing", "proficient", "mastery"]
        idx = phases.index(self.current_phase)
        
        if idx < 3:
            self.current_phase = phases[idx + 1]
            self.phase_questions = 0
            self.phase_scores = []
            self.save()
            return f"phase:{self.current_phase}"
        else:
            # Graduate level
            return self._graduate()
    
    def _graduate(self) -> str:
        """Graduate to next level."""
        # Save history
        self.level_history[self.current_level] = {
            "questions": self.level_questions,
            "average": self.level_average,
            "completed": datetime.now().isoformat()
        }
        
        # Get next level
        next_level = get_next_level(self.current_level)
        if next_level:
            old_level = self.current_level
            self.current_level = next_level
            self.current_phase = "entry"
            self.level_questions = 0
            self.level_scores = []
            self.level_quizzes = 0
            self.phase_questions = 0
            self.phase_scores = []
            self.graduations.append(old_level)
            self.save()
            return f"level:{next_level}"
        
        return None


def quick_answer(question: str, student: PersistentStudent) -> str:
    """Get AI answer."""
    if not AI_AVAILABLE:
        return f"Answer for {question[:30]}..."
    
    try:
        curriculum = K12_CURRICULUM.get(student.current_level)
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": f"You are {student.name}, a {curriculum.name} student. Answer clearly and concisely."},
                {"role": "user", "content": question}
            ],
            max_tokens=300,
            temperature=0.6
        )
        return response.choices[0].message.content
    except:
        return f"Attempting: {question[:30]}..."


def quick_grade(question: str, answer: str, difficulty: str, student: PersistentStudent) -> int:
    """Grade answer."""
    if not AI_AVAILABLE:
        base = {"easy": 75, "medium": 65, "hard": 55}
        return base.get(difficulty, 65) + random.randint(-10, 15)
    
    try:
        reqs = student.get_requirements()
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": f"Grade this {student.current_level} level answer 0-100. Be fair. Minimum 30."},
                {"role": "user", "content": f"Q: {question[:200]}\nA: {answer[:200]}\nScore:"}
            ],
            max_tokens=10,
            temperature=0.3
        )
        import re
        text = response.choices[0].message.content.strip()
        match = re.search(r'\d+', text)
        return max(30, min(100, int(match.group()))) if match else 60
    except:
        return 60 + random.randint(-10, 15)


def generate_question(student: PersistentStudent) -> dict:
    """Generate a question for the student."""
    curriculum = K12_CURRICULUM.get(student.current_level)
    
    # Difficulty based on phase
    phase_diff = {
        "entry": ["easy", "easy", "medium"],
        "developing": ["easy", "medium", "medium"],
        "proficient": ["medium", "medium", "hard"],
        "mastery": ["medium", "hard", "hard"]
    }
    difficulty = random.choice(phase_diff.get(student.current_phase, ["medium"]))
    
    concept = random.choice(curriculum.core_concepts)
    subject = random.choice(curriculum.subjects)
    
    templates = {
        "easy": f"Explain {concept} simply.",
        "medium": f"How does {concept} relate to {subject}? Give an example.",
        "hard": f"Apply {concept} to solve a problem in {subject}. Show your reasoning."
    }
    
    return {
        "question": templates[difficulty],
        "difficulty": difficulty,
        "concept": concept,
        "subject": subject
    }


def log_progress(students: dict, session: int, batch: int):
    """Log progress to file."""
    os.makedirs(os.path.dirname(PROGRESS_LOG), exist_ok=True)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "batch": batch,
        "session": session,
        "students": {}
    }
    
    for name, student in students.items():
        curriculum = K12_CURRICULUM.get(student.current_level)
        char_summary = student.character.get_character_summary()
        
        entry["students"][name] = {
            "level": student.current_level,
            "level_name": curriculum.name,
            "phase": student.current_phase,
            "total_questions": student.total_questions,
            "phase_avg": student.phase_average,
            "character": char_summary["overall_score"],
            "discipline": char_summary["discipline_score"],
            "graduations": student.graduations
        }
    
    with open(PROGRESS_LOG, 'a') as f:
        f.write(json.dumps(entry) + "\n")


def run_batch(students: dict, sessions: int, batch_num: int, project_manager: GroupProjectManager):
    """Run a batch of sessions."""
    
    break_manager = get_break_manager()
    
    for session in range(1, sessions + 1):
        global_session = (batch_num - 1) * sessions + session
        
        print(f"\n{'─'*60}")
        print(f"  BATCH {batch_num} | SESSION {session}/{sessions} (Global: {global_session})")
        print(f"{'─'*60}")
        
        for name, student in students.items():
            curriculum = K12_CURRICULUM.get(student.current_level)
            reqs = student.get_requirements()
            
            if student.current_level == "RES":
                print(f"\n  🚀 {name} at Research Level!")
                continue
            
            # Quiz length
            base = 10 if student.phase_average < 70 else 15
            quiz_len = base + random.randint(0, 10)
            
            print(f"\n  📝 {name}: {curriculum.name} ({student.current_phase})")
            print(f"     Target: {reqs['threshold']:.0f}% | Current: {student.phase_average:.0f}%")
            
            # Take quiz
            scores = []
            for i in range(quiz_len):
                q = generate_question(student)
                answer = quick_answer(q["question"], student)
                score = quick_grade(q["question"], answer, q["difficulty"], student)
                scores.append(score)
                student.record_score(score, was_difficult=(q["difficulty"] == "hard"))
                
                if (i + 1) % 5 == 0 or i == quiz_len - 1:
                    avg = sum(scores) / len(scores)
                    bar = "█" * int(30 * (i+1) / quiz_len) + "░" * (30 - int(30 * (i+1) / quiz_len))
                    emoji = "🌟" if avg >= reqs["threshold"] else "📈"
                    print(f"     [{bar}] {i+1}/{quiz_len} {emoji} {avg:.0f}%")
            
            student.level_quizzes += 1
            student.total_quizzes += 1
            student.total_sessions = global_session
            
            # Try to advance
            result = student.try_advance()
            if result:
                if result.startswith("level:"):
                    new_level = result.split(":")[1]
                    new_curriculum = K12_CURRICULUM.get(new_level)
                    print(f"     🎓 GRADUATED to {new_curriculum.name}!")
                else:
                    new_phase = result.split(":")[1]
                    print(f"     ⬆️ Advanced to {new_phase.title()}!")
            
            # Character
            char = student.character.get_character_summary()
            print(f"     💪 Character: {char['overall_score']:.0f} | Discipline: {char['discipline_score']:.0f}")
            
            # Break
            if break_manager.should_take_break(student.phase_questions, scores):
                brk = break_manager.take_break(name)
                print(f"     🎮 Break: {brk['activity']['name']}")
            
            student.save()
        
        # Check for group project
        if project_manager.should_trigger_project(global_session):
            print(f"\n  🤝 GROUP PROJECT TIME!")
            project = project_manager.assign_project(list(students.keys()), global_session)
            if project:
                print(f"     Project: {project['name']}")
                print(f"     Theme: {project['theme']}")
                for name in students:
                    students[name].group_projects += 1
                    students[name].save()
        
        # Log progress
        log_progress(students, global_session, batch_num)
        
        # Session summary
        print(f"\n  📊 Progress:")
        for name, student in students.items():
            curriculum = K12_CURRICULUM.get(student.current_level)
            progress = (get_level_index(student.current_level) / len(EDUCATION_ORDER)) * 100
            print(f"     {name}: {curriculum.name} ({student.current_phase}) - {progress:.0f}% to Yang-Mills")
    
    # Batch complete - save all
    print(f"\n  💾 Batch {batch_num} complete - Progress saved!")
    for student in students.values():
        student.save()


def run_continuous(batches: int = 3, sessions_per_batch: int = 5):
    """Run continuous learning with progress persistence."""
    
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*8 + "AETHER CONTINUOUS LEARNING" + " "*16 + "║")
    print("║" + " "*5 + "Progress Saved • Resumes Automatically" + " "*8 + "║")
    print("╚" + "="*58 + "╝")
    
    # Load or create students
    print("\n📚 Loading Students...")
    students = {
        "Stratify": PersistentStudent("Stratify"),
        "Principia": PersistentStudent("Principia")
    }
    
    # Initialize project manager
    project_manager = GroupProjectManager(MEMORY_DIR)
    
    # Show current status
    print("\n📊 Current Status:")
    for name, student in students.items():
        curriculum = K12_CURRICULUM.get(student.current_level)
        char = student.character.get_character_summary()
        print(f"  {name}:")
        print(f"    Level: {curriculum.name} ({student.current_phase})")
        print(f"    Questions: {student.total_questions} | Quizzes: {student.total_quizzes}")
        print(f"    Character: {char['overall_score']:.0f} | Discipline: {char['discipline_score']:.0f}")
        print(f"    Graduations: {', '.join(student.graduations) if student.graduations else 'None yet'}")
    
    # Run batches
    for batch in range(1, batches + 1):
        print(f"\n{'='*60}")
        print(f"  STARTING BATCH {batch}/{batches}")
        print(f"{'='*60}")
        
        run_batch(students, sessions_per_batch, batch, project_manager)
        
        # Motivation between batches
        if batch < batches:
            print(f"\n  💫 {get_motivation()}")
            print(f"  ⏳ Continuing to next batch...")
    
    # Final report
    print("\n" + "="*60)
    print("  CONTINUOUS LEARNING REPORT")
    print("="*60)
    
    for name, student in students.items():
        curriculum = K12_CURRICULUM.get(student.current_level)
        char = student.character.get_character_summary()
        progress = (get_level_index(student.current_level) / len(EDUCATION_ORDER)) * 100
        
        print(f"\n  📜 {name}:")
        print(f"     Level: {curriculum.name} | Phase: {student.current_phase}")
        print(f"     Total Questions: {student.total_questions}")
        print(f"     Total Quizzes: {student.total_quizzes}")
        print(f"     Group Projects: {student.group_projects}")
        print(f"     Graduations: {', '.join(student.graduations) if student.graduations else 'None'}")
        print(f"     Character: {char['overall_score']:.0f}/100")
        print(f"     Discipline: {char['discipline_score']:.0f}/100")
        
        bar = "█" * int(40 * progress / 100) + "░" * (40 - int(40 * progress / 100))
        print(f"     Progress: [{bar}] {progress:.0f}%")
    
    print(f"\n  📁 Progress saved to: {MEMORY_DIR}")
    print(f"  📊 Log saved to: {PROGRESS_LOG}")
    
    return students


if __name__ == "__main__":
    # Run 3 batches of 5 sessions each = 15 total sessions
    run_continuous(batches=3, sessions_per_batch=5)
