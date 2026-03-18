#!/usr/bin/env python3.11
"""
AETHER Adaptive Learning Journey

Features:
- Monitors for improvement
- Automatically extends study materials when no improvement detected
- Continues until advancement or intervention needed
- Comprehensive logging with detailed percentage breakdown
"""

import sys
import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

sys.path.append('/home/ubuntu/aether/core')

from enhanced_learning_system import (
    get_enhanced_learning_system, Level, DifficultyLevel, 
    ScoreClassification, EnhancedLearningSystem
)
from sequential_thinker import get_thinking_manager, SequentialThinker

# Try to import OpenAI
try:
    from openai import OpenAI
    client = OpenAI()
    AI_AVAILABLE = True
    print("✓ OpenAI API available")
except:
    AI_AVAILABLE = False
    client = None
    print("⚠ OpenAI API not available - using simulated mode")


@dataclass
class ImprovementTracker:
    """Track improvement over time for a framework."""
    framework: str
    score_history: List[float] = field(default_factory=list)
    rolling_average: float = 0.0
    improvement_detected: bool = True
    stagnation_count: int = 0
    materials_extended: int = 0
    
    def add_score(self, score: float) -> bool:
        """Add a score and check for improvement."""
        self.score_history.append(score)
        
        # Need at least 5 scores to detect stagnation
        if len(self.score_history) < 5:
            return True
        
        # Calculate rolling averages
        recent_avg = sum(self.score_history[-5:]) / 5
        previous_avg = sum(self.score_history[-10:-5]) / 5 if len(self.score_history) >= 10 else recent_avg
        
        # Check for improvement (at least 2% increase)
        if recent_avg > previous_avg + 2:
            self.improvement_detected = True
            self.stagnation_count = 0
        elif recent_avg < previous_avg - 5:
            # Significant drop
            self.improvement_detected = False
            self.stagnation_count += 1
        else:
            # Stagnation
            self.stagnation_count += 1
            if self.stagnation_count >= 3:
                self.improvement_detected = False
        
        self.rolling_average = recent_avg
        return self.improvement_detected
    
    def needs_more_materials(self) -> bool:
        """Check if framework needs extended materials."""
        return not self.improvement_detected and self.stagnation_count >= 3


