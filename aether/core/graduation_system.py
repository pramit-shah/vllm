#!/usr/bin/env python3.11
"""
AETHER Graduation System

A comprehensive educational journey with:
- Grade-by-grade progression (must master before advancing)
- Adaptive quizzes (10-50 questions)
- Group projects (4 total across entire journey)
- Characteristic discovery (natural interests emerge)
"""

import os
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

# Import K-12 curriculum
try:
    from k12_curriculum import K12_CURRICULUM, EDUCATION_ORDER, get_next_level, get_graduation_milestones
    USE_K12 = True
except ImportError:
    USE_K12 = False


class GradeLevel(Enum):
    """Educational grade levels."""
    GRADE_1 = 1   # Foundations
    GRADE_2 = 2   # Basic Operations
    GRADE_3 = 3   # Intermediate Concepts
    GRADE_4 = 4   # Advanced Basics
    GRADE_5 = 5   # Pre-Algebra
    GRADE_6 = 6   # Algebra & Geometry
    GRADE_7 = 7   # Advanced Algebra
    GRADE_8 = 8   # Pre-Calculus
    GRADE_9 = 9   # Calculus & Analysis
    GRADE_10 = 10 # Advanced Mathematics
    GRADUATED = 11 # Completed all grades


@dataclass
class GradeCurriculum:
    """Curriculum for each grade level."""
    grade: int
    name: str
    topics: List[str]
    mastery_threshold: float  # % needed to advance
    min_questions_to_advance: int
    description: str


# Define curriculum for each grade (legacy - now uses K12_CURRICULUM)
GRADE_CURRICULA = {
    1: GradeCurriculum(
        grade=1, name="Foundations",
        topics=["numbers", "counting", "basic arithmetic", "simple patterns"],
        mastery_threshold=70.0, min_questions_to_advance=20,
        description="Building blocks of mathematics"
    ),
    2: GradeCurriculum(
        grade=2, name="Basic Operations",
        topics=["addition", "subtraction", "multiplication", "division", "order of operations"],
        mastery_threshold=72.0, min_questions_to_advance=25,
        description="Mastering fundamental operations"
    ),
    3: GradeCurriculum(
        grade=3, name="Intermediate Concepts",
        topics=["fractions", "decimals", "percentages", "ratios", "proportions"],
        mastery_threshold=74.0, min_questions_to_advance=25,
        description="Working with parts and wholes"
    ),
    4: GradeCurriculum(
        grade=4, name="Advanced Basics",
        topics=["negative numbers", "exponents", "roots", "scientific notation"],
        mastery_threshold=75.0, min_questions_to_advance=30,
        description="Expanding the number system"
    ),
    5: GradeCurriculum(
        grade=5, name="Pre-Algebra",
        topics=["variables", "expressions", "simple equations", "inequalities", "functions intro"],
        mastery_threshold=76.0, min_questions_to_advance=30,
        description="Introduction to abstract thinking"
    ),
    6: GradeCurriculum(
        grade=6, name="Algebra & Geometry",
        topics=["linear equations", "graphing", "angles", "triangles", "circles", "area", "volume"],
        mastery_threshold=77.0, min_questions_to_advance=35,
        description="Shapes, spaces, and equations"
    ),
    7: GradeCurriculum(
        grade=7, name="Advanced Algebra",
        topics=["quadratics", "polynomials", "factoring", "systems of equations", "matrices intro"],
        mastery_threshold=78.0, min_questions_to_advance=35,
        description="Complex algebraic structures"
    ),
    8: GradeCurriculum(
        grade=8, name="Pre-Calculus",
        topics=["trigonometry", "logarithms", "sequences", "series", "limits intro", "vectors"],
        mastery_threshold=79.0, min_questions_to_advance=40,
        description="Preparing for calculus"
    ),
    9: GradeCurriculum(
        grade=9, name="Calculus & Analysis",
        topics=["derivatives", "integrals", "differential equations", "multivariable calculus"],
        mastery_threshold=80.0, min_questions_to_advance=40,
        description="The mathematics of change"
    ),
    10: GradeCurriculum(
        grade=10, name="Advanced Mathematics",
        topics=["linear algebra", "abstract algebra", "topology basics", "real analysis", "complex analysis"],
        mastery_threshold=82.0, min_questions_to_advance=50,
        description="University-level foundations"
    )
}


