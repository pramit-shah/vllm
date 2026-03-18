#!/usr/bin/env python3
"""
AETHER Learning System - Grade 5 Onwards
Continues education from Grade 5 through K-12
"""

import json
import os
from datetime import datetime
from openai import OpenAI

client = OpenAI()

# Grade 5-12 Curriculum
CURRICULUM = {
    5: {
        "name": "Grade 5 - Upper Elementary",
        "topics": [
            "decimal_operations", "fraction_multiplication", "volume_concepts",
            "coordinate_graphing", "order_of_operations", "algebraic_expressions"
        ],
        "pass_threshold": 95
    },
    6: {
        "name": "Grade 6 - Middle School Entry",
        "topics": [
            "ratios_proportions", "negative_numbers", "statistical_measures",
            "equations_one_variable", "area_surface_area", "rational_numbers"
        ],
        "pass_threshold": 95
    },
    7: {
        "name": "Grade 7 - Pre-Algebra",
        "topics": [
            "proportional_relationships", "linear_equations", "geometry_constructions",
            "probability", "inequalities", "scale_drawings"
        ],
        "pass_threshold": 95
    },
    8: {
        "name": "Grade 8 - Algebra Foundations",
        "topics": [
            "linear_functions", "systems_of_equations", "pythagorean_theorem",
            "transformations", "scientific_notation", "irrational_numbers"
        ],
        "pass_threshold": 95
    },
    9: {
        "name": "Grade 9 - Algebra I",
        "topics": [
            "quadratic_equations", "polynomial_operations", "factoring",
            "radical_expressions", "function_notation", "exponential_functions"
        ],
        "pass_threshold": 95
    },
    10: {
        "name": "Grade 10 - Geometry",
        "topics": [
            "geometric_proofs", "triangle_congruence", "similarity",
            "trigonometry_intro", "circles", "coordinate_geometry"
        ],
        "pass_threshold": 95
    },
    11: {
        "name": "Grade 11 - Algebra II / Pre-Calculus",
        "topics": [
            "complex_numbers", "logarithms", "sequences_series",
            "conic_sections", "matrices", "limits_intro"
        ],
        "pass_threshold": 95
    },
    12: {
        "name": "Grade 12 - Calculus",
        "topics": [
            "derivatives", "integrals", "differential_equations_intro",
            "applications_of_calculus", "infinite_series", "multivariable_intro"
        ],
        "pass_threshold": 95
    }
}

def generate_question(grade, topic):
    """Generate a challenging question for the given grade and topic."""
    grade_info = CURRICULUM[grade]
    
    prompt = f"""You are creating a challenging math question for {grade_info['name']}.
Topic: {topic}

Create ONE specific problem that:
1. Tests deep understanding, not just memorization
2. Requires showing work and explaining reasoning
3. Is appropriate for this grade level but challenging

Format:
PROBLEM: [The actual problem]
EXPECTED_APPROACH: [Brief description of how to solve it]

Be specific with numbers and scenarios."""

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return response.choices[0].message.content

def get_student_answer(student_name, role, question, grade, topic):
    """Get the student's answer to a question."""
    prompt = f"""You are {student_name}, a {role} AI learning mathematics.
You are currently in {CURRICULUM[grade]['name']}.

QUESTION on {topic}:
{question}

Solve this problem step by step. Show ALL your work and explain WHY each step is valid.
Be thorough but concise. Demonstrate genuine understanding."""

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600
    )
    return response.choices[0].message.content

def grade_answer(question, answer, grade, topic):
    """Grade the student's answer."""
    prompt = f"""Grade this math answer on a scale of 0-100.

QUESTION: {question}

STUDENT'S ANSWER: {answer}

Evaluate:
1. Mathematical correctness (40 points)
2. Clear step-by-step reasoning (30 points)
3. Explanation of WHY steps are valid (20 points)
4. Proper notation and presentation (10 points)

Respond with ONLY a JSON object:
{{"score": <number>, "feedback": "<brief feedback>", "passed": <true if score >= 95>}}"""

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    
    try:
        # Extract JSON from response
        text = response.choices[0].message.content
        # Find JSON in response
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except:
        pass
    
    return {"score": 75, "feedback": "Evaluation error", "passed": False}

