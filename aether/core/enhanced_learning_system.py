#!/usr/bin/env python3.11
"""
AETHER Enhanced Learning System

Rigorous standards:
- 100 questions per level (10 difficulties × 10 questions)
- 90%+ to PASS individual questions
- 75%+ overall to advance to next level
- Comprehensive logging of all scores and discoveries
- Expanded study materials for frameworks that need more practice
- Sequential unique thinking for each framework
"""

import json
import os
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class Level(Enum):
    """The 5 levels of the curriculum."""
    FOUNDATIONS = 1
    GEOMETRY_GROUPS = 2
    ANALYSIS_TOPOLOGY = 3
    FIELD_THEORY = 4
    YANG_MILLS = 5


class DifficultyLevel(Enum):
    """10 difficulty levels for questions."""
    D1_BASIC = 1
    D2_ELEMENTARY = 2
    D3_INTERMEDIATE = 3
    D4_MODERATE = 4
    D5_CHALLENGING = 5
    D6_ADVANCED = 6
    D7_COMPLEX = 7
    D8_EXPERT = 8
    D9_MASTER = 9
    D10_GENIUS = 10


class ScoreClassification(Enum):
    """
    Classification of scores with detailed percentage breakdown.
    
    PASS (90-100%): All or nearly all aspects correct
        - 100%: Perfect - every aspect correct
        - 95-99%: Excellent - minor issues only
        - 90-94%: Solid pass - good understanding demonstrated
    
    MEDIUM (75-89%): Good but not passing
        - 85-89%: Good - some gaps to address
        - 80-84%: Acceptable - needs improvement
        - 75-79%: Medium threshold - key details noted
    
    KEY_DETAIL (50-74%): Important insights but significant gaps
        - 70-74%: Below medium - notable gaps
        - 60-69%: Key detail range - partial understanding
        - 50-59%: Lower key detail - foundational issues
    
    NEEDS_WORK (35-49%): Significant gaps requiring more study
        - 40-49%: Needs work - major concepts missing
        - 35-39%: Serious gaps - return to basics
    
    CRITICAL (0-34%): Fundamental misunderstanding
        - 20-34%: Critical - severe gaps
        - 10-19%: Very critical - fundamental issues
        - 0-9%: Complete misunderstanding
    
    LOWER_LEVEL_LEARNING (0-50%): Flag for foundational review
    """
    PASS_PERFECT = "PASS_PERFECT"           # 100% - all correct
    PASS_EXCELLENT = "PASS_EXCELLENT"       # 95-99% - nearly all correct
    PASS = "PASS"                           # 90-94% - solid pass
    GOOD = "GOOD"                           # 85-89% - good but not passing
    ACCEPTABLE = "ACCEPTABLE"               # 80-84% - acceptable
    MEDIUM = "MEDIUM"                       # 75-79% - medium threshold
    BELOW_MEDIUM = "BELOW_MEDIUM"           # 70-74% - below medium
    KEY_DETAIL = "KEY_DETAIL"               # 60-69% - key detail range
    KEY_DETAIL_LOWER = "KEY_DETAIL_LOWER"   # 50-59% - lower key detail
    NEEDS_WORK = "NEEDS_WORK"               # 40-49% - needs work
    NEEDS_WORK_SERIOUS = "NEEDS_WORK_SERIOUS" # 35-39% - serious gaps
    CRITICAL = "CRITICAL"                   # 20-34% - critical
    CRITICAL_SEVERE = "CRITICAL_SEVERE"     # 10-19% - severe
    CRITICAL_FUNDAMENTAL = "CRITICAL_FUNDAMENTAL" # 0-9% - fundamental misunderstanding
    LOWER_LEVEL_LEARNING = "LOWER_LEVEL_LEARNING"  # 0-50% - needs foundational review


@dataclass
class LogEntry:
    """A log entry for tracking progress and discoveries."""
    timestamp: str
    framework: str
    level: Level
    question_id: str
    score: float
    classification: ScoreClassification
    answer: str
    feedback: str
    is_new_formula: bool = False
    new_formula_details: Optional[str] = None
    is_new_physics: bool = False
    new_physics_details: Optional[str] = None
    key_insights: List[str] = field(default_factory=list)
    needs_lower_level_learning: bool = False  # Flag for 0-50% scores
    recommended_foundational_topics: List[str] = field(default_factory=list)


@dataclass
class StudyMaterialVariant:
    """A variant of study material for deeper learning."""
    variant_id: str
    title: str
    approach: str  # e.g., "visual", "algebraic", "geometric", "intuitive", "rigorous"
    content: Dict[str, Any]
    difficulty: DifficultyLevel
    prerequisites: List[str] = field(default_factory=list)