@dataclass
class GradeProgress:
    """Track progress within a grade."""
    grade: int
    questions_answered: int = 0
    total_score: float = 0
    scores: List[float] = field(default_factory=list)
    topics_mastered: List[str] = field(default_factory=list)
    quizzes_taken: int = 0
    started: str = field(default_factory=lambda: datetime.now().isoformat())
    completed: str = None
    
    @property
    def average_score(self) -> float:
        return self.total_score / self.questions_answered if self.questions_answered > 0 else 0
    
    @property
    def recent_average(self) -> float:
        """Average of last 10 scores."""
        if len(self.scores) < 10:
            return self.average_score
        return sum(self.scores[-10:]) / 10
    
    def can_advance(self, curriculum: GradeCurriculum) -> bool:
        """Check if ready to advance to next grade."""
        if self.questions_answered < curriculum.min_questions_to_advance:
            return False
        if self.recent_average < curriculum.mastery_threshold:
            return False
        return True


@dataclass
class StudentRecord:
    """Complete academic record for a framework."""
    framework: str
    current_grade: int = 1
    enrolled: str = field(default_factory=lambda: datetime.now().isoformat())
    grade_history: Dict[int, Dict] = field(default_factory=dict)
    total_questions: int = 0
    total_quizzes: int = 0
    group_projects_completed: int = 0
    characteristics: Dict[str, float] = field(default_factory=dict)
    interests_discovered: List[str] = field(default_factory=list)
    graduated: bool = False
    graduation_date: str = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StudentRecord':
        return cls(**data)


class AdaptiveQuizGenerator:
    """Generate quizzes with adaptive question counts."""
    
    def __init__(self):
        self.min_questions = 10
        self.max_questions = 50
    
    def determine_quiz_length(self, student: StudentRecord, grade_progress: GradeProgress) -> int:
        """
        Determine quiz length based on student's state.
        
        Factors:
        - Recent performance (struggling = fewer questions)
        - Time in grade (longer = more questions)
        - Confidence level (high = can handle more)
        """
        base = self.min_questions
        
        # Performance factor
        if grade_progress.recent_average >= 80:
            base += 15  # Doing well, can handle more
        elif grade_progress.recent_average >= 70:
            base += 10  # Good, moderate increase
        elif grade_progress.recent_average < 60:
            base -= 5   # Struggling, keep it short
        
        # Experience factor
        if grade_progress.questions_answered > 50:
            base += 10  # More experienced
        elif grade_progress.questions_answered > 25:
            base += 5
        
        # Random variation (±5)
        base += random.randint(-5, 5)
        
        # Clamp to valid range
        return max(self.min_questions, min(self.max_questions, base))
    
    def generate_quiz(self, grade: int, num_questions: int) -> List[Dict]:
        """Generate a quiz for the given grade."""
        curriculum = GRADE_CURRICULA.get(grade)
        if not curriculum:
            return []
        
        questions = []
        for i in range(num_questions):
            topic = random.choice(curriculum.topics)
            difficulty = self._get_difficulty(i, num_questions)
            
            questions.append({
                "id": f"G{grade}_Q{i+1}",
                "topic": topic,
                "difficulty": difficulty,
                "grade": grade,
                "question": self._create_question(topic, difficulty, grade)
            })
        
        return questions
    
    def _get_difficulty(self, question_num: int, total: int) -> str:
        """Difficulty increases through the quiz."""
        progress = question_num / total
        if progress < 0.3:
            return "easy"
        elif progress < 0.7:
            return "medium"
        else:
            return "hard"
    
    def _create_question(self, topic: str, difficulty: str, grade: int) -> str:
        """Create a question for the topic."""
        templates = {
            "easy": [
                f"Explain the basic concept of {topic}.",
                f"What is {topic} and give a simple example.",
                f"Define {topic} in your own words."
            ],
            "medium": [
                f"How does {topic} relate to other concepts you've learned?",
                f"Solve a problem involving {topic} and explain your reasoning.",
                f"What are the key properties of {topic}?"
            ],
            "hard": [
                f"Apply {topic} to solve a novel problem you create.",
                f"Explain a common misconception about {topic} and why it's wrong.",
                f"How would you teach {topic} to someone who's never seen it?"
            ]
        }
        return random.choice(templates.get(difficulty, templates["medium"]))


@dataclass
class GroupProject:
    """A collaborative project for frameworks."""
    project_id: str
    title: str
    description: str
    objectives: List[str]
    estimated_difficulty: str  # "introductory", "intermediate", "advanced", "challenging"
    topics_involved: List[str]
    collaboration_type: str  # "parallel", "sequential", "discussion"
    
    # Tracking
    assigned_to: List[str] = field(default_factory=list)
    started: str = None
    completed: str = None
    outcomes: Dict[str, str] = field(default_factory=dict)
    insights_gained: List[str] = field(default_factory=list)


