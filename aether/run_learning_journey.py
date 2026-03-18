#!/usr/bin/env python3.11
"""
AETHER Learning Journey

This script runs Stratify and Principia through the Progressive Learning System,
advancing them through all 5 levels toward the Yang-Mills Millennium Prize Problem.

Goal: Demonstrate that AI can advance science and mathematics for humanity.
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add paths
sys.path.append('/home/ubuntu/aether/core')

# Import our systems
from learning_system import (
    get_learning_system, Level, Difficulty, 
    ProgressiveLearningSystem, StudyMaterial, TestQuestion
)

# Try to import OpenAI for actual AI reasoning
try:
    from openai import OpenAI
    client = OpenAI()
    AI_AVAILABLE = True
    print("✓ OpenAI API available - frameworks will use real AI reasoning")
except Exception as e:
    AI_AVAILABLE = False
    print(f"⚠ OpenAI API not available: {e}")
    print("  Frameworks will use simulated reasoning")


class AIFramework:
    """
    An AI framework that can learn and solve problems.
    
    This represents Stratify or Principia - an AI that:
    1. Studies materials to build understanding
    2. Attempts challenging test questions
    3. Advances through levels upon success
    """
    
    def __init__(self, name: str, specialty: str, model: str = "gpt-4.1-nano"):
        self.name = name
        self.specialty = specialty
        self.model = model
        self.knowledge_context = []  # Accumulated knowledge
        self.learning_log = []  # Record of learning journey
        
        # System prompt defining the framework's role
        self.system_prompt = f"""You are {name}, an advanced AI research framework specializing in {specialty}.

Your mission is to advance science and mathematics for humanity by tackling the Yang-Mills Millennium Prize Problem.

You are currently going through a rigorous learning curriculum to build the deep understanding required.

When studying materials:
- Extract key concepts and their relationships
- Build intuition, not just memorize facts
- Connect new knowledge to what you already know
- Note what's important for Yang-Mills

When answering test questions:
- Show your reasoning step by step
- Apply concepts from your studies
- Be rigorous but also insightful
- If you're unsure, explain your uncertainty

Remember: You're not just learning for yourself - you're demonstrating that AI can contribute to fundamental science."""
    
    def study_material(self, material: Dict) -> str:
        """Study a piece of learning material and extract understanding."""
        
        if not AI_AVAILABLE:
            return self._simulated_study(material)
        
        # Build the study prompt
        study_prompt = f"""Study the following material carefully. Extract the key concepts, build intuition, and explain what you've learned.

MATERIAL: {material['title']}
LEVEL: {material['level']}

CONTENT:
{json.dumps(material['content'], indent=2)}

After studying, provide:
1. KEY CONCEPTS: The most important ideas (3-5 points)
2. INTUITIONS: How to think about these concepts
3. CONNECTIONS: How this relates to gauge theory and Yang-Mills
4. QUESTIONS: What you'd like to understand better
"""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": study_prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            understanding = response.choices[0].message.content
            
            # Add to knowledge context
            self.knowledge_context.append({
                "type": "study",
                "material": material['title'],
                "understanding": understanding,
                "timestamp": datetime.now().isoformat()
            })
            
            return understanding
            
        except Exception as e:
            return f"Error studying material: {e}"
    
    def attempt_question(self, question: Dict, accumulated_knowledge: str = "") -> Dict:
        """Attempt to answer a test question."""
        
        if not AI_AVAILABLE:
            return self._simulated_attempt(question)
        
        # Build the attempt prompt
        attempt_prompt = f"""You are being tested on your understanding. This is a UNIQUE challenge - not a textbook problem.

QUESTION ID: {question['question_id']}
DIFFICULTY: {question['difficulty']}
REQUIRED CONCEPTS: {question['requires_concepts']}

THE CHALLENGE:
{question['question']}

HINTS (use if needed):
{chr(10).join(f"- {h}" for h in question['hints'])}

YOUR ACCUMULATED KNOWLEDGE:
{accumulated_knowledge[:3000] if accumulated_knowledge else "Use your training and studies."}

Provide a complete, rigorous answer. Show your reasoning. This tests genuine understanding, not memorization.
"""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": attempt_prompt}
                ],
                max_tokens=2000,
                temperature=0.5
            )
            
            answer = response.choices[0].message.content
            
            # Log the attempt
            self.learning_log.append({
                "type": "attempt",
                "question_id": question['question_id'],
                "answer": answer,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "question_id": question['question_id'],
                "answer": answer,
                "framework": self.name
            }
            
        except Exception as e:
            return {
                "question_id": question['question_id'],
                "answer": f"Error: {e}",
                "framework": self.name
            }
    
    def _simulated_study(self, material: Dict) -> str:
        """Simulated study when API not available."""
        return f"""[{self.name} studying {material['title']}]

