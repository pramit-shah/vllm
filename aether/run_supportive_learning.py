#!/usr/bin/env python3.11
"""
AETHER Supportive Learning Journey

A hands-on, encouraging approach to teaching AI frameworks.
No carrot and stick - just patient, supportive guidance.
"""

import sys
import os
import json
from datetime import datetime

sys.path.append('/home/ubuntu/aether/core')

from supportive_teacher import get_supportive_teacher, TrainingConfig
from sequential_thinker import get_thinking_manager

# Try to import OpenAI
try:
    from openai import OpenAI
    client = OpenAI()
    AI_AVAILABLE = True
    print("✓ OpenAI API available")
except:
    AI_AVAILABLE = False
    client = None
    print("⚠ Using simulated mode")


def print_header():
    """Print a friendly header."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*14 + "AETHER SUPPORTIVE LEARNING" + " "*26 + "║")
    print("║" + " "*10 + "A Hands-On, Encouraging Approach" + " "*24 + "║")
    print("╚" + "="*68 + "╝")


def print_encouragement(category: str, score: float):
    """Print encouraging feedback based on score."""
    if category == "excellent":
        print(f"    🌟 Outstanding! Score: {score}%")
    elif category == "good":
        print(f"    ✨ Great work! Score: {score}%")
    elif category == "developing":
        print(f"    📈 Good progress! Score: {score}%")
    elif category == "emerging":
        print(f"    🌱 Keep growing! Score: {score}%")
    else:
        print(f"    🌿 Building foundations! Score: {score}%")


def run_supportive_session(rounds: int = 3, questions_per_round: int = 5):
    """
    Run a supportive learning session.
    
    Features:
    - Worked examples before questions
    - Hints available
    - Multiple attempts allowed
    - Encouraging feedback
    - Gradual difficulty progression
    """
    
    print_header()
    
    # Initialize
    teacher = get_supportive_teacher()
    thinking_manager = get_thinking_manager()
    config = teacher.config
    
    print("\n📋 Training Configuration:")
    print(f"   Teaching style: {config.get('teaching_style', default='hands_on')}")
    print(f"   Starting level: {config.get('difficulty', 'starting_level', default=1)}")
    print(f"   Advancement threshold: {config.get('difficulty', 'advancement_threshold', default=60)}%")
    print(f"   Hints enabled: {config.get('support', 'hints_enabled', default=True)}")
    print(f"   Multiple attempts: {config.get('support', 'multiple_attempts', default=True)}")
    
    # Topics for Level 1 (Foundations) - Very basic
    level_1_topics = [
        "basic arithmetic and numbers",
        "simple algebra concepts",
        "introduction to functions",
        "basic geometry shapes",
        "simple word problems"
    ]
    
    # Create frameworks
    frameworks = {
        "Stratify": {
            "specialty": "pattern recognition and connections",
            "thinker": thinking_manager.create_thinker("Stratify", "finding patterns")
        },
        "Principia": {
            "specialty": "logical reasoning and proofs",
            "thinker": thinking_manager.create_thinker("Principia", "logical thinking")
        }
    }
    
    # Register learners
    print("\n👋 Welcoming learners...")
    for name in frameworks:
        teacher.register_learner(name)
    
    # Run learning rounds
    for round_num in range(1, rounds + 1):
        print(f"\n{'='*60}")
        print(f"  ROUND {round_num}: Learning Together")
        print(f"{'='*60}")
        
        for framework_name, framework_data in frameworks.items():
            learner = teacher.get_learner(framework_name)
            thinker = framework_data['thinker']
            
            print(f"\n  📚 {framework_name}'s Turn")
            print(f"     Current level: {learner.current_level}")
            print(f"     Questions answered: {learner.total_questions}")
            if learner.scores:
                print(f"     Average score: {sum(learner.scores)/len(learner.scores):.1f}%")
            
            # Check if needs extra support
            support = teacher.provide_support_if_struggling(learner)
            if support:
                print(f"\n     💪 {support['message']}")
                for suggestion in support['suggestions'][:2]:
                    print(f"        • {suggestion}")
            
            # Select topic based on level
            topic_idx = (learner.current_level - 1) % len(level_1_topics)
            topic = level_1_topics[topic_idx]
            
            # Provide worked example first
            if config.get("support", "examples_before_questions", default=True):
                print(f"\n     📖 Let me show you an example first...")
                example = teacher.provide_worked_example(topic, learner.current_level)
                
                # Study the example
                chain = thinker.study_sequentially({
                    "title": f"Worked Example: {topic}",
                    "content": example
                })
                print(f"        ✓ Example studied ({len(chain.thoughts)} thoughts)")
            
            # Ask questions
            for q_num in range(1, questions_per_round + 1):
                print(f"\n     ❓ Question {q_num}/{questions_per_round}")
                
                # Create supportive question
                question = teacher.create_supportive_question(topic, learner.current_level, learner)
                print(f"        Topic: {topic}")
                print(f"        Level: {question.get('level', 1)}/10")
                
                # Allow multiple attempts
                max_attempts = question.get("attempts_allowed", 3)
                best_score = 0
                
                for attempt in range(1, max_attempts + 1):
                    # Get answer using sequential thinking
                    attempt_result = thinker.attempt_sequentially({
                        "question_id": question.get("question_id", "Q"),
                        "question": question.get("content", ""),
                        "hints": question.get("hints", []) if attempt > 1 else []  # Show hints after first attempt
                    })
                    
                    # Evaluate with support
                    evaluation = teacher.evaluate_with_support(
                        question, 
                        attempt_result.get("answer", ""),
                        learner,
                        attempt
                    )
                    
                    score = evaluation["score"]
                    best_score = max(best_score, score)
                    
                    # Print encouraging feedback
                    print_encouragement(evaluation["category"], score)
                    
                    # Check for milestones
                    for milestone in evaluation["progress"].get("milestones_earned", []):
                        print(f"    🏆 Milestone: {milestone.replace('_', ' ').title()}!")
                    
                    # Check if can retry
                    if not evaluation.get("can_retry", False):
                        break
                    
                    if attempt < max_attempts and score < 70:
                        print(f"        💡 Hint available! Let's try again...")
            
            # Check level advancement
            advancement = teacher.check_level_advancement(learner)
            if advancement["advance"]:
                print(f"\n     {advancement['message']}")
            else:
                print(f"\n     📊 {advancement['message']}")
            
            # Log session
            teacher.log_session(learner, {
                "round": round_num,
                "questions_this_round": questions_per_round,
                "topic": topic
            })
    
    # Final summary
    print("\n" + "="*60)
    print("  LEARNING SESSION COMPLETE")
    print("="*60)
    
    for framework_name in frameworks:
        learner = teacher.get_learner(framework_name)
        avg = sum(learner.scores) / len(learner.scores) if learner.scores else 0
        trend = learner._calculate_trend()
        
        print(f"\n  {framework_name}:")
        print(f"    Questions answered: {learner.total_questions}")
        print(f"    Average score: {avg:.1f}%")
        print(f"    Current level: {learner.current_level}")
        print(f"    Trend: {trend}")
        print(f"    Best streak: {learner.best_streak}")
        print(f"    Milestones: {', '.join(learner.milestones) if learner.milestones else 'Keep going!'}")
    
    # Show log files
    print("\n  📁 Progress logged to:")
    log_dir = "/home/ubuntu/aether/logs"
    for f in os.listdir(log_dir):
        if f.endswith('.jsonl'):
            path = os.path.join(log_dir, f)
            lines = sum(1 for _ in open(path))
            print(f"     {f}: {lines} entries")
    
    return teacher, frameworks


if __name__ == "__main__":
    run_supportive_session(rounds=3, questions_per_round=5)
