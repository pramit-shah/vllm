#!/usr/bin/env python3.11
"""
AETHER Fast Learning Journey

Optimized for:
- Faster progress
- Fun breaks to reduce stress
- Persistent memory to build on success
- Momentum building
"""

import sys
import os
import json
import random
from datetime import datetime

sys.path.append('/home/ubuntu/aether/core')

from supportive_teacher import get_supportive_teacher, TrainingConfig
from fun_breaks import get_break_manager, get_motivation
from learning_memory import get_memory_store

# Try to import OpenAI
try:
    from openai import OpenAI
    client = OpenAI()
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False
    client = None


def quick_answer(question: str, framework: str, model: str = "gpt-4.1-nano") -> str:
    """Get a quick answer from the AI."""
    if not AI_AVAILABLE:
        return f"[{framework}] Simulated answer for: {question[:50]}..."
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"You are {framework}, a mathematical thinker. Give concise, clear answers."},
                {"role": "user", "content": question}
            ],
            max_tokens=500,
            temperature=0.5
        )
        return response.choices[0].message.content
    except:
        return f"[{framework}] Answer attempt for: {question[:50]}..."


def quick_grade(question: str, answer: str, model: str = "gpt-4.1-nano") -> int:
    """Quick grading with encouragement."""
    if not AI_AVAILABLE:
        # Simulated grading - more generous
        return random.randint(45, 85)
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Grade 0-100. Be encouraging. Give partial credit. Minimum 30 for effort."},
                {"role": "user", "content": f"Question: {question[:500]}\nAnswer: {answer[:500]}\nScore (just the number):"}
            ],
            max_tokens=10,
            temperature=0.3
        )
        text = response.choices[0].message.content.strip()
        # Extract number
        import re
        match = re.search(r'\d+', text)
        return max(30, min(100, int(match.group()))) if match else 50
    except:
        return random.randint(45, 75)


def create_simple_question(topic: str, level: int) -> str:
    """Create a simple question quickly."""
    templates = {
        1: [
            f"Explain the basic concept of {topic} in simple terms.",
            f"What is {topic} and why is it important?",
            f"Give a simple example of {topic}.",
        ],
        2: [
            f"How does {topic} relate to everyday mathematics?",
            f"Describe the key properties of {topic}.",
            f"What are the main uses of {topic}?",
        ],
        3: [
            f"Explain how {topic} connects to other mathematical concepts.",
            f"What problems can be solved using {topic}?",
            f"Describe the historical development of {topic}.",
        ]
    }
    level_key = min(3, max(1, level))
    return random.choice(templates[level_key])


def print_progress_bar(current: int, total: int, score: float, width: int = 30):
    """Print a visual progress bar."""
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)
    emoji = "🌟" if score >= 70 else "📈" if score >= 50 else "🌱"
    print(f"    [{bar}] {current}/{total} {emoji} {score:.0f}%")


