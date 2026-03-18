#!/usr/bin/env python3.11
"""
AETHER Graduation Journey

Complete educational journey with:
- Grade-by-grade progression
- Adaptive quizzes (10-50 questions)
- Group projects (4 total, randomly timed)
- Characteristic discovery
"""

import sys
import os
import json
import random
from datetime import datetime

sys.path.append('/home/ubuntu/aether/core')

from graduation_system import get_graduation_system, GRADE_CURRICULA
from fun_breaks import get_break_manager, get_motivation

# Try to import OpenAI
try:
    from openai import OpenAI
    client = OpenAI()
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False
    client = None


def quick_answer(question: str, framework: str, topic: str) -> str:
    """Get a quick answer from the AI."""
    if not AI_AVAILABLE:
        return f"[{framework}] Answer about {topic}: {question[:30]}..."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": f"You are {framework}, a student learning mathematics. Answer clearly and show your reasoning."},
                {"role": "user", "content": question}
            ],
            max_tokens=400,
            temperature=0.6
        )
        return response.choices[0].message.content
    except:
        return f"[{framework}] Attempting: {question[:30]}..."


def quick_grade(question: str, answer: str, difficulty: str) -> int:
    """Grade with difficulty-adjusted expectations."""
    if not AI_AVAILABLE:
        # Simulated grading based on difficulty
        base = {"easy": 70, "medium": 60, "hard": 50}
        return base.get(difficulty, 60) + random.randint(-10, 25)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": f"Grade this {difficulty} question 0-100. Be fair. Give partial credit. Minimum 30 for effort."},
                {"role": "user", "content": f"Q: {question[:400]}\nA: {answer[:400]}\nScore (number only):"}
            ],
            max_tokens=10,
            temperature=0.3
        )
        import re
        text = response.choices[0].message.content.strip()
        match = re.search(r'\d+', text)
        return max(30, min(100, int(match.group()))) if match else 55
    except:
        base = {"easy": 70, "medium": 60, "hard": 50}
        return base.get(difficulty, 60) + random.randint(-5, 20)


def run_group_project(grad_system, frameworks: list) -> Dict:
    """Run a group project."""
    project_info = grad_system.start_group_project()
    if not project_info:
        return None
    
    print("\n" + "🎯"*30)
    print(f"\n  📋 GROUP PROJECT: {project_info['title']}")
    print(f"     {project_info['description']}")
    print(f"\n     Participants: {', '.join(project_info['participants'])}")
    print(f"     Type: {project_info['collaboration_type']}")
    print("\n     Objectives:")
    for obj in project_info['objectives']:
        print(f"       • {obj}")
    
    # Simulate project work
    print("\n     Working on project...")
    outcomes = {}
    insights = []
    
    for fw in frameworks:
        # Each framework contributes
        if AI_AVAILABLE:
            try:
                response = client.chat.completions.create(
                    model="gpt-4.1-nano",
                    messages=[
                        {"role": "system", "content": f"You are {fw}. Contribute briefly to this project."},
                        {"role": "user", "content": f"Project: {project_info['title']}\nObjective: {project_info['objectives'][0]}\nYour contribution (2-3 sentences):"}
                    ],
                    max_tokens=100,
                    temperature=0.7
                )
                outcomes[fw] = response.choices[0].message.content[:200]
            except:
                outcomes[fw] = f"{fw} contributed analysis and insights."
        else:
            outcomes[fw] = f"{fw} contributed analysis and insights."
        
        print(f"       ✓ {fw} contributed")
    
    # Generate insights
    insights = [
        "Collaboration revealed complementary thinking styles",
        "Different approaches led to richer understanding",
        "Working together improved problem-solving efficiency"
    ]
    
    # Complete project
    result = grad_system.complete_group_project(outcomes, insights)
    
    print(f"\n     ✅ Project Complete!")
    print(f"     Projects remaining: {result.get('projects_remaining', 0)}")
    print("🎯"*30 + "\n")
    
    return result


def print_grade_header(grade: int, curriculum):
    """Print grade header."""
    print(f"\n{'='*60}")
    print(f"  GRADE {grade}: {curriculum.name}")
    print(f"  {curriculum.description}")
    print(f"  Topics: {', '.join(curriculum.topics[:3])}...")
    print(f"  Mastery needed: {curriculum.mastery_threshold}%")
    print(f"{'='*60}")