class AdaptiveGrader:
    """Grader with detailed percentage breakdown."""
    
    def __init__(self, model: str = "gpt-4.1-nano"):
        self.model = model
    
    def grade(self, question: Dict, answer: str, framework: str) -> Dict:
        """Grade with detailed breakdown."""
        
        if not AI_AVAILABLE:
            return self._simulated_grade(question, answer, framework)
        
        grading_prompt = f"""Grade this answer rigorously on a 0-100 scale.

QUESTION: {question.get('question', '')}
DIFFICULTY: {question.get('difficulty', '')}

ANSWER:
{answer[:2500]}

Score breakdown:
- CORRECTNESS (0-40): Mathematical/physical accuracy
- REASONING (0-30): Clarity and completeness of logic
- INSIGHT (0-20): Depth of understanding shown
- NOVELTY (0-10): Original contributions or connections

Provide:
CORRECTNESS: [0-40]
REASONING: [0-30]
INSIGHT: [0-20]
NOVELTY: [0-10]
TOTAL: [sum, 0-100]
FEEDBACK: [brief constructive feedback]
NEW_FORMULA: Yes/No
NEW_PHYSICS: Yes/No
"""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a rigorous academic grader. 90%+ is passing."},
                    {"role": "user", "content": grading_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            grading = response.choices[0].message.content
            return self._parse_grading(grading, framework, question)
            
        except Exception as e:
            return {"framework": framework, "score": 50, "error": str(e)}
    
    def _parse_grading(self, grading: str, framework: str, question: Dict) -> Dict:
        """Parse grading response."""
        result = {"framework": framework, "question_id": question.get('question_id', '')}
        
        # Extract total score
        total_match = re.search(r'TOTAL:\s*(\d+)', grading)
        result['score'] = int(total_match.group(1)) if total_match else 50
        result['passed'] = result['score'] >= 90
        
        # Extract component scores
        for component in ['CORRECTNESS', 'REASONING', 'INSIGHT', 'NOVELTY']:
            match = re.search(rf'{component}:\s*(\d+)', grading)
            result[component.lower()] = int(match.group(1)) if match else 0
        
        # Check for discoveries
        result['is_new_formula'] = 'NEW_FORMULA: Yes' in grading
        result['is_new_physics'] = 'NEW_PHYSICS: Yes' in grading
        
        # Extract feedback
        feedback_match = re.search(r'FEEDBACK:\s*(.+?)(?=NEW_|$)', grading, re.DOTALL)
        result['feedback'] = feedback_match.group(1).strip() if feedback_match else "No feedback"
        
        return result
    
    def _simulated_grade(self, question: Dict, answer: str, framework: str) -> Dict:
        """Simulated grading."""
        import random
        
        diff_name = question.get('difficulty', 'D5')
        diff_num = int(diff_name.split('_')[0][1:]) if '_' in diff_name else 5
        
        # Base score decreases with difficulty
        base = 90 - (diff_num * 4)
        score = max(30, min(100, base + random.randint(-10, 15)))
        
        return {
            "framework": framework,
            "question_id": question.get('question_id', ''),
            "score": score,
            "passed": score >= 90,
            "correctness": int(score * 0.4),
            "reasoning": int(score * 0.3),
            "insight": int(score * 0.2),
            "novelty": int(score * 0.1),
            "is_new_formula": random.random() < 0.05,
            "is_new_physics": random.random() < 0.03,
            "feedback": f"Simulated grade: {score}"
        }


def generate_extended_materials(framework: str, level: Level, weak_areas: List[str]) -> List[Dict]:
    """Generate additional study materials for weak areas."""
    
    extended = []
    
    # Base materials for each area
    material_templates = {
        "correctness": {
            "title": f"Precision in {level.name} - Extended Practice",
            "content": {
                "focus": "Mathematical rigor and accuracy",
                "exercises": [
                    "Verify each step of your derivations",
                    "Check boundary conditions and special cases",
                    "Ensure dimensional consistency"
                ],
                "common_errors": [
                    "Sign errors in gauge transformations",
                    "Missing factors in path integrals",
                    "Incorrect index contractions"
                ]
            }
        },
        "reasoning": {
            "title": f"Logical Structure in {level.name} - Extended",
            "content": {
                "focus": "Clear logical flow",
                "techniques": [
                    "State assumptions explicitly",
                    "Show each logical step",
                    "Connect conclusions to premises"
                ],
                "practice": [
                    "Write proofs in both directions",
                    "Identify necessary vs sufficient conditions",
                    "Practice proof by contradiction"
                ]
            }
        },
        "insight": {
            "title": f"Deep Understanding of {level.name} - Extended",
            "content": {
                "focus": "Conceptual depth",
                "approaches": [
                    "Ask 'why' at each step",
                    "Connect to physical intuition",
                    "Find multiple perspectives on same concept"
                ],
                "exercises": [
                    "Explain concepts without equations",
                    "Draw diagrams and visualizations",
                    "Find analogies in other fields"
                ]
            }
        },
        "novelty": {
            "title": f"Creative Thinking in {level.name} - Extended",
            "content": {
                "focus": "Original contributions",
                "techniques": [
                    "Combine ideas from different areas",
                    "Question standard approaches",
                    "Look for patterns and generalizations"
                ],
                "prompts": [
                    "What if this assumption were relaxed?",
                    "How would this look in a different context?",
                    "What's the simplest non-trivial example?"
                ]
            }
        }
    }
    
    for area in weak_areas:
        if area in material_templates:
            material = material_templates[area].copy()
            material['framework'] = framework
            material['level'] = level.name
            material['generated'] = datetime.now().isoformat()
            extended.append(material)
    
    return extended


def run_adaptive_journey(max_rounds: int = 5, questions_per_round: int = 10):
    """
    Run adaptive learning journey.
    
    - Monitors improvement
    - Extends materials when stagnation detected
    - Continues until advancement or max rounds
    """
    
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*12 + "AETHER ADAPTIVE LEARNING JOURNEY" + " "*21 + "║")
    print("║" + " "*8 + "Auto-Extends Materials When No Improvement" + " "*17 + "║")
    print("╚" + "="*68 + "╝")
    
    # Initialize systems
    learning_system = get_enhanced_learning_system()
    thinking_manager = get_thinking_manager()
    grader = AdaptiveGrader()
    
    # Create frameworks
    frameworks = {
        "Stratify": {
            "specialty": "theoretical physics, gauge theory",
            "thinker": thinking_manager.create_thinker("Stratify", "theoretical physics"),
            "tracker": ImprovementTracker("Stratify")
        },
        "Principia": {
            "specialty": "mathematical foundations, rigorous proofs",
            "thinker": thinking_manager.create_thinker("Principia", "mathematical foundations"),
            "tracker": ImprovementTracker("Principia")
        }
    }
    
    for name in frameworks:
        learning_system.register_framework(name)
    
    print(f"\n  Frameworks: {', '.join(frameworks.keys())}")
    print(f"  Max rounds: {max_rounds}")
    print(f"  Questions per round: {questions_per_round}")
    print(f"  Pass threshold: 90%+")
    print(f"  Advance threshold: 75%+ pass rate")
    
    # Run rounds
    for round_num in range(1, max_rounds + 1):
        print(f"\n{'#'*70}")
        print(f"#  ROUND {round_num} / {max_rounds}")
        print(f"{'#'*70}")
        
        for framework_name, framework_data in frameworks.items():
            print(f"\n{'='*60}")
            print(f"  {framework_name} - Round {round_num}")
            print(f"{'='*60}")
            
            thinker = framework_data['thinker']
            tracker = framework_data['tracker']
            
            # Check if needs extended materials
            if tracker.needs_more_materials():
                print(f"\n  ⚠️ STAGNATION DETECTED - Extending study materials...")
                
                # Identify weak areas from recent scores
                weak_areas = []
                if tracker.rolling_average < 70:
                    weak_areas.extend(['correctness', 'reasoning'])
                if tracker.rolling_average < 80:
                    weak_areas.append('insight')
                weak_areas.append('novelty')
                
                # Generate extended materials
                extended = generate_extended_materials(
                    framework_name, 
                    Level.FOUNDATIONS, 
                    weak_areas
                )
                
                print(f"  📚 Added {len(extended)} extended materials")
                tracker.materials_extended += len(extended)
                
                # Study extended materials
                for material in extended:
                    print(f"    Studying: {material['title']}...")
                    chain = thinker.study_sequentially(material)
                    print(f"    ✓ Completed")
                
                tracker.stagnation_count = 0  # Reset after intervention
            
            # Get questions for this round
            questions = []
            for diff in list(DifficultyLevel)[:5]:
                qs = learning_system.get_questions(framework_name, diff)
                questions.extend(qs[:2])  # 2 per difficulty = 10 total
            
            questions = questions[:questions_per_round]
            
            # Test
            round_scores = []
            round_passed = 0
            
            print(f"\n  🧪 Testing ({len(questions)} questions)...")
            
            for q in questions:
                # Attempt
                attempt = thinker.attempt_sequentially(q)
                
                # Grade
                grade = grader.grade(q, attempt['answer'], framework_name)
                score = grade['score']
                
                # Record
                learning_system.record_result(
                    framework_name,
                    q['question_id'],
                    score,
                    attempt['answer'],
                    grade.get('feedback', ''),
                    is_new_formula=grade.get('is_new_formula', False),
                    is_new_physics=grade.get('is_new_physics', False)
                )
                
                # Track
                round_scores.append(score)
                tracker.add_score(score)
                
                if grade['passed']:
                    round_passed += 1
                    status = "✓"
                elif score <= 50:
                    status = "🔻"
                else:
                    status = "○"
                
                # Get classification
                classification = learning_system.logger.classify_score(score)
                print(f"    {q['question_id']}: {score}% ({classification.value}) {status}")
            
            # Round summary
            avg_score = sum(round_scores) / len(round_scores) if round_scores else 0
            pass_rate = (round_passed / len(questions) * 100) if questions else 0
            
            print(f"\n  📊 Round Summary:")
            print(f"     Average: {avg_score:.1f}%")
            print(f"     Passed: {round_passed}/{len(questions)} ({pass_rate:.1f}%)")
            print(f"     Rolling avg: {tracker.rolling_average:.1f}%")
            print(f"     Improving: {'Yes' if tracker.improvement_detected else 'No'}")
            print(f"     Materials extended: {tracker.materials_extended}")
            
            # Check advancement
            advancement = learning_system.check_advancement(framework_name)
            if advancement['can_advance']:
                print(f"\n  🎉 {framework_name} CAN ADVANCE TO LEVEL 2!")
    
    # Final summary
    print("\n" + "="*70)
    print("  FINAL SUMMARY")
    print("="*70)
    
    stats = learning_system.get_statistics()
    logger_stats = stats['logger_stats']
    
    print(f"\n  Total questions answered: {logger_stats['total']}")
    print(f"  Overall average: {logger_stats['average_score']}%")
    print(f"  Overall pass rate: {logger_stats['pass_rate']}%")
    print(f"  Lower level flags: {logger_stats['lower_level_learning_flagged']}")
    print(f"  New formulas: {logger_stats['new_formulas_discovered']}")
    print(f"  New physics: {logger_stats['new_physics_discovered']}")
    
    print("\n  By Classification:")
    for cls, count in logger_stats['by_classification'].items():
        print(f"    {cls}: {count}")
    
    print("\n  Framework Status:")
    for name, data in frameworks.items():
        tracker = data['tracker']
        print(f"    {name}:")
        print(f"      Questions: {len(tracker.score_history)}")
        print(f"      Rolling avg: {tracker.rolling_average:.1f}%")
        print(f"      Materials extended: {tracker.materials_extended}")
    
    # Log files
    print("\n  📁 Log Files:")
    log_dir = "/home/ubuntu/aether/logs"
    for f in sorted(os.listdir(log_dir)):
        if f.endswith('.jsonl'):
            path = os.path.join(log_dir, f)
            lines = sum(1 for _ in open(path))
            print(f"    {f}: {lines} entries")
    
    return learning_system, frameworks


if __name__ == "__main__":
    run_adaptive_journey(max_rounds=5, questions_per_round=10)