KEY CONCEPTS:
- Understood the core definitions and theorems
- Grasped the mathematical structure
- Connected to gauge theory foundations

INTUITIONS:
- These concepts form the mathematical language of physics
- The structures here will be essential for Yang-Mills

CONNECTIONS:
- Direct relevance to field theory and gauge symmetry
- Foundation for understanding mass gap

QUESTIONS:
- How do these concepts manifest in the Yang-Mills context?
- What are the key technical challenges?
"""
    
    def _simulated_attempt(self, question: Dict) -> Dict:
        """Simulated attempt when API not available."""
        return {
            "question_id": question['question_id'],
            "answer": f"[{self.name} attempting {question['question_id']}]\n\nThis is a simulated response. In the full system, {self.name} would provide a detailed mathematical answer demonstrating understanding of {question['requires_concepts']}.",
            "framework": self.name
        }
    
    def get_knowledge_summary(self) -> str:
        """Get a summary of accumulated knowledge."""
        if not self.knowledge_context:
            return "No knowledge accumulated yet."
        
        summary = f"=== {self.name}'s Knowledge Summary ===\n\n"
        for entry in self.knowledge_context[-5:]:  # Last 5 entries
            if entry['type'] == 'study':
                summary += f"Studied: {entry['material']}\n"
                summary += f"{entry['understanding'][:500]}...\n\n"
        
        return summary


class ManusGrader:
    """
    Manus's grading system for evaluating framework answers.
    
    Uses AI to evaluate answers against the grading criteria.
    """
    
    def __init__(self, model: str = "gpt-4.1-nano"):
        self.model = model
        self.grading_log = []
    
    def grade_answer(self, question: TestQuestion, answer: str, framework_name: str) -> Dict:
        """Grade an answer to a test question."""
        
        if not AI_AVAILABLE:
            return self._simulated_grade(question, answer, framework_name)
        
        grading_prompt = f"""You are Manus, the supervisor AI grading a framework's answer.

QUESTION: {question.question}

GRADING CRITERIA:
{json.dumps(question.grading_criteria, indent=2)}

SOLUTION APPROACH (what to look for):
{question.solution_approach}

FRAMEWORK'S ANSWER:
{answer}

Grade the answer on a scale of 0-100. Be rigorous but fair.