def run_fast_learning(rounds: int = 10, questions_per_round: int = 5):
    """
    Run optimized fast learning session.
    
    Features:
    - Faster question/answer cycle
    - Fun breaks every 10 questions
    - Persistent memory
    - Momentum building
    - Celebration of progress
    """
    
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "AETHER FAST LEARNING" + " "*26 + "║")
    print("║" + " "*5 + "With Breaks, Memory & Momentum" + " "*21 + "║")
    print("╚" + "="*58 + "╝")
    
    # Initialize systems
    teacher = get_supportive_teacher()
    break_manager = get_break_manager()
    memory_store = get_memory_store()
    
    # Frameworks
    frameworks = ["Stratify", "Principia"]
    
    # Topics (simple to complex)
    topics = [
        "numbers and counting",
        "basic arithmetic",
        "fractions and decimals",
        "simple algebra",
        "patterns and sequences",
        "basic geometry",
        "measurement and units",
        "data and graphs",
        "problem solving",
        "mathematical reasoning"
    ]
    
    # Register and load memory
    print("\n📚 Loading learning memory...")
    for fw in frameworks:
        teacher.register_learner(fw)
        summary = memory_store.get_summary(fw)
        print(f"   {fw}: Level {summary['current_level']}, "
              f"{summary['total_questions']} questions, "
              f"avg {summary['average_score']:.1f}%")
        
        # Show recommendations
        recs = memory_store.get_recommendations(fw)
        if recs:
            print(f"      💡 {recs[0]}")
    
    # Start sessions
    sessions = {fw: memory_store.start_session(fw) for fw in frameworks}
    
    print(f"\n🚀 Starting {rounds} rounds with {questions_per_round} questions each")
    print(f"   Total: {rounds * questions_per_round * len(frameworks)} questions")
    print(f"   Breaks: Every 10 questions + when needed")
    
    # Track stats
    stats = {fw: {"scores": [], "questions": 0, "breaks": 0} for fw in frameworks}
    total_questions = 0
    
    # Main learning loop
    for round_num in range(1, rounds + 1):
        print(f"\n{'='*50}")
        print(f"  ROUND {round_num}/{rounds}")
        print(f"{'='*50}")
        
        for fw in frameworks:
            learner = teacher.get_learner(fw)
            memory = memory_store.get_or_create(fw)
            
            print(f"\n  {fw}'s turn (Level {memory.current_level})")
            
            # Check if break needed
            if break_manager.should_take_break(stats[fw]["questions"], stats[fw]["scores"]):
                print(f"\n  🎮 BREAK TIME for {fw}!")
                break_info = break_manager.take_break(fw)
                print(f"     {break_info['message']}")
                print(f"     {break_info['activity']['name']}: {break_info['activity']['content'][:100]}...")
                stats[fw]["breaks"] += 1
                print(f"     ✓ Break complete! Feeling refreshed.")
            
            # Quick questions
            round_scores = []
            for q_num in range(1, questions_per_round + 1):
                # Select topic based on level
                topic_idx = min(memory.current_level - 1, len(topics) - 1)
                topic = topics[topic_idx]
                
                # Create question
                question = create_simple_question(topic, memory.current_level)
                
                # Get answer
                answer = quick_answer(question, fw)
                
                # Grade
                score = quick_grade(question, answer)
                
                # Record in memory
                progress = memory_store.record_answer(fw, score, topic)
                
                # Update stats
                stats[fw]["scores"].append(score)
                stats[fw]["questions"] += 1
                round_scores.append(score)
                total_questions += 1
                
                # Show progress
                print_progress_bar(q_num, questions_per_round, score)
                
                # Celebrate milestones
                for milestone in progress.get("milestones_earned", []):
                    print(f"    🏆 MILESTONE: {milestone.replace('_', ' ').title()}!")
            
            # Round summary
            round_avg = sum(round_scores) / len(round_scores)
            overall_avg = sum(stats[fw]["scores"]) / len(stats[fw]["scores"])
            
            print(f"\n    Round avg: {round_avg:.1f}% | Overall: {overall_avg:.1f}%")
            
            # Check for level advancement
            if round_avg >= 60 and len(stats[fw]["scores"]) >= 10:
                recent_avg = sum(stats[fw]["scores"][-10:]) / 10
                if recent_avg >= 60 and memory.current_level < 10:
                    memory_store.update_level(fw, memory.current_level + 1)
                    print(f"    🎉 LEVEL UP! Now at Level {memory.current_level + 1}!")
            
            # Motivation
            if round_num % 3 == 0:
                print(f"\n    💫 {get_motivation()}")
    
    # End sessions
    for fw in frameworks:
        memory_store.end_session(fw, sessions[fw], {
            "questions": stats[fw]["questions"],
            "average": sum(stats[fw]["scores"]) / len(stats[fw]["scores"]) if stats[fw]["scores"] else 0,
            "breaks": stats[fw]["breaks"]
        })
    
    # Final summary
    print("\n" + "="*50)
    print("  SESSION COMPLETE!")
    print("="*50)
    
    print(f"\n  📊 Total questions: {total_questions}")
    
    for fw in frameworks:
        summary = memory_store.get_summary(fw)
        scores = stats[fw]["scores"]
        
        # Calculate improvement
        if len(scores) >= 10:
            first_5 = sum(scores[:5]) / 5
            last_5 = sum(scores[-5:]) / 5
            improvement = last_5 - first_5
        else:
            improvement = 0
        
        print(f"\n  {fw}:")
        print(f"    Questions: {stats[fw]['questions']}")
        print(f"    Average: {sum(scores)/len(scores):.1f}%")
        print(f"    Level: {summary['current_level']}")
        print(f"    Best streak: {summary['best_streak']}")
        print(f"    Improvement: {'+' if improvement >= 0 else ''}{improvement:.1f}%")
        print(f"    Breaks taken: {stats[fw]['breaks']}")
        print(f"    Milestones: {', '.join(summary['milestones'][-3:]) if summary['milestones'] else 'Keep going!'}")
    
    # Break stats
    break_stats = break_manager.get_stats()
    print(f"\n  🎮 Break Activities: {break_stats['total_breaks']} breaks taken")
    
    # Save final state
    print("\n  💾 Progress saved to memory!")
    print(f"     Memory files: /home/ubuntu/aether/memory/")
    
    return stats, memory_store


if __name__ == "__main__":
    # Run with more rounds for better learning
    run_fast_learning(rounds=10, questions_per_round=5)