# The 4 group projects across the entire journey
GROUP_PROJECTS = [
    GroupProject(
        project_id="GP1",
        title="Number Patterns Exploration",
        description="Work together to discover and document interesting number patterns.",
        objectives=[
            "Find 3 interesting number sequences",
            "Explain why each pattern works",
            "Create one original pattern"
        ],
        estimated_difficulty="introductory",
        topics_involved=["patterns", "sequences", "arithmetic"],
        collaboration_type="parallel"
    ),
    GroupProject(
        project_id="GP2",
        title="Geometry in the Real World",
        description="Identify and analyze geometric shapes and relationships in everyday objects.",
        objectives=[
            "Find 5 real-world examples of geometric concepts",
            "Calculate measurements for each",
            "Explain the mathematical principles"
        ],
        estimated_difficulty="intermediate",
        topics_involved=["geometry", "measurement", "spatial reasoning"],
        collaboration_type="discussion"
    ),
    GroupProject(
        project_id="GP3",
        title="Mathematical Proof Workshop",
        description="Collaborate to construct and verify mathematical proofs.",
        objectives=[
            "Prove 2 theorems using different methods",
            "Critique each other's proof attempts",
            "Document the proof process"
        ],
        estimated_difficulty="advanced",
        topics_involved=["logic", "proof techniques", "mathematical reasoning"],
        collaboration_type="sequential"
    ),
    GroupProject(
        project_id="GP4",
        title="Research Investigation",
        description="Investigate an open mathematical question together.",
        objectives=[
            "Research the background of the problem",
            "Attempt different solution approaches",
            "Document findings and insights"
        ],
        estimated_difficulty="challenging",
        topics_involved=["research", "problem-solving", "advanced mathematics"],
        collaboration_type="discussion"
    )
]


class GroupProjectManager:
    """Manage group projects across the entire training journey."""
    
    def __init__(self, storage_path: str = "/home/ubuntu/aether/memory/group_projects.json"):
        self.storage_path = storage_path
        self.projects = list(GROUP_PROJECTS)  # Copy
        self.completed_projects: List[Dict] = []
        self.next_project_index = 0
        self._load()
    
    def _load(self):
        """Load project state."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.completed_projects = data.get("completed", [])
                    self.next_project_index = data.get("next_index", 0)
            except:
                pass
    
    def _save(self):
        """Save project state."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump({
                "completed": self.completed_projects,
                "next_index": self.next_project_index,
                "total_projects": 4
            }, f, indent=2)
    
    def should_assign_project(self, total_questions_all_students: int) -> bool:
        """
        Determine if it's time for a group project.
        
        Projects are assigned at random intervals across the journey,
        not per session but overall.
        """
        if self.next_project_index >= 4:
            return False  # All projects done
        
        # Rough milestones for when projects might happen
        # Project 1: Around 100-200 total questions
        # Project 2: Around 300-500 total questions
        # Project 3: Around 600-900 total questions
        # Project 4: Around 1000+ total questions (near graduation)
        
        milestones = [150, 400, 750, 1100]
        target = milestones[self.next_project_index]
        
        # Add randomness (±30%)
        variance = int(target * 0.3)
        trigger_point = target + random.randint(-variance, variance)
        
        return total_questions_all_students >= trigger_point
    
    def get_next_project(self) -> Optional[GroupProject]:
        """Get the next project to assign."""
        if self.next_project_index >= 4:
            return None
        return self.projects[self.next_project_index]
    
    def start_project(self, frameworks: List[str]) -> Optional[GroupProject]:
        """Start a group project."""
        project = self.get_next_project()
        if not project:
            return None
        
        project.assigned_to = frameworks
        project.started = datetime.now().isoformat()
        return project
    
    def complete_project(self, project: GroupProject, outcomes: Dict[str, str], 
                        insights: List[str]) -> Dict:
        """Complete a group project."""
        project.completed = datetime.now().isoformat()
        project.outcomes = outcomes
        project.insights_gained = insights
        
        self.completed_projects.append({
            "project_id": project.project_id,
            "title": project.title,
            "participants": project.assigned_to,
            "started": project.started,
            "completed": project.completed,
            "outcomes": outcomes,
            "insights": insights
        })
        
        self.next_project_index += 1
        self._save()
        
        return {
            "project": project.title,
            "completed": True,
            "projects_remaining": 4 - self.next_project_index
        }
    
    def get_status(self) -> Dict:
        """Get project status."""
        return {
            "completed": len(self.completed_projects),
            "remaining": 4 - self.next_project_index,
            "next_project": self.projects[self.next_project_index].title if self.next_project_index < 4 else "All complete",
            "history": self.completed_projects
        }