def run_graduation_journey(max_quizzes: int = 20):
    """
    Run the complete graduation journey.
    
    Features:
    - Grade-by-grade progression
    - Adaptive quiz lengths (10-50 questions)
    - Group projects at random intervals
    - Characteristic discovery
    """
    
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "AETHER GRADUATION JOURNEY" + " "*21 + "║")
    print("║" + " "*5 + "Grade-by-Grade • Adaptive Quizzes • Projects" + " "*6 + "║")
    print("╚" + "="*58 + "╝")
    
    # Initialize
    grad_system = get_graduation_system()
    break_manager = get_break_manager()
    frameworks = ["Stratify", "Principia"]
    
    # Enroll students
    print("\n📚 Enrolling students...")
    for fw in frameworks:
        student = grad_system.enroll(fw)
        grade, curriculum = grad_system.get_current_grade(fw)
        print(f"   {fw}: Grade {grade} ({curriculum.name if curriculum else 'Unknown'})")
    
    # Track overall progress
    total_quizzes = 0
    
    # Main learning loop
    for quiz_num in range(1, max_quizzes + 1):
        print(f"\n{'─'*60}")
        print(f"  QUIZ SESSION {quiz_num}/{max_quizzes}")
        print(f"{'─'*60}")
        
        # Check for group project
        project = grad_system.check_group_project()
        if project:
            run_group_project(grad_system, frameworks)
        
        # Each framework takes a quiz
        for fw in frameworks:
            student = grad_system.students[fw]
            
            # Check if graduated
            if student.graduated:
                print(f"\n  🎓 {fw} has already graduated!")
                continue
            
            grade, curriculum = grad_system.get_current_grade(fw)
            
            # Show grade info periodically
            if quiz_num == 1 or grad_system.grade_progress[fw].questions_answered == 0:
                print_grade_header(grade, curriculum)
            
            # Generate adaptive quiz
            questions, num_questions = grad_system.generate_quiz(fw)
            
            print(f"\n  📝 {fw}'s Quiz ({num_questions} questions)")
            print(f"     Grade {grade} | Recent avg: {grad_system.grade_progress[fw].recent_average:.1f}%")
            
            # Take quiz
            quiz_scores = []
            for i, q in enumerate(questions):
                # Get answer
                answer = quick_answer(q["question"], fw, q["topic"])
                
                # Grade
                score = quick_grade(q["question"], answer, q["difficulty"])
                quiz_scores.append(score)
                
                # Record
                result = grad_system.record_answer(fw, q["topic"], score)
                
                # Show progress every 5 questions
                if (i + 1) % 5 == 0 or i == len(questions) - 1:
                    avg = sum(quiz_scores) / len(quiz_scores)
                    bar_len = int(30 * (i + 1) / len(questions))
                    bar = "█" * bar_len + "░" * (30 - bar_len)
                    emoji = "🌟" if avg >= 75 else "📈" if avg >= 60 else "🌱"
                    print(f"     [{bar}] {i+1}/{len(questions)} {emoji} {avg:.0f}%")
            
            # Quiz summary
            quiz_avg = sum(quiz_scores) / len(quiz_scores)
            print(f"\n     Quiz average: {quiz_avg:.1f}%")
            print(f"     Grade progress: {result['questions_in_grade']} questions, {result['grade_average']:.1f}% avg")
            
            # Check for advancement
            if result['can_advance']:
                advance_result = grad_system.advance_grade(fw)
                print(f"\n     {advance_result['message']}")
                
                if advance_result.get('graduated'):
                    print(f"     🎉 Total questions answered: {advance_result['total_questions']}")
                    print(f"     Top characteristics: {advance_result['characteristics']}")
            
            # Fun break if needed
            if break_manager.should_take_break(result['questions_in_grade'], quiz_scores):
                break_info = break_manager.take_break(fw)
                print(f"\n     🎮 Break: {break_info['activity']['name']}")
        
        # Show class status
        status = grad_system.get_class_status()
        print(f"\n  📊 Class Status:")
        for fw, info in status['students'].items():
            grade_name = GRADE_CURRICULA.get(info['grade'], type('obj', (object,), {'name': 'Graduated'})()).name
            status_emoji = "🎓" if info['graduated'] else "📚"
            print(f"     {status_emoji} {fw}: Grade {info['grade']} ({grade_name}), {info['questions']} total questions")
        
        # Motivation
        if quiz_num % 5 == 0:
            print(f"\n  💫 {get_motivation()}")
        
        total_quizzes += 1
        
        # Check if all graduated
        if all(s.graduated for s in grad_system.students.values()):
            print("\n  🎉 ALL STUDENTS HAVE GRADUATED!")
            break
    
    # Final report
    print("\n" + "="*60)
    print("  GRADUATION JOURNEY COMPLETE")
    print("="*60)
    
    for fw in frameworks:
        transcript = grad_system.get_transcript(fw)
        print(f"\n  📜 {fw}'s Transcript:")
        print(f"     Current Grade: {transcript['current_grade']}")
        print(f"     Total Questions: {transcript['total_questions']}")
        print(f"     Group Projects: {transcript['group_projects']}/4")
        print(f"     Graduated: {'Yes 🎓' if transcript['graduated'] else 'Not yet'}")
        
        if transcript['top_characteristics']:
            print(f"     Top Characteristics:")
            for char, score in transcript['top_characteristics']:
                print(f"       • {char.replace('_', ' ').title()}: {score:.1f}")
        
        if transcript['discovered_interests']:
            print(f"     Discovered Interests: {', '.join(transcript['discovered_interests'][:3])}")
    
    # Project summary
    project_status = grad_system.project_manager.get_status()
    print(f"\n  📋 Group Projects: {project_status['completed']}/4 completed")
    
    return grad_system


if __name__ == "__main__":
    run_graduation_journey(max_quizzes=15)