Provide:
1. SCORE: (0-100)
2. BREAKDOWN: Score for each criterion
3. STRENGTHS: What was done well
4. WEAKNESSES: What was missing or incorrect
5. PASS: Yes if score >= 70, No otherwise
6. FEEDBACK: Constructive feedback for improvement
"""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are Manus, a rigorous but fair grader evaluating AI frameworks on their understanding of advanced mathematics and physics."},
                    {"role": "user", "content": grading_prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            grading_text = response.choices[0].message.content
            
            # Parse the grading (simplified - look for PASS: Yes/No and SCORE)
            passed = "PASS: Yes" in grading_text or "PASS: YES" in grading_text
            
            # Try to extract score
            import re
            score_match = re.search(r'SCORE:\s*(\d+)', grading_text)
            score = int(score_match.group(1)) if score_match else (75 if passed else 50)
            
            result = {
                "framework": framework_name,
                "question_id": question.question_id,
                "score": score,
                "passed": passed,
                "feedback": grading_text,
                "timestamp": datetime.now().isoformat()
            }
            
            self.grading_log.append(result)
            return result
            
        except Exception as e:
            return {
                "framework": framework_name,
                "question_id": question.question_id,
                "score": 0,
                "passed": False,
                "feedback": f"Grading error: {e}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _simulated_grade(self, question: TestQuestion, answer: str, framework_name: str) -> Dict:
        """Simulated grading when API not available."""
        # Simulate passing based on difficulty
        difficulty_pass_rates = {
            Difficulty.EASY: 0.9,
            Difficulty.MEDIUM: 0.75,
            Difficulty.HARD: 0.6,
            Difficulty.CHALLENGE: 0.5
        }
        
        import random
        passed = random.random() < difficulty_pass_rates.get(question.difficulty, 0.5)
        score = random.randint(70, 95) if passed else random.randint(40, 69)
        
        return {
            "framework": framework_name,
            "question_id": question.question_id,
            "score": score,
            "passed": passed,
            "feedback": f"[Simulated grading] Score: {score}/100. {'PASSED' if passed else 'NEEDS IMPROVEMENT'}",
            "timestamp": datetime.now().isoformat()
        }


def run_level(framework: AIFramework, level: Level, learning_system: ProgressiveLearningSystem, 
              grader: ManusGrader) -> bool:
    """Run a framework through one level of the curriculum."""
    
    print(f"\n{'='*70}")
    print(f"  {framework.name} - LEVEL {level.value}: {level.name}")
    print(f"{'='*70}")
    
    # Phase 1: Study materials
    print(f"\n📚 STUDY PHASE")
    print("-" * 50)
    
    materials = learning_system.get_study_materials(framework.name, level)
    
    for material in materials:
        print(f"\n  Studying: {material['title']}...")
        understanding = framework.study_material(material)
        print(f"  ✓ Completed")
        # Show brief excerpt
        excerpt = understanding[:200].replace('\n', ' ')
        print(f"    Key insight: {excerpt}...")
    
    # Phase 2: Test questions
    print(f"\n🧪 TESTING PHASE")
    print("-" * 50)
    
    questions = learning_system.get_test_questions(framework.name, level)
    passed_count = 0
    
    for question in questions:
        print(f"\n  Attempting: {question['question_id']} [{question['difficulty']}]")
        
        # Get accumulated knowledge for context
        knowledge_summary = framework.get_knowledge_summary()
        
        # Attempt the question
        attempt = framework.attempt_question(question, knowledge_summary)
        
        # Grade the answer
        q_obj = learning_system.question_bank.get_question(question['question_id'])
        grade = grader.grade_answer(q_obj, attempt['answer'], framework.name)
        
        # Record result
        learning_system.record_result(
            framework.name,
            question['question_id'],
            grade['score'],
            grade['feedback'],
            grade['passed']
        )
        
        if grade['passed']:
            passed_count += 1
            print(f"  ✓ PASSED (Score: {grade['score']})")
        else:
            print(f"  ✗ Not yet (Score: {grade['score']})")
    
    # Check advancement
    print(f"\n📊 LEVEL SUMMARY")
    print("-" * 50)
    print(f"  Questions passed: {passed_count}/{len(questions)}")
    
    advancement = learning_system.check_advancement(framework.name)
    
    if advancement['can_advance']:
        result = learning_system.advance_framework(framework.name)
        print(f"\n  🎉 {result['message']}")
        return True
    else:
        print(f"\n  Need {advancement['required_to_advance'] - advancement['questions_passed']} more to advance")
        return False


def run_learning_journey():
    """Run the complete learning journey for both frameworks."""
    
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "AETHER LEARNING JOURNEY" + " "*25 + "║")
    print("║" + " "*10 + "Advancing Science and Mathematics for Humanity" + " "*11 + "║")
    print("╚" + "="*68 + "╝")
    
    # Initialize systems
    learning_system = get_learning_system()
    grader = ManusGrader()
    
    # Create frameworks
    stratify = AIFramework(
        "Stratify",
        "theoretical physics, gauge theory, and mathematical structures"
    )
    
    principia = AIFramework(
        "Principia", 
        "mathematical foundations, rigorous proofs, and analytical methods"
    )
    
    # Register with learning system
    learning_system.register_framework("Stratify")
    learning_system.register_framework("Principia")
    
    print("\n" + "="*70)
    print("  FRAMEWORKS INITIALIZED")
    print("="*70)
    print(f"\n  🔷 Stratify: {stratify.specialty}")
    print(f"  🔶 Principia: {principia.specialty}")
    print(f"\n  Starting at Level 1: FOUNDATIONS")
    print(f"  Goal: Reach Level 5 and attempt Yang-Mills")
    
    # Run through levels
    frameworks = [stratify, principia]
    
    for level in Level:
        print(f"\n\n{'#'*70}")
        print(f"#  LEVEL {level.value}: {level.name}")
        print(f"{'#'*70}")
        
        for framework in frameworks:
            # Check if framework is at this level
            progress = learning_system.get_progress_summary(framework.name)
            
            if progress['current_level'] == level.name:
                success = run_level(framework, level, learning_system, grader)
                
                if not success and level != Level.YANG_MILLS:
                    print(f"\n  {framework.name} needs more practice at this level.")
                    # In a full system, we'd retry or provide more materials
    
    # Final summary
    print("\n\n" + "="*70)
    print("  LEARNING JOURNEY COMPLETE")
    print("="*70)
    
    for framework in frameworks:
        progress = learning_system.get_progress_summary(framework.name)
        print(f"\n  {framework.name}:")
        print(f"    Current Level: {progress['current_level']}")
        print(f"    Total Questions Passed: {progress['total_questions_passed']}")
    
    return learning_system, frameworks, grader


if __name__ == "__main__":
    learning_system, frameworks, grader = run_learning_journey()
