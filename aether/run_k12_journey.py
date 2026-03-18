#!/usr/bin/env python3.11
"""
AETHER K-12 and Higher Education Journey

Complete educational journey following real standards:
- K-12 (Kindergarten through 12th grade)
- Higher Education (Undergraduate + Graduate)
- Research Level (Ready for Yang-Mills)
"""

import sys
import os
import json
import random
from datetime import datetime
from typing import Dict, List, Optional

sys.path.append('/home/ubuntu/aether/core')

from k12_curriculum import (
    K12_CURRICULUM, EDUCATION_ORDER, get_next_level, 
    get_graduation_milestones, get_level_index
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


class K12Student:
    """A student progressing through K-12 and higher education."""
    
    def __init__(self, name: str, storage_dir: str = "/home/ubuntu/aether/memory"):
        self.name = name
        self.storage_dir = storage_dir
        self.storage_path = os.path.join(storage_dir, f"{name.lower()}_k12_record.json")
        
        # Academic record
        self.current_level = "K"
        self.enrolled_date = datetime.now().isoformat()
        self.level_history: Dict[str, Dict] = {}
        self.total_questions = 0
        self.total_quizzes = 0
        self.group_projects = 0
        
        # Current level progress
        self.level_questions = 0
        self.level_scores: List[float] = []
        self.level_quizzes = 0
        
        # Characteristics discovered
        self.characteristics: Dict[str, float] = {}
        self.interests: List[str] = []
        
        # Milestones
        self.graduations: List[str] = []
        
        os.makedirs(storage_dir, exist_ok=True)
        self._load()
    
    def _load(self):
        """Load student record."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.current_level = data.get("current_level", "K")
                    self.enrolled_date = data.get("enrolled_date", self.enrolled_date)
                    self.level_history = data.get("level_history", {})
                    self.total_questions = data.get("total_questions", 0)
                    self.total_quizzes = data.get("total_quizzes", 0)
                    self.group_projects = data.get("group_projects", 0)
                    self.level_questions = data.get("level_questions", 0)
                    self.level_scores = data.get("level_scores", [])
                    self.level_quizzes = data.get("level_quizzes", 0)
                    self.characteristics = data.get("characteristics", {})
                    self.interests = data.get("interests", [])
                    self.graduations = data.get("graduations", [])
            except:
                pass
    
    def save(self):
        """Save student record."""
        data = {
            "name": self.name,
            "current_level": self.current_level,
            "enrolled_date": self.enrolled_date,
            "level_history": self.level_history,
            "total_questions": self.total_questions,
            "total_quizzes": self.total_quizzes,
            "group_projects": self.group_projects,
            "level_questions": self.level_questions,
            "level_scores": self.level_scores,
            "level_quizzes": self.level_quizzes,
            "characteristics": self.characteristics,
            "interests": self.interests,
            "graduations": self.graduations,
            "last_updated": datetime.now().isoformat()
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @property
    def level_average(self) -> float:
        """Average score at current level."""
        if not self.level_scores:
            return 0
        return sum(self.level_scores) / len(self.level_scores)
    
    @property
    def recent_average(self) -> float:
        """Average of last 10 scores."""
        if len(self.level_scores) < 10:
            return self.level_average
        return sum(self.level_scores[-10:]) / 10
    
    def can_advance(self) -> bool:
        """Check if ready to advance to next level."""
        curriculum = K12_CURRICULUM.get(self.current_level)
        if not curriculum:
            return False
        
        if self.level_questions < curriculum.min_questions:
            return False
        if self.level_quizzes < curriculum.min_quizzes:
            return False
        if self.recent_average < curriculum.mastery_threshold:
            return False
        
        return True
    
    def advance(self) -> Optional[str]:
        """Advance to next level."""
        if not self.can_advance():
            return None
        
        # Save current level history
        self.level_history[self.current_level] = {
            "questions": self.level_questions,
            "average": self.level_average,
            "quizzes": self.level_quizzes,
            "completed": datetime.now().isoformat()
        }
        
        # Check for graduation milestone
        milestones = get_graduation_milestones()
        if self.current_level in milestones:
            self.graduations.append(milestones[self.current_level])
        
        # Advance
        next_level = get_next_level(self.current_level)
        if next_level:
            self.current_level = next_level
            self.level_questions = 0
            self.level_scores = []
            self.level_quizzes = 0
            self.save()
            return next_level
        
        return None
    
    def record_score(self, score: float, topic: str = None):
        """Record a quiz score."""
        self.level_scores.append(score)
        self.level_questions += 1
        self.total_questions += 1
        
        # Update characteristics based on topic
        if topic:
            topic_lower = topic.lower()
            char_map = {
                "algebra": "abstract_thinking",
                "geometry": "visual_spatial",
                "proof": "logical_reasoning",
                "calculus": "analytical_thinking",
                "statistics": "data_analysis",
                "number": "computational",
                "pattern": "pattern_recognition"
            }
            for key, char in char_map.items():
                if key in topic_lower:
                    current = self.characteristics.get(char, 50)
                    self.characteristics[char] = current + (score - current) * 0.1
        
        self.save()


class AdaptiveK12Quiz:
    """Generate adaptive quizzes for K-12 curriculum."""
    
    def __init__(self):
        self.min_questions = 10
        self.max_questions = 50
    
    def determine_length(self, student: K12Student) -> int:
        """Determine quiz length based on student state."""
        base = self.min_questions
        
        # Performance factor
        if student.recent_average >= 85:
            base += 20  # Doing great, can handle more
        elif student.recent_average >= 75:
            base += 10
        elif student.recent_average < 60:
            base -= 5   # Struggling, keep it short
        
        # Experience factor
        if student.level_questions > 50:
            base += 10
        elif student.level_questions > 25:
            base += 5
        
        # Random variation
        base += random.randint(-5, 5)
        
        return max(self.min_questions, min(self.max_questions, base))
    
    def generate(self, student: K12Student) -> List[Dict]:
        """Generate a quiz for the student's current level."""
        curriculum = K12_CURRICULUM.get(student.current_level)
        if not curriculum:
            return []
        
        num_questions = self.determine_length(student)
        questions = []
        
        for i in range(num_questions):
            concept = random.choice(curriculum.core_concepts)
            subject = random.choice(curriculum.subjects)
            difficulty = self._get_difficulty(i, num_questions)
            
            questions.append({
                "id": f"{student.current_level}_Q{i+1}",
                "subject": subject,
                "concept": concept,
                "difficulty": difficulty,
                "question": self._create_question(concept, subject, difficulty, curriculum)
            })
        
        return questions
    
    def _get_difficulty(self, idx: int, total: int) -> str:
        """Difficulty increases through quiz."""
        progress = idx / total
        if progress < 0.3:
            return "easy"
        elif progress < 0.7:
            return "medium"
        else:
            return "hard"
    
    def _create_question(self, concept: str, subject: str, difficulty: str, curriculum) -> str:
        """Create a question."""
        templates = {
            "easy": [
                f"Explain what '{concept}' means in simple terms.",
                f"Give an example of {concept}.",
                f"What is the basic idea behind {subject}?"
            ],
            "medium": [
                f"How would you apply {concept} to solve a problem?",
                f"Explain the relationship between {concept} and {subject}.",
                f"What are the key steps in working with {concept}?"
            ],
            "hard": [
                f"Create a challenging problem involving {concept} and solve it.",
                f"Explain why {concept} is important in {subject} and give a real-world application.",
                f"How does understanding {concept} prepare you for more advanced topics?"
            ]
        }
        return random.choice(templates.get(difficulty, templates["medium"]))


def quick_answer(question: str, student_name: str, level: str) -> str:
    """Get answer from AI."""
    if not AI_AVAILABLE:
        return f"[{student_name}] Answer for {level}: {question[:30]}..."
    
    try:
        curriculum = K12_CURRICULUM.get(level)
        context = f"You are {student_name}, a {curriculum.name} student ({curriculum.real_world_age}). Answer appropriately for your level."
        
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


def quick_grade(question: str, answer: str, difficulty: str, level: str) -> int:
    """Grade with level-appropriate expectations."""
    if not AI_AVAILABLE:
        base = {"easy": 75, "medium": 65, "hard": 55}
        return base.get(difficulty, 65) + random.randint(-10, 20)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": f"Grade this {level} level {difficulty} question 0-100. Be encouraging. Minimum 30."},
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
        base = {"easy": 75, "medium": 65, "hard": 55}
        return base.get(difficulty, 65) + random.randint(-5, 15)


def print_level_header(level: str):
    """Print level header."""
    curriculum = K12_CURRICULUM.get(level)
    if not curriculum:
        return
    
    category_emoji = {
        "elementary": "🏫",
        "middle": "📚",
        "high": "🎓",
        "undergraduate": "🏛️",
        "graduate": "🔬",
        "research": "🚀"
    }
    emoji = category_emoji.get(curriculum.category, "📖")
    
    print(f"\n{'='*60}")
    print(f"  {emoji} {curriculum.name} (Level {level})")
    print(f"  {curriculum.description}")
    print(f"  Age equivalent: {curriculum.real_world_age}")
    print(f"  Subjects: {', '.join(curriculum.subjects[:3])}...")
    print(f"  Mastery needed: {curriculum.mastery_threshold}%")
    print(f"{'='*60}")


def run_k12_journey(students: List[str] = None, max_sessions: int = 20):
    """
    Run the K-12 and Higher Education journey.
    """
    
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*8 + "AETHER K-12 & HIGHER EDUCATION" + " "*16 + "║")
    print("║" + " "*5 + "Kindergarten → PhD → Yang-Mills Ready" + " "*13 + "║")
    print("╚" + "="*58 + "╝")
    
    if students is None:
        students = ["Stratify", "Principia"]
    
    # Initialize
    k12_students = {name: K12Student(name) for name in students}
    quiz_generator = AdaptiveK12Quiz()
    break_manager = get_break_manager()
    
    # Show current status
    print("\n📚 Student Status:")
    for name, student in k12_students.items():
        curriculum = K12_CURRICULUM.get(student.current_level)
        print(f"   {name}: {curriculum.name} ({student.current_level})")
        print(f"      Questions: {student.total_questions}, Graduations: {len(student.graduations)}")
    
    # Track group projects
    total_questions_all = sum(s.total_questions for s in k12_students.values())
    project_milestones = [200, 500, 900, 1400]  # When to trigger projects
    projects_done = min(len([m for m in project_milestones if total_questions_all >= m]), 4)
    
    # Main learning loop
    for session in range(1, max_sessions + 1):
        print(f"\n{'─'*60}")
        print(f"  SESSION {session}/{max_sessions}")
        print(f"{'─'*60}")
        
        # Check for group project
        total_questions_all = sum(s.total_questions for s in k12_students.values())
        if projects_done < 4 and total_questions_all >= project_milestones[projects_done]:
            print(f"\n  🎯 GROUP PROJECT TIME!")
            print(f"     Project {projects_done + 1}/4: Collaborative Learning Activity")
            print(f"     Participants: {', '.join(students)}")
            for name, student in k12_students.items():
                student.group_projects += 1
                student.save()
            projects_done += 1
            print(f"     ✅ Project complete! ({4 - projects_done} remaining)")
        
        # Each student takes a quiz
        for name, student in k12_students.items():
            curriculum = K12_CURRICULUM.get(student.current_level)
            
            # Check if at research level (graduated)
            if student.current_level == "RES":
                print(f"\n  🚀 {name} is at Research Level - Ready for Yang-Mills!")
                continue
            
            # Show level header for new levels
            if student.level_questions == 0:
                print_level_header(student.current_level)
            
            # Generate quiz
            questions = quiz_generator.generate(student)
            
            print(f"\n  📝 {name}'s Quiz ({len(questions)} questions)")
            print(f"     Level: {curriculum.name} | Recent avg: {student.recent_average:.1f}%")
            
            # Take quiz
            quiz_scores = []
            for i, q in enumerate(questions):
                answer = quick_answer(q["question"], name, student.current_level)
                score = quick_grade(q["question"], answer, q["difficulty"], student.current_level)
                quiz_scores.append(score)
                student.record_score(score, q["subject"])
                
                # Progress bar every 5 questions
                if (i + 1) % 5 == 0 or i == len(questions) - 1:
                    avg = sum(quiz_scores) / len(quiz_scores)
                    bar_len = int(30 * (i + 1) / len(questions))
                    bar = "█" * bar_len + "░" * (30 - bar_len)
                    emoji = "🌟" if avg >= 80 else "📈" if avg >= 65 else "🌱"
                    print(f"     [{bar}] {i+1}/{len(questions)} {emoji} {avg:.0f}%")
            
            # Quiz complete
            student.level_quizzes += 1
            student.total_quizzes += 1
            quiz_avg = sum(quiz_scores) / len(quiz_scores)
            
            print(f"\n     Quiz avg: {quiz_avg:.1f}% | Level avg: {student.level_average:.1f}%")
            print(f"     Progress: {student.level_questions}/{curriculum.min_questions} questions, "
                  f"{student.level_quizzes}/{curriculum.min_quizzes} quizzes")
            
            # Check for advancement
            if student.can_advance():
                next_level = student.advance()
                if next_level:
                    next_curriculum = K12_CURRICULUM.get(next_level)
                    print(f"\n     🎉 ADVANCED to {next_curriculum.name}!")
                    
                    # Check for graduation milestone
                    milestones = get_graduation_milestones()
                    prev_level = EDUCATION_ORDER[EDUCATION_ORDER.index(next_level) - 1]
                    if prev_level in milestones:
                        print(f"     🎓 GRADUATION: {milestones[prev_level]}!")
            
            # Break if needed
            if break_manager.should_take_break(student.level_questions, quiz_scores):
                break_info = break_manager.take_break(name)
                print(f"\n     🎮 Break: {break_info['activity']['name']}")
            
            student.save()
        
        # Session summary
        print(f"\n  📊 Session Summary:")
        for name, student in k12_students.items():
            curriculum = K12_CURRICULUM.get(student.current_level)
            level_idx = get_level_index(student.current_level)
            total_levels = len(EDUCATION_ORDER)
            progress_pct = (level_idx / total_levels) * 100
            print(f"     {name}: {curriculum.name} ({progress_pct:.0f}% to Yang-Mills)")
        
        # Motivation
        if session % 3 == 0:
            print(f"\n  💫 {get_motivation()}")
    
    # Final report
    print("\n" + "="*60)
    print("  JOURNEY PROGRESS REPORT")
    print("="*60)
    
    for name, student in k12_students.items():
        curriculum = K12_CURRICULUM.get(student.current_level)
        level_idx = get_level_index(student.current_level)
        
        print(f"\n  📜 {name}'s Academic Record:")
        print(f"     Current Level: {curriculum.name} ({student.current_level})")
        print(f"     Total Questions: {student.total_questions}")
        print(f"     Total Quizzes: {student.total_quizzes}")
        print(f"     Group Projects: {student.group_projects}/4")
        
        if student.graduations:
            print(f"     Graduations: {', '.join(student.graduations)}")
        
        if student.characteristics:
            top_chars = sorted(student.characteristics.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"     Top Characteristics:")
            for char, score in top_chars:
                print(f"       • {char.replace('_', ' ').title()}: {score:.1f}")
        
        # Progress to Yang-Mills
        progress = (level_idx / len(EDUCATION_ORDER)) * 100
        bar_len = int(40 * level_idx / len(EDUCATION_ORDER))
        bar = "█" * bar_len + "░" * (40 - bar_len)
        print(f"     Progress to Yang-Mills: [{bar}] {progress:.0f}%")
    
    return k12_students


if __name__ == "__main__":
    run_k12_journey(max_sessions=15)