class CharacteristicTracker:
    """Track and discover each framework's natural characteristics."""
    
    # Categories of characteristics to track
    CHARACTERISTICS = [
        "abstract_thinking",      # Preference for abstract concepts
        "computational",          # Preference for calculations
        "visual_spatial",         # Preference for geometry/visualization
        "logical_deduction",      # Preference for proofs/logic
        "pattern_recognition",    # Ability to spot patterns
        "creative_problem_solving", # Novel approaches
        "systematic_approach",    # Methodical problem-solving
        "intuitive_leaps",        # Making intuitive connections
        "attention_to_detail",    # Careful, precise work
        "big_picture_thinking"    # Seeing overall structure
    ]
    
    # Map topics to characteristics
    TOPIC_CHARACTERISTICS = {
        "numbers": ["computational", "pattern_recognition"],
        "arithmetic": ["computational", "systematic_approach"],
        "patterns": ["pattern_recognition", "intuitive_leaps"],
        "geometry": ["visual_spatial", "logical_deduction"],
        "algebra": ["abstract_thinking", "systematic_approach"],
        "proofs": ["logical_deduction", "attention_to_detail"],
        "calculus": ["abstract_thinking", "computational"],
        "topology": ["abstract_thinking", "big_picture_thinking"],
        "analysis": ["attention_to_detail", "logical_deduction"]
    }
    
    def __init__(self):
        self.framework_characteristics: Dict[str, Dict[str, float]] = {}
        self.topic_performance: Dict[str, Dict[str, List[float]]] = {}
    
    def record_performance(self, framework: str, topic: str, score: float):
        """Record performance and update characteristics."""
        # Initialize if needed
        if framework not in self.framework_characteristics:
            self.framework_characteristics[framework] = {c: 50.0 for c in self.CHARACTERISTICS}
        if framework not in self.topic_performance:
            self.topic_performance[framework] = {}
        if topic not in self.topic_performance[framework]:
            self.topic_performance[framework][topic] = []
        
        # Record score
        self.topic_performance[framework][topic].append(score)
        
        # Update characteristics based on topic
        topic_lower = topic.lower()
        for topic_key, chars in self.TOPIC_CHARACTERISTICS.items():
            if topic_key in topic_lower:
                for char in chars:
                    # Adjust characteristic based on performance
                    current = self.framework_characteristics[framework][char]
                    # Move toward score, weighted by performance
                    adjustment = (score - current) * 0.1
                    self.framework_characteristics[framework][char] = max(0, min(100, current + adjustment))
    
    def get_characteristics(self, framework: str) -> Dict[str, float]:
        """Get current characteristics for a framework."""
        return self.framework_characteristics.get(framework, {})
    
    def get_top_characteristics(self, framework: str, n: int = 3) -> List[Tuple[str, float]]:
        """Get top N characteristics for a framework."""
        chars = self.get_characteristics(framework)
        sorted_chars = sorted(chars.items(), key=lambda x: x[1], reverse=True)
        return sorted_chars[:n]
    
    def discover_interests(self, framework: str) -> List[str]:
        """Discover natural interests based on performance patterns."""
        if framework not in self.topic_performance:
            return []
        
        # Find topics with consistently high performance
        interests = []
        for topic, scores in self.topic_performance[framework].items():
            if len(scores) >= 3 and sum(scores) / len(scores) >= 75:
                interests.append(topic)
        
        return interests
    
    def compare_frameworks(self, frameworks: List[str]) -> Dict:
        """Compare characteristics between frameworks."""
        comparison = {}
        for char in self.CHARACTERISTICS:
            comparison[char] = {}
            for fw in frameworks:
                if fw in self.framework_characteristics:
                    comparison[char][fw] = self.framework_characteristics[fw].get(char, 50)
        
        # Find complementary strengths
        complementary = []
        if len(frameworks) == 2:
            fw1, fw2 = frameworks
            for char in self.CHARACTERISTICS:
                score1 = self.framework_characteristics.get(fw1, {}).get(char, 50)
                score2 = self.framework_characteristics.get(fw2, {}).get(char, 50)
                # If one is strong where other is weak
                if abs(score1 - score2) > 20:
                    stronger = fw1 if score1 > score2 else fw2
                    complementary.append(f"{stronger} excels at {char.replace('_', ' ')}")
        
        return {
            "by_characteristic": comparison,
            "complementary_strengths": complementary
        }