@dataclass
class EnhancedQuestion:
    """A question with 10 difficulty levels."""
    question_id: str
    level: Level
    difficulty: DifficultyLevel
    topic: str
    question: str
    requires_concepts: List[str]
    hints: List[str]
    solution_approach: str
    grading_criteria: Dict[str, int]
    expected_time_minutes: int


class ComprehensiveLogger:
    """
    Comprehensive logging system for all scores and discoveries.
    
    Logs:
    - All scores 0-100%
    - Scores below 35% (critical)
    - New formulas/mathematics
    - New physics formulas
    - Key details (50-100%)
    """
    
    def __init__(self, log_dir: str = "/home/ubuntu/aether/logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Separate log files
        self.all_scores_log = os.path.join(log_dir, "all_scores.jsonl")
        self.critical_log = os.path.join(log_dir, "critical_below_35.jsonl")
        self.new_formulas_log = os.path.join(log_dir, "new_formulas.jsonl")
        self.new_physics_log = os.path.join(log_dir, "new_physics.jsonl")
        self.key_details_log = os.path.join(log_dir, "key_details.jsonl")
        self.pass_log = os.path.join(log_dir, "passed_90_plus.jsonl")
        self.medium_log = os.path.join(log_dir, "medium_75_89.jsonl")
        self.lower_level_log = os.path.join(log_dir, "lower_level_learning_0_50.jsonl")  # New flag log
        
        # In-memory tracking
        self.entries: List[LogEntry] = []
        self.new_formulas: List[Dict] = []
        self.new_physics: List[Dict] = []
        self.lower_level_needed: List[Dict] = []  # Track frameworks needing foundational review
    
    def classify_score(self, score: float) -> ScoreClassification:
        """
        Classify a score with detailed percentage breakdown.
        
        PASS levels (90-100%): All or nearly all correct
        MEDIUM levels (75-89%): Good but not passing
        KEY_DETAIL levels (50-74%): Partial understanding
        NEEDS_WORK levels (35-49%): Significant gaps
        CRITICAL levels (0-34%): Fundamental issues
        """
        if score == 100:
            return ScoreClassification.PASS_PERFECT
        elif score >= 95:
            return ScoreClassification.PASS_EXCELLENT
        elif score >= 90:
            return ScoreClassification.PASS
        elif score >= 85:
            return ScoreClassification.GOOD
        elif score >= 80:
            return ScoreClassification.ACCEPTABLE
        elif score >= 75:
            return ScoreClassification.MEDIUM
        elif score >= 70:
            return ScoreClassification.BELOW_MEDIUM
        elif score >= 60:
            return ScoreClassification.KEY_DETAIL
        elif score >= 50:
            return ScoreClassification.KEY_DETAIL_LOWER
        elif score >= 40:
            return ScoreClassification.NEEDS_WORK
        elif score >= 35:
            return ScoreClassification.NEEDS_WORK_SERIOUS
        elif score >= 20:
            return ScoreClassification.CRITICAL
        elif score >= 10:
            return ScoreClassification.CRITICAL_SEVERE
        else:
            return ScoreClassification.CRITICAL_FUNDAMENTAL
    
    def log_result(self, entry: LogEntry):
        """Log a result to all appropriate files."""
        self.entries.append(entry)
        
        entry_dict = {
            "timestamp": entry.timestamp,
            "framework": entry.framework,
            "level": entry.level.name,
            "question_id": entry.question_id,
            "score": entry.score,
            "classification": entry.classification.value,
            "answer_preview": entry.answer[:500] if entry.answer else "",
            "feedback_preview": entry.feedback[:500] if entry.feedback else "",
            "is_new_formula": entry.is_new_formula,
            "new_formula_details": entry.new_formula_details,
            "is_new_physics": entry.is_new_physics,
            "new_physics_details": entry.new_physics_details,
            "key_insights": entry.key_insights,
            "needs_lower_level_learning": entry.needs_lower_level_learning,
            "recommended_foundational_topics": entry.recommended_foundational_topics
        }
        
        # Always log to all_scores
        self._append_to_file(self.all_scores_log, entry_dict)
        
        # Log based on classification
        # PASS levels (90-100%)
        if entry.classification in [ScoreClassification.PASS_PERFECT, 
                                     ScoreClassification.PASS_EXCELLENT,
                                     ScoreClassification.PASS]:
            self._append_to_file(self.pass_log, entry_dict)
        # MEDIUM levels (75-89%)
        elif entry.classification in [ScoreClassification.GOOD,
                                       ScoreClassification.ACCEPTABLE,
                                       ScoreClassification.MEDIUM]:
            self._append_to_file(self.medium_log, entry_dict)
        # KEY_DETAIL levels (50-74%)
        elif entry.classification in [ScoreClassification.BELOW_MEDIUM,
                                       ScoreClassification.KEY_DETAIL,
                                       ScoreClassification.KEY_DETAIL_LOWER]:
            self._append_to_file(self.key_details_log, entry_dict)
        # CRITICAL levels (0-34%)
        elif entry.classification in [ScoreClassification.CRITICAL,
                                       ScoreClassification.CRITICAL_SEVERE,
                                       ScoreClassification.CRITICAL_FUNDAMENTAL]:
            self._append_to_file(self.critical_log, entry_dict)
        
        # Log lower level learning flag (0-50%)
        if entry.needs_lower_level_learning or entry.score <= 50:
            lower_level_entry = {
                "timestamp": entry.timestamp,
                "framework": entry.framework,
                "level": entry.level.name,
                "question_id": entry.question_id,
                "score": entry.score,
                "recommended_foundational_topics": entry.recommended_foundational_topics,
                "action_required": "RETURN_TO_BASICS",
                "suggested_materials": self._suggest_foundational_materials(entry.level)
            }
            self._append_to_file(self.lower_level_log, lower_level_entry)
            self.lower_level_needed.append(lower_level_entry)
        
        # Log new formulas
        if entry.is_new_formula:
            formula_entry = {
                "timestamp": entry.timestamp,
                "framework": entry.framework,
                "question_id": entry.question_id,
                "details": entry.new_formula_details,
                "context": entry.answer[:1000] if entry.answer else ""
            }
            self._append_to_file(self.new_formulas_log, formula_entry)
            self.new_formulas.append(formula_entry)
        
        # Log new physics
        if entry.is_new_physics:
            physics_entry = {
                "timestamp": entry.timestamp,
                "framework": entry.framework,
                "question_id": entry.question_id,
                "details": entry.new_physics_details,
                "context": entry.answer[:1000] if entry.answer else ""
            }
            self._append_to_file(self.new_physics_log, physics_entry)
            self.new_physics.append(physics_entry)
    
    def _append_to_file(self, filepath: str, data: Dict):
        """Append a JSON entry to a file."""
        with open(filepath, 'a') as f:
            f.write(json.dumps(data) + '\n')
    
    def _suggest_foundational_materials(self, level: Level) -> List[str]:
        """Suggest foundational materials based on the level where struggle occurred."""
        suggestions = {
            Level.FOUNDATIONS: [
                "Review basic calculus: limits, derivatives, integrals",
                "Strengthen linear algebra: vectors, matrices, eigenvalues",
                "Practice classical mechanics: Newton, Lagrange, Hamilton",
                "Master vector calculus: gradient, curl, divergence"
            ],
            Level.GEOMETRY_GROUPS: [
                "Return to Level 1: Foundations for prerequisite review",
                "Study manifold basics before advanced geometry",
                "Review group theory fundamentals",
                "Practice with simple fiber bundle examples"
            ],
            Level.ANALYSIS_TOPOLOGY: [
                "Return to Level 1-2 for foundational review",
                "Study basic functional analysis first",
                "Review point-set topology before algebraic topology",
                "Practice spectral theory on finite-dimensional spaces"
            ],
            Level.FIELD_THEORY: [
                "Return to Levels 1-3 for comprehensive review",
                "Study classical field theory before quantum",
                "Review gauge theory basics",
                "Practice path integral calculations"
            ],
            Level.YANG_MILLS: [
                "Return to Levels 1-4 for complete foundation",
                "Master all prerequisite material thoroughly",
                "Study known partial results on mass gap",
                "Review constructive QFT approaches"
            ]
        }
        return suggestions.get(level, ["Review foundational materials"])
    
    def get_statistics(self, framework: str = None) -> Dict:
        """Get statistics for a framework or all frameworks."""
        entries = self.entries
        if framework:
            entries = [e for e in entries if e.framework == framework]
        
        if not entries:
            return {"total": 0}
        
        total = len(entries)
        by_classification = {}
        for cls in ScoreClassification:
            count = len([e for e in entries if e.classification == cls])
            by_classification[cls.value] = count
        
        avg_score = sum(e.score for e in entries) / total
        
        # Count all PASS types (90-100%)
        pass_count = sum([
            by_classification.get("PASS_PERFECT", 0),
            by_classification.get("PASS_EXCELLENT", 0),
            by_classification.get("PASS", 0)
        ])
        
        return {
            "total": total,
            "average_score": round(avg_score, 2),
            "by_classification": by_classification,
            "pass_count": pass_count,
            "pass_rate": round(pass_count / total * 100, 2),
            "new_formulas_discovered": len(self.new_formulas),
            "new_physics_discovered": len(self.new_physics),
            "lower_level_learning_flagged": len(self.lower_level_needed),
            "needs_foundational_review": len([e for e in entries if e.score <= 50])
        }


class EnhancedQuestionBank:
    """
    Question bank with 100 questions per level.
    10 difficulty levels × 10 questions = 100 questions per level.
    """
    
    def __init__(self):
        self.questions: Dict[Level, Dict[DifficultyLevel, List[EnhancedQuestion]]] = {}
        self._initialize_questions()
    
    def _initialize_questions(self):
        """Initialize 100 questions per level."""
        for level in Level:
            self.questions[level] = {}
            for diff in DifficultyLevel:
                self.questions[level][diff] = self._generate_questions_for_difficulty(level, diff)
    
    def _generate_questions_for_difficulty(self, level: Level, diff: DifficultyLevel) -> List[EnhancedQuestion]:
        """Generate 10 questions for a specific level and difficulty."""
        questions = []
        
        # Question templates based on level
        templates = self._get_question_templates(level, diff)
        
        for i, template in enumerate(templates[:10]):  # Ensure exactly 10
            q = EnhancedQuestion(
                question_id=f"{level.name[:2]}_D{diff.value}_Q{i+1}",
                level=level,
                difficulty=diff,
                topic=template.get("topic", f"Topic {i+1}"),
                question=template.get("question", f"Question {i+1} for {level.name} at difficulty {diff.value}"),
                requires_concepts=template.get("requires", []),
                hints=template.get("hints", []),
                solution_approach=template.get("solution", "Apply relevant concepts"),
                grading_criteria=template.get("criteria", {"correctness": 50, "reasoning": 30, "insight": 20}),
                expected_time_minutes=diff.value * 5  # Higher difficulty = more time
            )
            questions.append(q)
        
        return questions
    
    def _get_question_templates(self, level: Level, diff: DifficultyLevel) -> List[Dict]:
        """Get question templates for a level and difficulty."""
        
        # Base templates that scale with difficulty
        if level == Level.FOUNDATIONS:
            return self._foundations_templates(diff)
        elif level == Level.GEOMETRY_GROUPS:
            return self._geometry_templates(diff)
        elif level == Level.ANALYSIS_TOPOLOGY:
            return self._analysis_templates(diff)
        elif level == Level.FIELD_THEORY:
            return self._field_theory_templates(diff)
        elif level == Level.YANG_MILLS:
            return self._yang_mills_templates(diff)
        
        return [{}] * 10
    
    def _foundations_templates(self, diff: DifficultyLevel) -> List[Dict]:
        """Foundation level question templates."""
        base_topics = [
            ("Derivatives", "calculus", ["limits", "continuity"]),
            ("Integrals", "calculus", ["antiderivatives", "area"]),
            ("Vectors", "linear_algebra", ["vector_spaces", "basis"]),
            ("Matrices", "linear_algebra", ["eigenvalues", "transformations"]),
            ("Differential Equations", "ode", ["solutions", "stability"]),
            ("Lagrangian Mechanics", "mechanics", ["action", "euler_lagrange"]),
            ("Hamiltonian Mechanics", "mechanics", ["phase_space", "poisson_brackets"]),
            ("Symmetry", "physics", ["noether", "conservation"]),
            ("Vector Calculus", "calculus", ["gradient", "curl", "divergence"]),
            ("Complex Analysis", "analysis", ["holomorphic", "residues"])
        ]
        
        templates = []
        for topic, area, concepts in base_topics:
            difficulty_modifier = diff.value
            templates.append({
                "topic": topic,
                "question": self._scale_question(topic, area, diff),
                "requires": concepts,
                "hints": [f"Consider the {c} aspect" for c in concepts[:2]],
                "solution": f"Apply {topic} principles with {area} techniques",
                "criteria": {
                    "correctness": 40 + difficulty_modifier,
                    "reasoning": 30,
                    "insight": 30 - difficulty_modifier
                }
            })
        
        return templates
    
    def _geometry_templates(self, diff: DifficultyLevel) -> List[Dict]:
        """Geometry and Groups level question templates."""
        base_topics = [
            ("Manifolds", "differential_geometry", ["charts", "atlas"]),
            ("Tangent Spaces", "differential_geometry", ["vectors", "derivations"]),
            ("Differential Forms", "differential_geometry", ["exterior_derivative", "wedge"]),
            ("Lie Groups", "group_theory", ["matrix_groups", "exponential_map"]),
            ("Lie Algebras", "group_theory", ["commutators", "structure_constants"]),
            ("Fiber Bundles", "topology", ["sections", "connections"]),
            ("Connections", "differential_geometry", ["parallel_transport", "curvature"]),
            ("Curvature", "differential_geometry", ["riemann_tensor", "ricci"]),
            ("Gauge Transformations", "physics", ["local_symmetry", "covariant_derivative"]),
            ("Principal Bundles", "topology", ["structure_group", "associated_bundles"])
        ]
        
        templates = []
        for topic, area, concepts in base_topics:
            templates.append({
                "topic": topic,
                "question": self._scale_question(topic, area, diff),
                "requires": concepts,
                "hints": [f"Think about {c}" for c in concepts[:2]],
                "solution": f"Use {topic} theory",
                "criteria": {"correctness": 45, "reasoning": 35, "insight": 20}
            })
        
        return templates
    
    def _analysis_templates(self, diff: DifficultyLevel) -> List[Dict]:
        """Analysis and Topology level question templates."""
        base_topics = [
            ("Hilbert Spaces", "functional_analysis", ["inner_product", "completeness"]),
            ("Operators", "functional_analysis", ["bounded", "unbounded", "spectrum"]),
            ("Spectral Theory", "functional_analysis", ["eigenvalues", "spectral_theorem"]),
            ("Distributions", "analysis", ["test_functions", "weak_derivatives"]),
            ("Sobolev Spaces", "analysis", ["weak_solutions", "regularity"]),
            ("Homotopy", "topology", ["fundamental_group", "higher_homotopy"]),
            ("Homology", "topology", ["chains", "cycles", "boundaries"]),
            ("Cohomology", "topology", ["de_rham", "cech"]),
            ("Index Theory", "analysis", ["fredholm", "atiyah_singer"]),
            ("K-Theory", "topology", ["vector_bundles", "bott_periodicity"])
        ]
        
        templates = []
        for topic, area, concepts in base_topics:
            templates.append({
                "topic": topic,
                "question": self._scale_question(topic, area, diff),
                "requires": concepts,
                "hints": [f"Consider {c}" for c in concepts[:2]],
                "solution": f"Apply {topic} methods",
                "criteria": {"correctness": 40, "reasoning": 40, "insight": 20}
            })
        
        return templates
    
    def _field_theory_templates(self, diff: DifficultyLevel) -> List[Dict]:
        """Field Theory level question templates."""
        base_topics = [
            ("Path Integrals", "qft", ["functional_integration", "measure"]),
            ("Gauge Fields", "qft", ["yang_mills", "field_strength"]),
            ("Renormalization", "qft", ["divergences", "counterterms"]),
            ("Asymptotic Freedom", "qcd", ["beta_function", "running_coupling"]),
            ("Confinement", "qcd", ["wilson_loops", "string_tension"]),
            ("Instantons", "qft", ["tunneling", "topological_charge"]),
            ("Anomalies", "qft", ["chiral", "gauge_anomalies"]),
            ("BRST Symmetry", "qft", ["ghost_fields", "cohomology"]),
            ("Lattice QCD", "qcd", ["discretization", "continuum_limit"]),
            ("Non-Perturbative", "qft", ["strong_coupling", "dualities"])
        ]
        
        templates = []
        for topic, area, concepts in base_topics:
            templates.append({
                "topic": topic,
                "question": self._scale_question(topic, area, diff),
                "requires": concepts,
                "hints": [f"Use {c}" for c in concepts[:2]],
                "solution": f"Apply {topic} techniques",
                "criteria": {"correctness": 35, "reasoning": 40, "insight": 25}
            })
        
        return templates
    
    def _yang_mills_templates(self, diff: DifficultyLevel) -> List[Dict]:
        """Yang-Mills level question templates - the final challenge."""
        base_topics = [
            ("Mass Gap Definition", "millennium", ["spectrum", "gap"]),
            ("Existence Proof", "millennium", ["constructive", "axiomatic"]),
            ("Uniqueness", "millennium", ["vacuum", "ground_state"]),
            ("Regularity", "millennium", ["smoothness", "singularities"]),
            ("Gauge Fixing", "millennium", ["gribov", "faddeev_popov"]),
            ("Cluster Decomposition", "millennium", ["locality", "causality"]),
            ("Wightman Axioms", "millennium", ["qft_axioms", "reconstruction"]),
            ("Osterwalder-Schrader", "millennium", ["euclidean", "reflection_positivity"]),
            ("Constructive QFT", "millennium", ["rigorous", "mathematical"]),
            ("Novel Approaches", "millennium", ["new_methods", "breakthroughs"])
        ]
        
        templates = []
        for topic, area, concepts in base_topics:
            templates.append({
                "topic": topic,
                "question": self._scale_question(topic, area, diff),
                "requires": concepts,
                "hints": [f"Consider {c}" for c in concepts[:2]],
                "solution": f"This requires deep insight into {topic}",
                "criteria": {"correctness": 30, "reasoning": 35, "insight": 35}
            })
        
        return templates
    
    def _scale_question(self, topic: str, area: str, diff: DifficultyLevel) -> str:
        """Generate a question scaled to difficulty level."""
        
        difficulty_prefixes = {
            DifficultyLevel.D1_BASIC: "Define and explain",
            DifficultyLevel.D2_ELEMENTARY: "Describe the key properties of",
            DifficultyLevel.D3_INTERMEDIATE: "Prove a basic result about",
            DifficultyLevel.D4_MODERATE: "Derive the relationship between",
            DifficultyLevel.D5_CHALLENGING: "Analyze the implications of",
            DifficultyLevel.D6_ADVANCED: "Construct a novel example demonstrating",
            DifficultyLevel.D7_COMPLEX: "Prove a non-trivial theorem about",
            DifficultyLevel.D8_EXPERT: "Develop a new approach to understanding",
            DifficultyLevel.D9_MASTER: "Synthesize multiple concepts to solve",
            DifficultyLevel.D10_GENIUS: "Propose an original contribution to"
        }
        
        prefix = difficulty_prefixes.get(diff, "Explain")
        
        return f"{prefix} {topic} in the context of {area}. Show your complete reasoning and highlight any novel insights or connections to the Yang-Mills problem."
    
    def get_questions(self, level: Level, difficulty: DifficultyLevel = None) -> List[EnhancedQuestion]:
        """Get questions for a level, optionally filtered by difficulty."""
        if difficulty:
            return self.questions[level].get(difficulty, [])
        
        # Return all questions for the level
        all_questions = []
        for diff in DifficultyLevel:
            all_questions.extend(self.questions[level].get(diff, []))
        return all_questions
    
    def get_question_count(self, level: Level) -> int:
        """Get total question count for a level."""
        return sum(len(self.questions[level].get(d, [])) for d in DifficultyLevel)


class EnhancedStudyLibrary:
    """
    Enhanced study library with n-varieties of materials.
    Multiple approaches to each topic for deeper learning.
    """
    
    def __init__(self):
        self.materials: Dict[Level, List[StudyMaterialVariant]] = {}
        self._initialize_materials()
    
    def _initialize_materials(self):
        """Initialize study materials with multiple variants."""
        for level in Level:
            self.materials[level] = self._create_materials_for_level(level)
    
    def _create_materials_for_level(self, level: Level) -> List[StudyMaterialVariant]:
        """Create multiple variant materials for a level."""
        materials = []
        
        # Get topics for this level
        topics = self._get_topics_for_level(level)
        
        # Create 5 variants for each topic (different approaches)
        approaches = ["intuitive", "rigorous", "visual", "computational", "historical"]
        
        for topic_name, topic_content in topics:
            for approach in approaches:
                for diff in [DifficultyLevel.D1_BASIC, DifficultyLevel.D5_CHALLENGING, DifficultyLevel.D10_GENIUS]:
                    variant = StudyMaterialVariant(
                        variant_id=f"{level.name[:2]}_{topic_name[:10]}_{approach}_{diff.value}",
                        title=f"{topic_name} ({approach.title()} Approach, Level {diff.value})",
                        approach=approach,
                        content=self._generate_content(topic_name, topic_content, approach, diff),
                        difficulty=diff
                    )
                    materials.append(variant)
        
        return materials
    
    def _get_topics_for_level(self, level: Level) -> List[Tuple[str, Dict]]:
        """Get topics for a level."""
        topics_map = {
            Level.FOUNDATIONS: [
                ("Calculus", {"core": "derivatives, integrals, limits"}),
                ("Linear Algebra", {"core": "vectors, matrices, eigenvalues"}),
                ("Classical Mechanics", {"core": "Lagrangian, Hamiltonian, symmetry"}),
                ("Vector Calculus", {"core": "gradient, curl, divergence, Stokes"})
            ],
            Level.GEOMETRY_GROUPS: [
                ("Manifolds", {"core": "charts, atlas, smooth structures"}),
                ("Lie Groups", {"core": "matrix groups, exponential map"}),
                ("Fiber Bundles", {"core": "principal bundles, connections"}),
                ("Differential Forms", {"core": "exterior algebra, de Rham"})
            ],
            Level.ANALYSIS_TOPOLOGY: [
                ("Functional Analysis", {"core": "Hilbert spaces, operators"}),
                ("Spectral Theory", {"core": "spectrum, eigenvalues"}),
                ("Algebraic Topology", {"core": "homotopy, homology"}),
                ("Index Theory", {"core": "Atiyah-Singer, Fredholm"})
            ],
            Level.FIELD_THEORY: [
                ("Quantum Field Theory", {"core": "path integrals, renormalization"}),
                ("Gauge Theory", {"core": "Yang-Mills, gauge transformations"}),
                ("Non-Perturbative Methods", {"core": "instantons, lattice"}),
                ("QCD", {"core": "asymptotic freedom, confinement"})
            ],
            Level.YANG_MILLS: [
                ("The Millennium Problem", {"core": "mass gap, existence, uniqueness"}),
                ("Constructive QFT", {"core": "rigorous construction"}),
                ("Known Approaches", {"core": "lattice, functional methods"}),
                ("Open Questions", {"core": "what remains to be solved"})
            ]
        }
        
        return topics_map.get(level, [])
    
    def _generate_content(self, topic: str, base_content: Dict, approach: str, diff: DifficultyLevel) -> Dict:
        """Generate content for a specific approach and difficulty."""
        return {
            "topic": topic,
            "approach": approach,
            "difficulty": diff.name,
            "overview": f"A {approach} treatment of {topic} at difficulty level {diff.value}",
            "core_concepts": base_content.get("core", ""),
            "key_ideas": [
                f"Key idea 1 for {topic} ({approach})",
                f"Key idea 2 for {topic} ({approach})",
                f"Key idea 3 for {topic} ({approach})"
            ],
            "examples": [
                f"Example demonstrating {topic} using {approach} approach"
            ],
            "connections_to_yang_mills": f"How {topic} relates to the Yang-Mills problem",
            "exercises": [
                f"Practice problem for {topic} at difficulty {diff.value}"
            ]
        }
    
    def get_materials(self, level: Level, approach: str = None, difficulty: DifficultyLevel = None) -> List[StudyMaterialVariant]:
        """Get materials, optionally filtered by approach and difficulty."""
        materials = self.materials.get(level, [])
        
        if approach:
            materials = [m for m in materials if m.approach == approach]
        
        if difficulty:
            materials = [m for m in materials if m.difficulty == difficulty]
        
        return materials
    
    def get_additional_materials(self, level: Level, topic: str) -> List[StudyMaterialVariant]:
        """Get additional materials for a topic when framework needs more study."""
        return [m for m in self.materials.get(level, []) if topic.lower() in m.title.lower()]


class FrameworkProgress:
    """Track progress for a single framework."""
    
    def __init__(self, framework_name: str):
        self.framework_name = framework_name
        self.current_level = Level.FOUNDATIONS
        self.level_scores: Dict[Level, List[float]] = {level: [] for level in Level}
        self.passed_questions: Dict[Level, List[str]] = {level: [] for level in Level}
        self.failed_questions: Dict[Level, List[str]] = {level: [] for level in Level}
        self.study_materials_completed: Dict[Level, List[str]] = {level: [] for level in Level}
        self.needs_more_study: List[str] = []  # Topics needing more study
    
    def record_score(self, level: Level, question_id: str, score: float, passed: bool):
        """Record a score for a question."""
        self.level_scores[level].append(score)
        if passed:
            if question_id not in self.passed_questions[level]:
                self.passed_questions[level].append(question_id)
        else:
            if question_id not in self.failed_questions[level]:
                self.failed_questions[level].append(question_id)
    
    def get_level_pass_rate(self, level: Level) -> float:
        """Get the pass rate for a level (must be >75% to advance)."""
        total = len(self.passed_questions[level]) + len(self.failed_questions[level])
        if total == 0:
            return 0.0
        return len(self.passed_questions[level]) / total * 100
    
    def can_advance(self) -> bool:
        """Check if framework can advance to next level (>75% pass rate)."""
        pass_rate = self.get_level_pass_rate(self.current_level)
        return pass_rate >= 75.0
    
    def advance(self) -> bool:
        """Advance to next level if eligible."""
        if not self.can_advance():
            return False
        
        levels = list(Level)
        current_idx = levels.index(self.current_level)
        
        if current_idx < len(levels) - 1:
            self.current_level = levels[current_idx + 1]
            return True
        
        return False


class EnhancedLearningSystem:
    """
    The complete enhanced learning system.
    
    Features:
    - 100 questions per level (10 difficulties × 10 questions)
    - 90%+ to PASS individual questions
    - 75%+ overall to advance to next level
    - Comprehensive logging
    - Expanded study materials
    - Sequential unique thinking
    """
    
    def __init__(self):
        self.question_bank = EnhancedQuestionBank()
        self.study_library = EnhancedStudyLibrary()
        self.logger = ComprehensiveLogger()
        self.frameworks: Dict[str, FrameworkProgress] = {}
        
        print("=" * 60)
        print("ENHANCED LEARNING SYSTEM INITIALIZED")
        print("=" * 60)
        print(f"Questions per level: {self.question_bank.get_question_count(Level.FOUNDATIONS)}")
        print(f"Total questions: {sum(self.question_bank.get_question_count(l) for l in Level)}")
        print(f"Study material variants: {sum(len(self.study_library.materials[l]) for l in Level)}")
        print(f"Pass threshold: 90%+")
        print(f"Advance threshold: 75%+ pass rate")
        print("=" * 60)
    
    def register_framework(self, name: str):
        """Register a framework for learning."""
        self.frameworks[name] = FrameworkProgress(name)
        print(f"✓ Registered {name} (starting at Level 1: FOUNDATIONS)")
    
    def get_study_materials(self, framework: str, approach: str = None) -> List[Dict]:
        """Get study materials for a framework's current level."""
        if framework not in self.frameworks:
            return []
        
        progress = self.frameworks[framework]
        materials = self.study_library.get_materials(progress.current_level, approach)
        
        return [
            {
                "variant_id": m.variant_id,
                "title": m.title,
                "approach": m.approach,
                "difficulty": m.difficulty.name,
                "content": m.content
            }
            for m in materials
        ]
    
    def get_questions(self, framework: str, difficulty: DifficultyLevel = None) -> List[Dict]:
        """Get questions for a framework's current level."""
        if framework not in self.frameworks:
            return []
        
        progress = self.frameworks[framework]
        questions = self.question_bank.get_questions(progress.current_level, difficulty)
        
        return [
            {
                "question_id": q.question_id,
                "difficulty": q.difficulty.name,
                "topic": q.topic,
                "question": q.question,
                "requires_concepts": q.requires_concepts,
                "hints": q.hints,
                "expected_time": q.expected_time_minutes
            }
            for q in questions
        ]
    
    def record_result(self, framework: str, question_id: str, score: float, 
                      answer: str, feedback: str,
                      is_new_formula: bool = False, new_formula_details: str = None,
                      is_new_physics: bool = False, new_physics_details: str = None,
                      key_insights: List[str] = None):
        """Record a result with comprehensive logging."""
        if framework not in self.frameworks:
            return
        
        progress = self.frameworks[framework]
        classification = self.logger.classify_score(score)
        passed = score >= 90  # 90%+ to pass
        
        # Record in progress
        progress.record_score(progress.current_level, question_id, score, passed)
        
        # Create log entry
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            framework=framework,
            level=progress.current_level,
            question_id=question_id,
            score=score,
            classification=classification,
            answer=answer,
            feedback=feedback,
            is_new_formula=is_new_formula,
            new_formula_details=new_formula_details,
            is_new_physics=is_new_physics,
            new_physics_details=new_physics_details,
            key_insights=key_insights or []
        )
        
        # Log it
        self.logger.log_result(entry)
        
        return {
            "passed": passed,
            "classification": classification.value,
            "can_advance": progress.can_advance(),
            "level_pass_rate": progress.get_level_pass_rate(progress.current_level)
        }
    
    def check_advancement(self, framework: str) -> Dict:
        """Check if a framework can advance."""
        if framework not in self.frameworks:
            return {"can_advance": False}
        
        progress = self.frameworks[framework]
        pass_rate = progress.get_level_pass_rate(progress.current_level)
        
        return {
            "framework": framework,
            "current_level": progress.current_level.name,
            "pass_rate": pass_rate,
            "required_rate": 75.0,
            "can_advance": pass_rate >= 75.0,
            "questions_passed": len(progress.passed_questions[progress.current_level]),
            "questions_failed": len(progress.failed_questions[progress.current_level])
        }
    
    def advance_framework(self, framework: str) -> Dict:
        """Advance a framework to the next level."""
        if framework not in self.frameworks:
            return {"success": False, "message": "Framework not found"}
        
        progress = self.frameworks[framework]
        old_level = progress.current_level
        
        if progress.advance():
            return {
                "success": True,
                "message": f"{framework} advanced from {old_level.name} to {progress.current_level.name}!",
                "old_level": old_level.name,
                "new_level": progress.current_level.name
            }
        else:
            return {
                "success": False,
                "message": f"Cannot advance. Pass rate: {progress.get_level_pass_rate(old_level):.1f}% (need 75%+)",
                "current_level": old_level.name
            }
    
    def get_statistics(self) -> Dict:
        """Get overall statistics."""
        return {
            "logger_stats": self.logger.get_statistics(),
            "frameworks": {
                name: {
                    "current_level": p.current_level.name,
                    "pass_rate": p.get_level_pass_rate(p.current_level),
                    "can_advance": p.can_advance()
                }
                for name, p in self.frameworks.items()
            }
        }


# Singleton instance
_enhanced_system = None

def get_enhanced_learning_system() -> EnhancedLearningSystem:
    """Get the singleton enhanced learning system."""
    global _enhanced_system
    if _enhanced_system is None:
        _enhanced_system = EnhancedLearningSystem()
    return _enhanced_system