def run_grade_session(student_name, role, grade, num_questions=5):
    """Run a learning session for one grade level."""
    grade_info = CURRICULUM[grade]
    results = []
    
    print(f"\n{'='*60}")
    print(f"📚 {student_name} - {grade_info['name']}")
    print(f"{'='*60}")
    
    for i, topic in enumerate(grade_info['topics'][:num_questions]):
        print(f"\n--- Question {i+1}: {topic} ---")
        
        # Generate question
        question = generate_question(grade, topic)
        print(f"Q: {question[:100]}...")
        
        # Get student answer
        answer = get_student_answer(student_name, role, question, grade, topic)
        
        # Grade answer
        result = grade_answer(question, answer, grade, topic)
        score = result.get('score', 0)
        passed = result.get('passed', False)
        
        status = "✅ PASSED" if passed else "❌ NOT PASSED"
        print(f"Score: {score}% | {status}")
        
        results.append({
            "topic": topic,
            "score": score,
            "passed": passed,
            "feedback": result.get('feedback', '')
        })
    
    # Calculate grade summary
    avg_score = sum(r['score'] for r in results) / len(results)
    pass_rate = sum(1 for r in results if r['passed']) / len(results) * 100
    
    print(f"\n📊 Grade Summary: Avg={avg_score:.1f}%, Pass Rate={pass_rate:.1f}%")
    
    return {
        "grade": grade,
        "grade_name": grade_info['name'],
        "average_score": avg_score,
        "pass_rate": pass_rate,
        "results": results,
        "advanced": pass_rate >= 75  # Need 75% pass rate to advance
    }

def update_progress(student_name, session_result):
    """Update student's progress file."""
    progress_file = f"/home/ubuntu/aether/memory/{student_name.lower()}_full_record.json"
    
    try:
        with open(progress_file, 'r') as f:
            progress = json.load(f)
    except:
        progress = {
            "name": student_name,
            "current_level": 5,
            "total_questions": 0,
            "total_passed": 0,
            "average_score": 0,
            "sessions": []
        }
    
    # Update progress
    new_questions = len(session_result['results'])
    new_passed = sum(1 for r in session_result['results'] if r['passed'])
    
    old_total = progress.get('total_questions', 0)
    old_avg = progress.get('average_score', 0)
    
    progress['total_questions'] = old_total + new_questions
    progress['total_passed'] = progress.get('total_passed', 0) + new_passed
    
    # Update running average
    if progress['total_questions'] > 0:
        progress['average_score'] = (
            (old_avg * old_total + session_result['average_score'] * new_questions) 
            / progress['total_questions']
        )
    
    # Update level if advanced
    if session_result['advanced']:
        progress['current_level'] = session_result['grade'] + 1
    
    progress['sessions'].append({
        "timestamp": datetime.now().isoformat(),
        "grade": session_result['grade'],
        "average_score": session_result['average_score'],
        "pass_rate": session_result['pass_rate'],
        "advanced": session_result['advanced']
    })
    
    with open(progress_file, 'w') as f:
        json.dump(progress, f, indent=2)
    
    return progress

def main():
    print("\n" + "="*70)
    print("🎓 AETHER LEARNING SYSTEM - Grade 5 Onwards")
    print("="*70)
    
    students = [
        ("Stratify", "Theoretical Mathematician specializing in abstract reasoning"),
        ("Principia", "Rigorous Verifier specializing in mathematical proofs")
    ]
    
    # Run sessions for each student
    all_results = {}
    
    for student_name, role in students:
        # Load current level
        try:
            with open(f"/home/ubuntu/aether/memory/{student_name.lower()}_full_record.json", 'r') as f:
                progress = json.load(f)
                current_grade = progress.get('current_level', 5)
        except:
            current_grade = 5
        
        # Run session at current grade
        if current_grade <= 12:
            result = run_grade_session(student_name, role, current_grade, num_questions=4)
            progress = update_progress(student_name, result)
            all_results[student_name] = {
                "session": result,
                "progress": progress
            }
            
            if result['advanced']:
                print(f"\n🎉 {student_name} ADVANCED to Grade {current_grade + 1}!")
            else:
                print(f"\n📖 {student_name} needs more practice at Grade {current_grade}")
        else:
            print(f"\n🎓 {student_name} has completed K-12! Ready for Higher Education.")
    
    # Summary
    print("\n" + "="*70)
    print("📊 SESSION SUMMARY")
    print("="*70)
    
    for name, data in all_results.items():
        session = data['session']
        progress = data['progress']
        print(f"\n{name}:")
        print(f"  Current Grade: {progress['current_level']}")
        print(f"  Session Score: {session['average_score']:.1f}%")
        print(f"  Pass Rate: {session['pass_rate']:.1f}%")
        print(f"  Total Questions: {progress['total_questions']}")
        print(f"  Overall Average: {progress['average_score']:.1f}%")
        print(f"  Advanced: {'Yes ✅' if session['advanced'] else 'No - More practice needed'}")
    
    print("\n✅ Session complete!")

if __name__ == "__main__":
    main()