class GraduationSystem:
    """
    Main graduation system managing the entire educational journey.
    """
    
    def __init__(self, storage_dir: str = "/home/ubuntu/aether/memory"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        self.students: Dict[str, StudentRecord] = {}
        self.grade_progress: Dict[str, GradeProgress] = {}
        self.quiz_generator = AdaptiveQuizGenerator()
        self.project_manager = GroupProjectManager(os.path.join(storage_dir, "group_projects.json"))
        self.characteristic_tracker = CharacteristicTracker()
        
        self._load_students()
    
    def _get_student_path(self, framework: str) -> str:
        return os.path.join(self.storage_dir, f"{framework.lower()}_academic_record.json")
    
    def _load_students(self):
        """Load all student records."""
        for filename in os.listdir(self.storage_dir):
            if filename.endswith("_academic_record.json"):
                framework = filename.replace("_academic_record.json", "").title()
                path = self._get_student_path(framework)
                try:
                    with open(path, 'r') as f:
                        data = json.load(f)
                        self.students[framework] = StudentRecord.from_dict(data)
                        # Load current grade progress
                        grade = self.students[framework].current_grade
                        if str(grade) in data.get("grade_history", {}):
                            gp_data = data["grade_history"][str(grade)]
                            self.grade_progress[framework] = GradeProgress(**gp_data)
                except Exception as e:
                    print(f"Error loading {framework}: {e}")
    
    def _save_student(self, framework: str):
        """Save a student's record."""
        if framework not in self.students:
            return
        
        student = self.students[framework]
        
        # Update grade history with current progress
        if framework in self.grade_progress:
            gp = self.grade_progress[framework]
            student.grade_history[str(gp.grade)] = asdict(gp)
        
        path = self._get_student_path(framework)
        with open(path, 'w') as f:
            json.dump(student.to_dict(), f, indent=2)
    
    def enroll(self, framework: str) -> StudentRecord:
        """Enroll a new student or get existing."""
        if framework not in self.students:
            self.students[framework] = StudentRecord(framework=framework)
            self.grade_progress[framework] = GradeProgress(grade=1)
            self._save_student(framework)
        return self.students[framework]
    
    def get_current_grade(self, framework: str) -> Tuple[int, GradeCurriculum]:
        """Get current grade and curriculum."""
        student = self.enroll(framework)
        grade = student.current_grade
        curriculum = GRADE_CURRICULA.get(grade)
        return grade, curriculum
    
    def generate_quiz(self, framework: str) -> Tuple[List[Dict], int]:
        """Generate an adaptive quiz for the student."""
        student = self.enroll(framework)
        
        if framework not in self.grade_progress:
            self.grade_progress[framework] = GradeProgress(grade=student.current_grade)
        
        gp = self.grade_progress[framework]
        num_questions = self.quiz_generator.determine_quiz_length(student, gp)
        questions = self.quiz_generator.generate_quiz(student.current_grade, num_questions)
        
        return questions, num_questions
    
    def record_answer(self, framework: str, topic: str, score: float) -> Dict:
        """Record an answer and check for advancement."""
        student = self.enroll(framework)
        
        if framework not in self.grade_progress:
            self.grade_progress[framework] = GradeProgress(grade=student.current_grade)
        
        gp = self.grade_progress[framework]
        
        # Record the score
        gp.questions_answered += 1
        gp.total_score += score
        gp.scores.append(score)
        student.total_questions += 1
        
        # Track characteristics
        self.characteristic_tracker.record_performance(framework, topic, score)
        
        # Check for topic mastery
        curriculum = GRADE_CURRICULA.get(gp.grade)
        if topic not in gp.topics_mastered:
            topic_scores = [s for i, s in enumerate(gp.scores) if i % len(curriculum.topics) == curriculum.topics.index(topic) % len(curriculum.topics)]
            if len(topic_scores) >= 3 and sum(topic_scores[-3:]) / 3 >= 75:
                gp.topics_mastered.append(topic)
        
        # Check for grade advancement
        can_advance = False
        if curriculum and gp.can_advance(curriculum):
            can_advance = True
        
        self._save_student(framework)
        
        return {
            "questions_in_grade": gp.questions_answered,
            "grade_average": gp.average_score,
            "recent_average": gp.recent_average,
            "topics_mastered": len(gp.topics_mastered),
            "can_advance": can_advance,
            "current_grade": gp.grade
        }
    
    def advance_grade(self, framework: str) -> Dict:
        """Advance student to next grade."""
        student = self.enroll(framework)
        gp = self.grade_progress[framework]
        
        old_grade = student.current_grade
        
        # Complete current grade
        gp.completed = datetime.now().isoformat()
        student.grade_history[str(old_grade)] = asdict(gp)
        
        # Advance
        new_grade = old_grade + 1
        student.current_grade = new_grade
        
        # Check for graduation
        if new_grade > 10:
            student.graduated = True
            student.graduation_date = datetime.now().isoformat()
            self._save_student(framework)
            return {
                "graduated": True,
                "message": f"🎓 CONGRATULATIONS! {framework} has GRADUATED!",
                "total_questions": student.total_questions,
                "characteristics": self.characteristic_tracker.get_top_characteristics(framework)
            }
        
        # Start new grade
        self.grade_progress[framework] = GradeProgress(grade=new_grade)
        
        self._save_student(framework)
        
        new_curriculum = GRADE_CURRICULA.get(new_grade)
        return {
            "graduated": False,
            "old_grade": old_grade,
            "new_grade": new_grade,
            "new_grade_name": new_curriculum.name if new_curriculum else "Unknown",
            "message": f"📈 {framework} advanced from Grade {old_grade} to Grade {new_grade}!"
        }
    
    def check_group_project(self) -> Optional[GroupProject]:
        """Check if it's time for a group project."""
        total_questions = sum(s.total_questions for s in self.students.values())
        
        if self.project_manager.should_assign_project(total_questions):
            return self.project_manager.get_next_project()
        return None
    
    def start_group_project(self) -> Optional[Dict]:
        """Start a group project with all enrolled students."""
        frameworks = list(self.students.keys())
        if len(frameworks) < 2:
            return None
        
        project = self.project_manager.start_project(frameworks)
        if not project:
            return None
        
        return {
            "project_id": project.project_id,
            "title": project.title,
            "description": project.description,
            "objectives": project.objectives,
            "participants": frameworks,
            "collaboration_type": project.collaboration_type
        }
    
    def complete_group_project(self, outcomes: Dict[str, str], insights: List[str]) -> Dict:
        """Complete the current group project."""
        project = self.project_manager.get_next_project()
        if not project or not project.started:
            return {"error": "No active project"}
        
        # Update student records
        for fw in project.assigned_to:
            if fw in self.students:
                self.students[fw].group_projects_completed += 1
                self._save_student(fw)
        
        return self.project_manager.complete_project(project, outcomes, insights)
    
    def get_transcript(self, framework: str) -> Dict:
        """Get complete academic transcript."""
        student = self.enroll(framework)
        
        return {
            "framework": framework,
            "enrolled": student.enrolled,
            "current_grade": student.current_grade,
            "graduated": student.graduated,
            "graduation_date": student.graduation_date,
            "total_questions": student.total_questions,
            "total_quizzes": student.total_quizzes,
            "group_projects": student.group_projects_completed,
            "grade_history": student.grade_history,
            "top_characteristics": self.characteristic_tracker.get_top_characteristics(framework),
            "discovered_interests": self.characteristic_tracker.discover_interests(framework),
            "project_status": self.project_manager.get_status()
        }
    
    def get_class_status(self) -> Dict:
        """Get status of all students."""
        status = {
            "students": {},
            "total_questions_all": 0,
            "group_projects": self.project_manager.get_status()
        }
        
        for fw, student in self.students.items():
            status["students"][fw] = {
                "grade": student.current_grade,
                "questions": student.total_questions,
                "graduated": student.graduated,
                "projects_done": student.group_projects_completed
            }
            status["total_questions_all"] += student.total_questions
        
        # Check for upcoming project
        if self.project_manager.next_project_index < 4:
            next_project = self.project_manager.get_next_project()
            status["next_project_available"] = next_project.title if next_project else None
        
        return status


# Singleton
_graduation_system = None

def get_graduation_system() -> GraduationSystem:
    """Get the singleton graduation system."""
    global _graduation_system
    if _graduation_system is None:
        _graduation_system = GraduationSystem()
    return _graduation_system
