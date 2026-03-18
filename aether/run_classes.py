#!/usr/bin/env python3
"""
AETHER Learning System - Class Runner
Runs classes from current progress-based grade level
Includes automatic corruption detection and repair
"""

import json
import os
from datetime import datetime
from openai import OpenAI

# Import integrity checker
import sys
sys.path.insert(0, '/home/ubuntu/aether')
from core.data_integrity import DataIntegrityChecker

client = OpenAI()

# K-12 Curriculum
CURRICULUM = {
    1: {"name": "Grade 1", "topics": ["addition_basics", "subtraction_basics", "counting_patterns", "simple_shapes"]},
    2: {"name": "Grade 2", "topics": ["two_digit_addition", "two_digit_subtraction", "time_telling", "measurement_basics"]},
    3: {"name": "Grade 3", "topics": ["multiplication_intro", "division_intro", "fractions_intro", "area_perimeter"]},
    4: {"name": "Grade 4", "topics": ["multi_digit_multiplication", "long_division", "equivalent_fractions", "angles_geometry"]},
    5: {"name": "Grade 5", "topics": ["decimal_operations", "fraction_operations", "volume_concepts", "coordinate_graphing"]},
    6: {"name": "Grade 6", "topics": ["ratios_proportions", "negative_numbers", "statistical_measures", "equations_one_variable"]},
    7: {"name": "Grade 7", "topics": ["proportional_relationships", "linear_equations", "geometry_constructions", "probability"]},
    8: {"name": "Grade 8", "topics": ["linear_functions", "systems_of_equations", "pythagorean_theorem", "transformations"]},
    9: {"name": "Grade 9 - Algebra I", "topics": ["quadratic_equations", "polynomial_operations", "factoring", "exponential_functions"]},
    10: {"name": "Grade 10 - Geometry", "topics": ["geometric_proofs", "triangle_congruence", "similarity", "trigonometry_intro"]},
    11: {"name": "Grade 11 - Algebra II", "topics": ["complex_numbers", "logarithms", "sequences_series", "conic_sections"]},
    12: {"name": "Grade 12 - Calculus", "topics": ["derivatives", "integrals", "differential_equations_intro", "applications_of_calculus"]}
}

PASS_THRESHOLD = 95  # Must score 95%+ to pass

def run_integrity_check():
    """Run integrity check before starting."""
    print("\n🔍 Running data integrity check...")
    checker = DataIntegrityChecker()
    results = checker.check_all_files()
    
    if results["files_corrupted"] > 0:
        print(f"⚠️  Found and repaired {results['files_corrupted']} corrupted file(s)")
    else:
        print("✅ All data files are valid")
    
    return results

def load_progress(name: str) -> dict:
    """Load student progress with validation."""
    filepath = f"/home/ubuntu/aether/memory/{name.lower()}_full_record.json"
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Validate and ensure required fields
        checker = DataIntegrityChecker()
        is_valid, data = checker.validate_before_save(data)
        
        return data
    except Exception as e:
        print(f"Error loading {name}: {e}")
        return {
            "name": name,
            "total_questions": 0,
            "total_passed": 0,
            "average_score": 50.0,
            "current_level": 1,
            "sessions": []
        }

def save_progress(name: str, data: dict):
    """Save progress with validation."""
    filepath = f"/home/ubuntu/aether/memory/{name.lower()}_full_record.json"
    
    # Validate before saving
    checker = DataIntegrityChecker()
    is_valid, cleaned_data = checker.validate_before_save(data)
    
    cleaned_data["last_updated"] = datetime.now().isoformat()
    
    with open(filepath, 'w') as f:
        json.dump(cleaned_data, f, indent=2)

def generate_question(grade: int, topic: str) -> str:
    """Generate a question for the given grade and topic."""
    grade_name = CURRICULUM[grade]["name"]
    
    prompt = f"""Create ONE challenging math problem for {grade_name}, topic: {topic}.

Requirements:
1. Age-appropriate but challenging
2. Requires showing work
3. Tests understanding, not just memorization

Format:
PROBLEM: [specific problem with numbers]
HINT: [one helpful hint]"""

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )
    return response.choices[0].message.content

def get_student_answer(name: str, role: str, question: str, grade: int) -> str:
    """Get student's answer."""
    grade_name = CURRICULUM[grade]["name"]
    
    prompt = f"""You are {name}, a {role} AI student in {grade_name}.

QUESTION:
{question}

Solve step-by-step. Show ALL work. Explain WHY each step is correct."""

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return response.choices[0].message.content

def grade_answer(question: str, answer: str) -> dict:
    """Grade the answer."""
    prompt = f"""Grade this math answer (0-100):

QUESTION: {question}

ANSWER: {answer}

Score based on:
- Correctness (50 pts)
- Clear reasoning (30 pts)  
- Explanation quality (20 pts)

Return ONLY JSON: {{"score": <0-100>, "feedback": "<brief>", "passed": <true if 95+>}}"""

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )
    
    try:
        text = response.choices[0].message.content
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            result = json.loads(text[start:end])
            # Validate score
            result["score"] = max(0, min(100, int(result.get("score", 50))))
            result["passed"] = result["score"] >= PASS_THRESHOLD
            return result
    except:
        pass
    
    return {"score": 70, "feedback": "Evaluation error", "passed": False}

