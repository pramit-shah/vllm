#!/usr/bin/env python3.11
"""
AETHER Enhanced Learning Journey

Features:
- 100 questions per level (10 difficulties × 10 questions)
- 90%+ to PASS individual questions
- 75%+ overall to advance to next level
- Comprehensive logging of all scores
- Lower level learning flag for 0-50%
- New formula/physics discovery tracking
- Sequential unique thinking for each framework
- Cannot advance until threshold met
"""

import sys
import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any

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


class EnhancedGrader:
    """
    Enhanced grader with rigorous standards.
    
    - 90%+ to PASS
    - Detects new formulas and physics
    - Extracts key insights
    """
    
    def __init__(self, model: str = "gpt-4.1-nano"):
        self.model = model
    
    def grade(self, question: Dict, answer: str, framework: str) -> Dict:
        """Grade an answer with enhanced criteria."""
        
        if not AI_AVAILABLE:
            return self._simulated_grade(question, answer, framework)
        
        grading_prompt = f"""Grade this answer rigorously. Pass threshold is 90%.

QUESTION: {question.get('question', '')}
DIFFICULTY: {question.get('difficulty', '')}
EXPECTED CONCEPTS: {question.get('requires_concepts', [])}

ANSWER:
{answer[:3000]}

Grade on:
1. CORRECTNESS (0-40): Is the answer mathematically/physically correct?
2. REASONING (0-30): Is the reasoning clear and complete?
3. INSIGHT (0-20): Does it show deep understanding?
4. NOVELTY (0-10): Any original contributions?

Also identify:
- NEW_FORMULA: Yes/No - Did they derive something new?
- NEW_PHYSICS: Yes/No - Did they discover new physical insight?
- KEY_INSIGHTS: List any important observations
- FOUNDATIONAL_GAPS: List any basic concepts they're missing

Format:
CORRECTNESS: [score]
REASONING: [score]
INSIGHT: [score]
NOVELTY: [score]
TOTAL: [sum]
PASS: Yes/No (Yes if total >= 90)
NEW_FORMULA: Yes/No
FORMULA_DETAILS: [if yes, describe]
NEW_PHYSICS: Yes/No
PHYSICS_DETAILS: [if yes, describe]
KEY_INSIGHTS: [list]
FOUNDATIONAL_GAPS: [list]
FEEDBACK: [constructive feedback]
"""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a rigorous academic grader. Be fair but demanding. 90% is the pass threshold."},
                    {"role": "user", "content": grading_prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            grading = response.choices[0].message.content
            return self._parse_grading(grading, framework, question)
            
        except Exception as e:
            return {
                "framework": framework,
                "question_id": question.get('question_id', ''),
                "score": 0,
                "passed": False,
                "error": str(e)
            }
    
    def _parse_grading(self, grading: str, framework: str, question: Dict) -> Dict:
        """Parse grading response."""
        result = {
            "framework": framework,
            "question_id": question.get('question_id', ''),
            "raw_grading": grading
        }
        
        # Extract total score
        total_match = re.search(r'TOTAL:\s*(\d+)', grading)
        result['score'] = int(total_match.group(1)) if total_match else 50
        
        # Check pass
        result['passed'] = result['score'] >= 90
        
        # Check for new formula
        result['is_new_formula'] = 'NEW_FORMULA: Yes' in grading
        if result['is_new_formula']:
            formula_match = re.search(r'FORMULA_DETAILS:\s*(.+?)(?=\n|$)', grading)
            result['formula_details'] = formula_match.group(1).strip() if formula_match else None
        
        # Check for new physics
        result['is_new_physics'] = 'NEW_PHYSICS: Yes' in grading
        if result['is_new_physics']:
            physics_match = re.search(r'PHYSICS_DETAILS:\s*(.+?)(?=\n|$)', grading)
            result['physics_details'] = physics_match.group(1).strip() if physics_match else None
        
        # Extract key insights
        insights_match = re.search(r'KEY_INSIGHTS:\s*(.+?)(?=FOUNDATIONAL|FEEDBACK|$)', grading, re.DOTALL)
        if insights_match:
            result['key_insights'] = [i.strip() for i in insights_match.group(1).split(',') if i.strip()]
        else:
            result['key_insights'] = []
        
        # Extract foundational gaps
        gaps_match = re.search(r'FOUNDATIONAL_GAPS:\s*(.+?)(?=FEEDBACK|$)', grading, re.DOTALL)
        if gaps_match:
            result['foundational_gaps'] = [g.strip() for g in gaps_match.group(1).split(',') if g.strip()]
        else:
            result['foundational_gaps'] = []
        
        # Extract feedback
        feedback_match = re.search(r'FEEDBACK:\s*(.+?)$', grading, re.DOTALL)
        result['feedback'] = feedback_match.group(1).strip() if feedback_match else "No feedback"
        
        # Flag lower level learning
        result['needs_lower_level'] = result['score'] <= 50
        
        return result
    
    def _simulated_grade(self, question: Dict, answer: str, framework: str) -> Dict:
        """Simulated grading."""
        import random
        
        # Simulate scores based on difficulty
        diff_name = question.get('difficulty', 'D5_CHALLENGING')
        diff_num = int(diff_name.split('_')[0][1:]) if '_' in diff_name else 5
        
        # Higher difficulty = lower expected score
        base_score = 95 - (diff_num * 5)
        score = max(20, min(100, base_score + random.randint(-15, 15)))
        
        return {
            "framework": framework,
            "question_id": question.get('question_id', ''),
            "score": score,
            "passed": score >= 90,
            "is_new_formula": random.random() < 0.05,  # 5% chance
            "is_new_physics": random.random() < 0.03,  # 3% chance
            "key_insights": ["Simulated insight"],
            "foundational_gaps": [] if score > 50 else ["Needs review"],
            "feedback": f"Simulated grade: {score}",
            "needs_lower_level": score <= 50
        }


def run_enhanced_journey(max_questions_per_difficulty: int = 2):
    """
    Run the enhanced learning journey.
    
    Args:
        max_questions_per_difficulty: Limit questions per difficulty for testing
    """
    
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "AETHER ENHANCED LEARNING JOURNEY" + " "*18 + "║")
    print("║" + " "*10 + "Rigorous Standards • Sequential Thinking" + " "*17 + "║")
    print("╚" + "="*68 + "╝")
    
    # Initialize systems
    learning_system = get_enhanced_learning_system()
    thinking_manager = get_thinking_manager()
    grader = EnhancedGrader()
    
    # Create frameworks with sequential thinkers
    frameworks = {
        "Stratify": {
            "specialty": "theoretical physics, gauge theory, mathematical structures",
            "thinker": thinking_manager.create_thinker(
                "Stratify", 
                "theoretical physics, gauge theory, mathematical structures"
            )
        },
        "Principia": {
            "specialty": "mathematical foundations, rigorous proofs, analytical methods",
            "thinker": thinking_manager.create_thinker(
                "Principia",
                "mathematical foundations, rigorous proofs, analytical methods"
            )
        }
    }
    
    # Register with learning system
    for name in frameworks:
        learning_system.register_framework(name)
    
    print("\n" + "="*70)
    print("  FRAMEWORKS INITIALIZED WITH SEQUENTIAL THINKING")
    print("="*70)
    for name, data in frameworks.items():
        print(f"  • {name}: {data['specialty']}")
    
    print(f"\n  Standards:")
    print(f"    - Pass threshold: 90%+")
    print(f"    - Advance threshold: 75%+ pass rate")
    print(f"    - Lower level flag: 0-50%")
    print(f"    - Questions per level: 100 (testing with {max_questions_per_difficulty} per difficulty)")
    
    # Run Level 1 for both frameworks
    print("\n" + "#"*70)
    print("#  LEVEL 1: FOUNDATIONS")
    print("#"*70)
    
    for framework_name, framework_data in frameworks.items():
        print(f"\n{'='*70}")
        print(f"  {framework_name} - LEVEL 1: FOUNDATIONS")
        print(f"{'='*70}")
        
        thinker = framework_data['thinker']
        
        # STUDY PHASE
        print(f"\n📚 STUDY PHASE (Sequential Thinking)")
        print("-" * 50)
        
        # Get study materials (limit for testing)
        materials = learning_system.get_study_materials(framework_name, approach="intuitive")[:3]
        
        for material in materials:
            print(f"\n  Studying: {material['title']}...")
            chain = thinker.study_sequentially(material)
            print(f"  ✓ Completed ({len(chain.thoughts)} thoughts)")
            if chain.conclusions:
                print(f"    Conclusion: {chain.conclusions[0][:80]}...")
            if chain.new_insights:
                print(f"    💡 New insight: {chain.new_insights[0][:60]}...")
            if chain.potential_formulas:
                print(f"    🔬 Potential formula: {chain.potential_formulas[0][:60]}...")
        
        # TESTING PHASE
        print(f"\n🧪 TESTING PHASE (Sequential Thinking)")
        print("-" * 50)
        
        results_summary = {
            "total": 0,
            "passed": 0,
            "lower_level_flagged": 0,
            "new_formulas": 0,
            "new_physics": 0
        }
        
        # Test across difficulties (limited for demo)
        for diff in list(DifficultyLevel)[:5]:  # First 5 difficulties
            questions = learning_system.get_questions(framework_name, diff)[:max_questions_per_difficulty]
            
            print(f"\n  Difficulty: {diff.name}")
            
            for q in questions:
                # Attempt with sequential thinking
                attempt = thinker.attempt_sequentially(q)
                
                # Grade
                grade = grader.grade(q, attempt['answer'], framework_name)
                
                # Record result
                learning_system.record_result(
                    framework_name,
                    q['question_id'],
                    grade['score'],
                    attempt['answer'],
                    grade.get('feedback', ''),
                    is_new_formula=grade.get('is_new_formula', False),
                    new_formula_details=grade.get('formula_details'),
                    is_new_physics=grade.get('is_new_physics', False),
                    new_physics_details=grade.get('physics_details'),
                    key_insights=grade.get('key_insights', [])
                )
                
                # Update summary
                results_summary['total'] += 1
                if grade['passed']:
                    results_summary['passed'] += 1
                    status = "✓ PASS"
                elif grade['score'] <= 50:
                    results_summary['lower_level_flagged'] += 1
                    status = "🔻 LOWER LEVEL"
                else:
                    status = "○ Not yet"
                
                if grade.get('is_new_formula'):
                    results_summary['new_formulas'] += 1
                    status += " 🔬"
                if grade.get('is_new_physics'):
                    results_summary['new_physics'] += 1
                    status += " ⚛️"
                
                print(f"    {q['question_id']}: Score {grade['score']} {status}")
        
        # Level summary
        print(f"\n📊 {framework_name} LEVEL SUMMARY")
        print("-" * 50)
        print(f"  Total questions: {results_summary['total']}")
        print(f"  Passed (90%+): {results_summary['passed']}")
        pass_rate = (results_summary['passed'] / results_summary['total'] * 100) if results_summary['total'] > 0 else 0
        print(f"  Pass rate: {pass_rate:.1f}%")
        print(f"  Lower level flagged: {results_summary['lower_level_flagged']}")
        print(f"  New formulas discovered: {results_summary['new_formulas']}")
        print(f"  New physics discovered: {results_summary['new_physics']}")
        
        # Check advancement
        advancement = learning_system.check_advancement(framework_name)
        if advancement['can_advance']:
            print(f"\n  🎉 CAN ADVANCE to Level 2!")
        else:
            print(f"\n  ⏳ Need {75 - advancement['pass_rate']:.1f}% more to advance")
        
        # Knowledge summary
        print(f"\n📝 {framework_name} KNOWLEDGE SUMMARY")
        print("-" * 50)
        print(thinker.get_knowledge_summary())
    
    # Overall statistics
    print("\n" + "="*70)
    print("  OVERALL STATISTICS")
    print("="*70)
    
    stats = learning_system.get_statistics()
    logger_stats = stats['logger_stats']
    
    print(f"\n  Total entries logged: {logger_stats['total']}")
    print(f"  Average score: {logger_stats['average_score']}")
    print(f"  Overall pass rate: {logger_stats['pass_rate']}%")
    print(f"  Lower level learning flagged: {logger_stats['lower_level_learning_flagged']}")
    print(f"  New formulas discovered: {logger_stats['new_formulas_discovered']}")
    print(f"  New physics discovered: {logger_stats['new_physics_discovered']}")
    
    # Combined insights
    combined = thinking_manager.get_combined_insights()
    print(f"\n  Total unique insights: {combined['total_insights']}")
    print(f"  Potential discoveries: {len(combined['potential_discoveries'])}")
    
    # Show log files
    print("\n📁 LOG FILES CREATED")
    print("-" * 50)
    log_dir = "/home/ubuntu/aether/logs"
    for f in sorted(os.listdir(log_dir)):
        if f.endswith('.jsonl'):
            path = os.path.join(log_dir, f)
            lines = sum(1 for _ in open(path))
            print(f"  {f}: {lines} entries")
    
    return learning_system, thinking_manager, grader


if __name__ == "__main__":
    # Run with limited questions for testing
    run_enhanced_journey(max_questions_per_difficulty=2)
