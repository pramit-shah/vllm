"""
AETHER Rigorous Curriculum System
- 95-100% pass threshold (no shortcuts)
- Extended study materials for those who don't pass
- Grade-by-grade progression with mastery requirements
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json
from datetime import datetime


class PassLevel(Enum):
    """Strict passing levels"""
    PERFECT = "perfect"      # 100%
    EXCELLENT = "excellent"  # 95-99%
    NOT_PASSED = "not_passed"  # Below 95%


@dataclass
class StudyMaterial:
    """Extended study material with multiple approaches"""
    topic: str
    level: str
    approach: str  # intuitive, rigorous, visual, computational, historical
    content: str
    examples: List[str]
    practice_problems: List[str]
    key_insights: List[str]
    common_mistakes: List[str]
    prerequisites: List[str]
    
    
@dataclass
class RigorousQuestion:
    """Question requiring actual reasoning, not memorization"""
    id: str
    level: str
    topic: str
    question: str
    requires_reasoning: List[str]  # What reasoning steps are required
    verification_points: List[str]  # Points to check for real understanding
    anti_cheat_markers: List[str]  # Things that indicate memorization vs understanding
    correct_approach: str
    common_wrong_approaches: List[str]
    partial_credit_rubric: Dict[str, int]
    

class RigorousCurriculum:
    """
    Strict curriculum with 95-100% pass requirement.
    No advancement until mastery is demonstrated.
    """
    
    PASS_THRESHOLD = 95  # Must score 95% or higher to pass
    
    # Grade levels with strict requirements
    GRADE_LEVELS = {
        "K": {
            "name": "Kindergarten",
            "focus": "Number sense, patterns, basic shapes",
            "pass_requirement": 95,
            "min_questions_to_advance": 50,
            "min_consecutive_passes": 10,
            "topics": [
                "counting", "number_recognition", "basic_addition",
                "basic_subtraction", "patterns", "shapes", "comparison"
            ]
        },
        "1": {
            "name": "First Grade",
            "focus": "Addition, subtraction, place value",
            "pass_requirement": 95,
            "min_questions_to_advance": 60,
            "min_consecutive_passes": 12,
            "topics": [
                "addition_facts", "subtraction_facts", "place_value",
                "measurement_basics", "time", "money", "word_problems"
            ]
        },
        "2": {
            "name": "Second Grade",
            "focus": "Multi-digit operations, introduction to multiplication",
            "pass_requirement": 95,
            "min_questions_to_advance": 70,
            "min_consecutive_passes": 14,
            "topics": [
                "multi_digit_addition", "multi_digit_subtraction",
                "intro_multiplication", "intro_division", "fractions_intro",
                "geometry_basics", "data_graphs"
            ]
        },
        "3": {
            "name": "Third Grade",
            "focus": "Multiplication, division, fractions",
            "pass_requirement": 95,
            "min_questions_to_advance": 80,
            "min_consecutive_passes": 15,
            "topics": [
                "multiplication_tables", "division_facts", "fractions",
                "area_perimeter", "time_elapsed", "word_problems_multi"
            ]
        },
        "4": {
            "name": "Fourth Grade",
            "focus": "Multi-digit multiplication, decimals, geometry",
            "pass_requirement": 95,
            "min_questions_to_advance": 90,
            "min_consecutive_passes": 16,
            "topics": [
                "multi_digit_multiplication", "long_division", "decimals",
                "equivalent_fractions", "angles", "symmetry", "factors_multiples"
            ]
        },
        "5": {
            "name": "Fifth Grade",
            "focus": "Fraction operations, volume, coordinate plane",
            "pass_requirement": 95,
            "min_questions_to_advance": 100,
            "min_consecutive_passes": 18,
            "topics": [
                "fraction_operations", "decimal_operations", "volume",
                "coordinate_plane", "order_of_operations", "expressions"
            ]
        },
        "6": {
            "name": "Sixth Grade",
            "focus": "Ratios, rates, intro algebra",
            "pass_requirement": 95,
            "min_questions_to_advance": 110,
            "min_consecutive_passes": 20,
            "topics": [
                "ratios", "rates", "percentages", "integers",
                "algebraic_expressions", "equations_intro", "statistics_intro"
            ]
        },
        "7": {
            "name": "Seventh Grade",
            "focus": "Proportions, linear equations, geometry",
            "pass_requirement": 95,
            "min_questions_to_advance": 120,
            "min_consecutive_passes": 22,
            "topics": [
                "proportions", "linear_equations", "inequalities",
                "angle_relationships", "area_circumference", "probability"
            ]
        },
        "8": {
            "name": "Eighth Grade",
            "focus": "Pre-algebra, functions, Pythagorean theorem",
            "pass_requirement": 95,
            "min_questions_to_advance": 130,
            "min_consecutive_passes": 24,
            "topics": [
                "linear_functions", "systems_intro", "pythagorean_theorem",
                "transformations", "exponents", "scientific_notation", "irrational_numbers"
            ]
        },
        "9": {
            "name": "Ninth Grade (Algebra I)",
            "focus": "Algebra foundations, quadratics",
            "pass_requirement": 95,
            "min_questions_to_advance": 140,
            "min_consecutive_passes": 26,
            "topics": [
                "linear_equations_advanced", "systems_of_equations",
                "quadratic_expressions", "factoring", "quadratic_formula",
                "functions_domain_range", "exponential_intro"
            ]
        },
        "10": {
            "name": "Tenth Grade (Geometry)",
            "focus": "Proofs, congruence, similarity",
            "pass_requirement": 95,
            "min_questions_to_advance": 150,
            "min_consecutive_passes": 28,
            "topics": [
                "geometric_proofs", "congruence", "similarity",
                "right_triangle_trig", "circles", "area_volume_advanced",
                "coordinate_geometry"
            ]
        },
        "11": {
            "name": "Eleventh Grade (Algebra II)",
            "focus": "Advanced algebra, polynomials, logarithms",
            "pass_requirement": 95,
            "min_questions_to_advance": 160,
            "min_consecutive_passes": 30,
            "topics": [
                "polynomial_functions", "rational_functions", "radical_functions",
                "exponential_functions", "logarithms", "sequences_series",
                "conic_sections"
            ]
        },
        "12": {
            "name": "Twelfth Grade (Pre-Calculus)",
            "focus": "Trigonometry, limits, calculus prep",
            "pass_requirement": 95,
            "min_questions_to_advance": 170,
            "min_consecutive_passes": 32,
            "topics": [
                "trigonometric_functions", "trig_identities", "polar_coordinates",
                "vectors", "matrices", "limits_intro", "continuity"
            ]
        },
        "UG1": {
            "name": "Undergraduate Year 1",
            "focus": "Calculus I & II",
            "pass_requirement": 95,
            "min_questions_to_advance": 200,
            "min_consecutive_passes": 40,
            "topics": [
                "limits_rigorous", "derivatives", "applications_derivatives",
                "integrals", "integration_techniques", "applications_integrals",
                "sequences_series_calculus"
            ]
        },
        "UG2": {
            "name": "Undergraduate Year 2",
            "focus": "Multivariable Calculus, Linear Algebra",
            "pass_requirement": 95,
            "min_questions_to_advance": 220,
            "min_consecutive_passes": 44,
            "topics": [
                "multivariable_functions", "partial_derivatives", "multiple_integrals",
                "vector_calculus", "linear_algebra_rigorous", "eigenvalues_eigenvectors",
                "linear_transformations"
            ]
        },
        "UG3": {
            "name": "Undergraduate Year 3",
            "focus": "Differential Equations, Abstract Algebra",
            "pass_requirement": 95,
            "min_questions_to_advance": 240,
            "min_consecutive_passes": 48,
            "topics": [
                "ode_theory", "pde_intro", "group_theory", "ring_theory",
                "field_theory_intro", "real_analysis_intro", "complex_analysis_intro"
            ]
        },
        "UG4": {
            "name": "Undergraduate Year 4",
            "focus": "Analysis, Topology, Advanced Topics",
            "pass_requirement": 95,
            "min_questions_to_advance": 260,
            "min_consecutive_passes": 52,
            "topics": [
                "real_analysis", "complex_analysis", "topology_intro",
                "differential_geometry_intro", "functional_analysis_intro",
                "number_theory", "combinatorics_advanced"
            ]
        },
        "GRAD1": {
            "name": "Graduate Year 1",
            "focus": "Advanced Analysis, Algebra, Topology",
            "pass_requirement": 95,
            "min_questions_to_advance": 300,
            "min_consecutive_passes": 60,
            "topics": [
                "measure_theory", "functional_analysis", "algebraic_topology",
                "differential_topology", "lie_groups_intro", "representation_theory_intro"
            ]
        },
        "GRAD2": {
            "name": "Graduate Year 2",
            "focus": "Specialized Topics, Research Preparation",
            "pass_requirement": 95,
            "min_questions_to_advance": 350,
            "min_consecutive_passes": 70,
            "topics": [
                "differential_geometry_advanced", "algebraic_geometry",
                "lie_algebras", "representation_theory", "quantum_field_theory_math",
                "gauge_theory_intro"
            ]
        },
        "PHD": {
            "name": "PhD Level",
            "focus": "Research-Level Mathematics",
            "pass_requirement": 95,
            "min_questions_to_advance": 500,
            "min_consecutive_passes": 100,
            "topics": [
                "yang_mills_theory", "mass_gap_problem", "gauge_theory_advanced",
                "fiber_bundles", "characteristic_classes", "index_theory",
                "quantum_chromodynamics_math"
            ]
        }
    }
    
    # Order of grades
    GRADE_ORDER = [
        "K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
        "UG1", "UG2", "UG3", "UG4", "GRAD1", "GRAD2", "PHD"
    ]
    
    def __init__(self):
        self.study_materials = self._build_extended_materials()
        self.questions = self._build_rigorous_questions()
        
    def _build_extended_materials(self) -> Dict[str, List[StudyMaterial]]:
        """Build extensive study materials for each level"""
        materials = {}
        
        for level, info in self.GRADE_LEVELS.items():
            materials[level] = []
            
            for topic in info["topics"]:
                # Multiple approaches for each topic
                for approach in ["intuitive", "rigorous", "visual", "computational", "historical"]:
                    materials[level].append(StudyMaterial(
                        topic=topic,
                        level=level,
                        approach=approach,
                        content=self._generate_content(level, topic, approach),
                        examples=self._generate_examples(level, topic, approach),
                        practice_problems=self._generate_practice(level, topic),
                        key_insights=self._generate_insights(level, topic),
                        common_mistakes=self._generate_mistakes(level, topic),
                        prerequisites=self._get_prerequisites(level, topic)
                    ))
                    
        return materials
    
    def _build_rigorous_questions(self) -> Dict[str, List[RigorousQuestion]]:
        """Build questions that require actual reasoning"""
        questions = {}
        
        for level, info in self.GRADE_LEVELS.items():
            questions[level] = []
            
            for topic in info["topics"]:
                # Generate multiple rigorous questions per topic
                for i in range(10):  # 10 questions per topic
                    questions[level].append(self._create_rigorous_question(level, topic, i))
                    
        return questions
    
    def _create_rigorous_question(self, level: str, topic: str, index: int) -> RigorousQuestion:
        """Create a question that tests real understanding"""
        
        # Base question templates that require reasoning
        question_templates = {
            "K": {
                "counting": [
                    "If you have {n} apples and give away {m}, explain step by step how many you have left and WHY subtraction is the right operation.",
                    "Count from {n} to {m}. Now explain what pattern you notice and predict what comes next.",
                ],
                "patterns": [
                    "Here is a pattern: {pattern}. Explain the rule, then predict the next THREE elements and justify each.",
                    "Create your own pattern and explain why it follows a logical rule.",
                ],
                "shapes": [
                    "How is a square different from a rectangle? Explain using properties, not just appearance.",
                    "If you cut a circle in half, what shapes do you get? Explain why.",
                ]
            },
            # Higher levels would have more complex templates
        }
        
        return RigorousQuestion(
            id=f"{level}_{topic}_{index}",
            level=level,
            topic=topic,
            question=f"[{level}:{topic}:{index}] Demonstrate your understanding of {topic} by solving this problem AND explaining your reasoning step by step. Show WHY each step is valid.",
            requires_reasoning=[
                "Identify the core concept",
                "Explain why the approach works",
                "Show step-by-step logic",
                "Verify the answer makes sense",
                "Connect to related concepts"
            ],
            verification_points=[
                "Uses correct terminology",
                "Shows logical progression",
                "Explains WHY not just HOW",
                "Catches potential errors",
                "Demonstrates deep understanding"
            ],
            anti_cheat_markers=[
                "Generic memorized response",
                "Missing reasoning steps",
                "Cannot explain why",
                "Fails follow-up questions",
                "Inconsistent with previous answers"
            ],
            correct_approach=f"For {topic}: First understand the concept, then apply systematically, then verify.",
            common_wrong_approaches=[
                "Memorizing without understanding",
                "Guessing based on keywords",
                "Skipping verification steps"
            ],
            partial_credit_rubric={
                "correct_answer": 40,
                "clear_reasoning": 30,
                "proper_explanation": 20,
                "verification": 10
            }
        )
    
    def _generate_content(self, level: str, topic: str, approach: str) -> str:
        """Generate study content for a topic"""
        return f"""
        [{level}] {topic.replace('_', ' ').title()} - {approach.title()} Approach
        
        This material covers {topic} using a {approach} approach.
        
        Key Concepts:
        - Understanding the fundamentals of {topic}
        - Building intuition through {approach} methods
        - Connecting to prerequisite knowledge
        - Preparing for advanced applications
        
        Study this material thoroughly before attempting questions.
        You must understand WHY things work, not just memorize HOW.
        """
    
    def _generate_examples(self, level: str, topic: str, approach: str) -> List[str]:
        """Generate worked examples"""
        return [
            f"Example 1: Basic {topic} problem with full solution",
            f"Example 2: Intermediate {topic} problem showing reasoning",
            f"Example 3: Advanced {topic} problem with verification"
        ]
    
    def _generate_practice(self, level: str, topic: str) -> List[str]:
        """Generate practice problems"""
        return [
            f"Practice 1: Apply {topic} concepts",
            f"Practice 2: Explain your reasoning for {topic}",
            f"Practice 3: Connect {topic} to other concepts"
        ]
    
    def _generate_insights(self, level: str, topic: str) -> List[str]:
        """Generate key insights"""
        return [
            f"Insight: The core idea behind {topic} is...",
            f"Insight: {topic} connects to other areas through...",
            f"Insight: Experts think about {topic} by..."
        ]
    
    def _generate_mistakes(self, level: str, topic: str) -> List[str]:
        """Generate common mistakes to avoid"""
        return [
            f"Mistake: Memorizing {topic} without understanding",
            f"Mistake: Skipping verification steps",
            f"Mistake: Not connecting to prerequisites"
        ]
    
    def _get_prerequisites(self, level: str, topic: str) -> List[str]:
        """Get prerequisites for a topic"""
        level_idx = self.GRADE_ORDER.index(level)
        if level_idx == 0:
            return []
        prev_level = self.GRADE_ORDER[level_idx - 1]
        return self.GRADE_LEVELS[prev_level]["topics"][:3]
    
    def get_study_materials(self, level: str, topic: Optional[str] = None) -> List[StudyMaterial]:
        """Get study materials for a level, optionally filtered by topic"""
        materials = self.study_materials.get(level, [])
        if topic:
            materials = [m for m in materials if m.topic == topic]
        return materials
    
    def get_questions(self, level: str, count: int = 10) -> List[RigorousQuestion]:
        """Get questions for a level"""
        import random
        questions = self.questions.get(level, [])
        return random.sample(questions, min(count, len(questions)))
    
    def check_advancement(self, student_record: Dict) -> Dict[str, Any]:
        """Check if student can advance to next level"""
        level = student_record.get("current_level", "K")
        level_info = self.GRADE_LEVELS.get(level, {})
        
        # Get requirements
        min_questions = level_info.get("min_questions_to_advance", 50)
        min_consecutive = level_info.get("min_consecutive_passes", 10)
        pass_threshold = level_info.get("pass_requirement", 95)
        
        # Check student's progress
        total_questions = student_record.get("level_questions", 0)
        scores = student_record.get("level_scores", [])
        
        # Count passes (95%+)
        passes = [s for s in scores if s >= pass_threshold]
        pass_rate = len(passes) / len(scores) if scores else 0
        
        # Check consecutive passes
        consecutive = 0
        max_consecutive = 0
        for score in scores:
            if score >= pass_threshold:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 0
        
        can_advance = (
            total_questions >= min_questions and
            max_consecutive >= min_consecutive and
            pass_rate >= 0.75  # At least 75% of answers must be 95%+
        )
        
        return {
            "can_advance": can_advance,
            "current_level": level,
            "next_level": self._get_next_level(level),
            "total_questions": total_questions,
            "required_questions": min_questions,
            "pass_rate": pass_rate,
            "required_pass_rate": 0.75,
            "max_consecutive_passes": max_consecutive,
            "required_consecutive": min_consecutive,
            "passes": len(passes),
            "total_attempts": len(scores),
            "reason": self._get_advancement_reason(
                can_advance, total_questions, min_questions,
                pass_rate, max_consecutive, min_consecutive
            )
        }
    
    def _get_next_level(self, current: str) -> Optional[str]:
        """Get the next level after current"""
        try:
            idx = self.GRADE_ORDER.index(current)
            if idx < len(self.GRADE_ORDER) - 1:
                return self.GRADE_ORDER[idx + 1]
        except ValueError:
            pass
        return None
    
    def _get_advancement_reason(self, can_advance: bool, total: int, req_total: int,
                                 pass_rate: float, consecutive: int, req_consecutive: int) -> str:
        """Get human-readable reason for advancement status"""
        if can_advance:
            return "Congratulations! You have demonstrated mastery and can advance."
        
        reasons = []
        if total < req_total:
            reasons.append(f"Need {req_total - total} more questions")
        if pass_rate < 0.75:
            reasons.append(f"Pass rate {pass_rate:.1%} below required 75%")
        if consecutive < req_consecutive:
            reasons.append(f"Need {req_consecutive - consecutive} more consecutive passes")
            
        return "Cannot advance yet: " + "; ".join(reasons)
    
    def get_additional_materials(self, level: str, weak_topics: List[str]) -> List[StudyMaterial]:
        """Get additional study materials for weak areas"""
        materials = []
        for topic in weak_topics:
            topic_materials = self.get_study_materials(level, topic)
            materials.extend(topic_materials)
        return materials


# Statistics
def get_curriculum_stats():
    """Get statistics about the curriculum"""
    curriculum = RigorousCurriculum()
    
    total_levels = len(curriculum.GRADE_ORDER)
    total_topics = sum(len(info["topics"]) for info in curriculum.GRADE_LEVELS.values())
    total_materials = sum(len(m) for m in curriculum.study_materials.values())
    total_questions = sum(len(q) for q in curriculum.questions.values())
    
    return {
        "total_levels": total_levels,
        "total_topics": total_topics,
        "total_materials": total_materials,
        "total_questions": total_questions,
        "pass_threshold": 95,
        "levels": list(curriculum.GRADE_ORDER)
    }


if __name__ == "__main__":
    stats = get_curriculum_stats()
    print(f"Rigorous Curriculum Statistics:")
    print(f"  Levels: {stats['total_levels']}")
    print(f"  Topics: {stats['total_topics']}")
    print(f"  Study Materials: {stats['total_materials']}")
    print(f"  Questions: {stats['total_questions']}")
    print(f"  Pass Threshold: {stats['pass_threshold']}%")