def run_class_session(name: str, role: str, grade: int, questions_per_topic: int = 1) -> dict:
    """Run a class session for one student."""
    grade_info = CURRICULUM[grade]
    results = []
    
    print(f"\n{'='*60}")
    print(f"📚 {name} - {grade_info['name']}")
    print(f"{'='*60}")
    
    for topic in grade_info["topics"]:
        for q_num in range(questions_per_topic):
            print(f"\n📝 Topic: {topic}")
            
            # Generate question
            question = generate_question(grade, topic)
            print(f"Q: {question[:80]}...")
            
            # Get answer
            answer = get_student_answer(name, role, question, grade)
            
            # Grade
            result = grade_answer(question, answer)
            score = result["score"]
            passed = result["passed"]
            
            status = "✅ PASS" if passed else "❌ NEED MORE PRACTICE"
            print(f"Score: {score}% | {status}")
            
            results.append({
                "topic": topic,
                "score": score,
                "passed": passed,
                "feedback": result.get("feedback", "")
            })
    
    # Calculate summary
    avg_score = sum(r["score"] for r in results) / len(results)
    pass_rate = sum(1 for r in results if r["passed"]) / len(results) * 100
    can_advance = pass_rate >= 75  # Need 75% pass rate to advance
    
    print(f"\n📊 Session Summary:")
    print(f"   Average Score: {avg_score:.1f}%")
    print(f"   Pass Rate: {pass_rate:.1f}%")
    print(f"   Can Advance: {'Yes ✅' if can_advance else 'No - More practice needed'}")
    
    return {
        "grade": grade,
        "grade_name": grade_info["name"],
        "average_score": avg_score,
        "pass_rate": pass_rate,
        "can_advance": can_advance,
        "results": results
    }

def update_student_progress(name: str, session: dict) -> dict:
    """Update student progress after a session."""
    progress = load_progress(name)
    
    # Update totals
    new_questions = len(session["results"])
    new_passed = sum(1 for r in session["results"] if r["passed"])
    
    old_total = progress.get("total_questions", 0)
    old_avg = progress.get("average_score", 50.0)
    
    progress["total_questions"] = old_total + new_questions
    progress["total_passed"] = progress.get("total_passed", 0) + new_passed
    
    # Update running average (weighted)
    if progress["total_questions"] > 0:
        progress["average_score"] = (
            (old_avg * old_total + session["average_score"] * new_questions) 
            / progress["total_questions"]
        )
    
    # Update level based on performance
    if session["can_advance"] and session["grade"] == progress.get("current_level", 1):
        progress["current_level"] = min(session["grade"] + 1, 12)
        print(f"\n🎉 {name} ADVANCED to Grade {progress['current_level']}!")
    
    # Add session record
    if "sessions" not in progress:
        progress["sessions"] = []
    
    progress["sessions"].append({
        "timestamp": datetime.now().isoformat(),
        "grade": session["grade"],
        "average_score": session["average_score"],
        "pass_rate": session["pass_rate"],
        "advanced": session["can_advance"]
    })
    
    # Save with validation
    save_progress(name, progress)
    
    return progress

def main():
    print("\n" + "="*70)
    print("🎓 AETHER LEARNING SYSTEM - CLASS SESSION")
    print("="*70)
    
    # Run integrity check first
    run_integrity_check()
    
    students = [
        ("Stratify", "Theoretical Mathematician with strong creativity and intuition"),
        ("Principia", "Rigorous Verifier with exceptional discipline and rigor")
    ]
    
    all_results = {}
    
    for name, role in students:
        # Load current progress
        progress = load_progress(name)
        current_grade = progress.get("current_level", 1)
        
        print(f"\n📋 {name} starting at Grade {current_grade}")
        print(f"   Total Questions: {progress.get('total_questions', 0)}")
        print(f"   Average Score: {progress.get('average_score', 0):.1f}%")
        
        if current_grade <= 12:
            # Run session
            session = run_class_session(name, role, current_grade)
            
            # Update progress
            updated = update_student_progress(name, session)
            
            all_results[name] = {
                "session": session,
                "progress": updated
            }
        else:
            print(f"   🎓 {name} has completed K-12!")
    
    # Final summary
    print("\n" + "="*70)
    print("📊 FINAL SESSION SUMMARY")
    print("="*70)
    
    for name, data in all_results.items():
        session = data["session"]
        progress = data["progress"]
        
        print(f"\n{name}:")
        print(f"  Current Grade: {progress['current_level']}")
        print(f"  Session Score: {session['average_score']:.1f}%")
        print(f"  Overall Average: {progress['average_score']:.1f}%")
        print(f"  Total Questions: {progress['total_questions']}")
        print(f"  Advanced: {'Yes ✅' if session['can_advance'] else 'No'}")
    
    # Run final integrity check
    print("\n")
    run_integrity_check()
    
    print("\n✅ Class session complete!")

if __name__ == "__main__":
    main()
