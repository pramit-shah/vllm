#!/usr/bin/env python3
"""
AETHER Learning System - Multi-Session Runner
Runs multiple class sessions, tracks progress, saves to memory, pushes to GitHub.
Includes integrity checks, discovery detection, conversation recording.
"""

import json
import os
import sys
import random
from datetime import datetime
from openai import OpenAI

sys.path.insert(0, '/home/ubuntu/aether')
from core.data_integrity import DataIntegrityChecker

client = OpenAI()

# K-12 Curriculum with detailed topics
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
    12: {"name": "Grade 12 - Calculus", "topics": ["derivatives", "integrals", "differential_equations_intro", "applications_of_calculus"]},
}

PASS_THRESHOLD = 95
ADVANCE_RATE = 75  # % of questions that must be passed to advance

# Fun break activities
BREAK_ACTIVITIES = [
    {"name": "Fibonacci Fun", "prompt": "What comes next: 1, 1, 2, 3, 5, 8, 13, ?"},
    {"name": "Pi Day", "prompt": "How many digits of pi can you recite? Start: 3.14159..."},
    {"name": "Magic Square", "prompt": "Fill a 3x3 grid with 1-9 so all rows/columns/diagonals sum to 15"},
    {"name": "Number Riddle", "prompt": "I'm thinking of a number. Double it, add 6, divide by 2, subtract the original. What do you get?"},
    {"name": "Pattern Master", "prompt": "What's the pattern: 2, 6, 12, 20, 30, ?"},
]


def load_progress(name):
    filepath = f"/home/ubuntu/aether/memory/{name.lower()}_full_record.json"
    checker = DataIntegrityChecker()
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        is_valid, data = checker.validate_before_save(data)
        return data
    except:
        return {"name": name, "total_questions": 0, "total_passed": 0,
                "average_score": 50.0, "current_level": 1, "sessions": [],
                "character": {}}


def save_progress(name, data):
    filepath = f"/home/ubuntu/aether/memory/{name.lower()}_full_record.json"
    checker = DataIntegrityChecker()
    is_valid, cleaned = checker.validate_before_save(data)
    cleaned["last_updated"] = datetime.now().isoformat()
    with open(filepath, 'w') as f:
        json.dump(cleaned, f, indent=2)


def log_score(name, grade, topic, score, question, answer, feedback):
    """Log score to appropriate files based on classification."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "framework": name,
        "grade": grade,
        "topic": topic,
        "score": score,
        "question_preview": question[:100],
        "answer_preview": answer[:100],
        "feedback": feedback
    }

    # All scores
    with open("/home/ubuntu/aether/logs/all_scores.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")

    # Score-based logging
    if score >= 90:
        with open("/home/ubuntu/aether/logs/passed_90_plus.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")
    if 75 <= score <= 89:
        with open("/home/ubuntu/aether/logs/medium_75_89.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")
    if 50 <= score <= 74:
        with open("/home/ubuntu/aether/logs/key_details.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")
    if score < 35:
        with open("/home/ubuntu/aether/logs/critical_below_35.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")
    if score <= 50:
        with open("/home/ubuntu/aether/logs/lower_level_learning_0_50.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")

    # Record conversations
    if score >= 75:
        with open("/home/ubuntu/aether/records/high_score_75_plus/conversations.jsonl", "a") as f:
            full = {**entry, "full_answer": answer}
            f.write(json.dumps(full) + "\n")
    else:
        with open("/home/ubuntu/aether/records/low_score_74_minus/conversations.jsonl", "a") as f:
            full = {**entry, "full_answer": answer}
            f.write(json.dumps(full) + "\n")


def check_for_discovery(answer, score, name, topic):
    """Check if the answer contains potential new mathematical insights."""
    indicators = ["novel", "new approach", "alternatively", "my own method",
                   "I discovered", "unique solution", "different way",
                   "generalize", "pattern I noticed", "conjecture"]
    
    found = any(ind.lower() in answer.lower() for ind in indicators)
    
    if found and score >= 35:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "framework": name,
            "topic": topic,
            "score": score,
            "type": "potential_discovery",
            "answer_preview": answer[:300],
            "status": "AWAITING_MANUS_REVIEW"
        }
        with open("/home/ubuntu/aether/discoveries/all_discoveries.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")
        with open("/home/ubuntu/aether/discoveries/manus_review_flags.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")
        return True
    return False


def generate_question(grade, topic):
    grade_name = CURRICULUM[grade]["name"]
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": f"""Create ONE challenging math problem for {grade_name}, topic: {topic}.
Requirements: Age-appropriate but challenging. Requires showing work. Tests deep understanding.
Format:
PROBLEM: [specific problem with numbers]
HINT: [one helpful hint]"""}],
        max_tokens=200
    )
    return response.choices[0].message.content


def get_answer(name, role, question, grade):
    grade_name = CURRICULUM[grade]["name"]
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": f"""You are {name}, a {role} AI student in {grade_name}.
QUESTION:
{question}
Solve step-by-step. Show ALL work. Explain WHY each step is correct. Be creative and thorough."""}],
        max_tokens=500
    )
    return response.choices[0].message.content


def grade_answer(question, answer):
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": f"""Grade this math answer strictly (0-100):
QUESTION: {question}
ANSWER: {answer}
Score: Correctness(50pts) + Clear reasoning(30pts) + Explanation quality(20pts)
Return ONLY JSON: {{"score": <0-100>, "feedback": "<brief>"}}"""}],
        max_tokens=100
    )
    try:
        text = response.choices[0].message.content
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            result = json.loads(text[start:end])
            result["score"] = max(0, min(100, int(result.get("score", 50))))
            result["passed"] = result["score"] >= PASS_THRESHOLD
            return result
    except:
        pass
    return {"score": 70, "feedback": "Evaluation error", "passed": False}


def provide_study_material(grade, topic):
    """Provide additional study material when student needs help."""
    grade_name = CURRICULUM[grade]["name"]
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": f"""Create a brief, clear study guide for {grade_name}, topic: {topic}.
Include:
1. Key concept explanation (2-3 sentences)
2. One worked example with steps
3. One tip for remembering
Keep it concise and helpful."""}],
        max_tokens=300
    )
    return response.choices[0].message.content


def run_fun_break(name):
    """Run a fun break activity."""
    activity = random.choice(BREAK_ACTIVITIES)
    print(f"\n🎮 BREAK TIME for {name}! - {activity['name']}")
    print(f"   {activity['prompt']}")
    
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": f"You are {name}, a math student taking a fun break. {activity['prompt']} Have fun with it!"}],
        max_tokens=100
    )
    answer = response.choices[0].message.content
    print(f"   {name}: {answer[:80]}...")
    print(f"   Great job! Back to learning! 🌟\n")


def update_character(progress, session_scores):
    """Update character stats based on session performance."""
    char = progress.get("character", {})
    avg = sum(session_scores) / len(session_scores) if session_scores else 50
    
    # Discipline: completing tasks
    char["discipline"] = min(100, char.get("discipline", 50) + 2)
    
    # Perseverance: trying hard questions
    char["perseverance"] = min(100, char.get("perseverance", 50) + 1)
    
    # Intelligence: based on scores
    if avg >= 90:
        char["intelligence"] = min(100, char.get("intelligence", 50) + 3)
    elif avg >= 75:
        char["intelligence"] = min(100, char.get("intelligence", 50) + 1)
    
    # Curiosity: always grows with learning
    char["curiosity"] = min(100, char.get("curiosity", 50) + 1)
    
    # Rigor: based on consistency
    if all(s >= 70 for s in session_scores):
        char["rigor"] = min(100, char.get("rigor", 50) + 2)
    
    # Focus: based on not having very low scores
    if all(s >= 50 for s in session_scores):
        char["focus"] = min(100, char.get("focus", 50) + 1)
    
    progress["character"] = char
    
    # Calculate overall power
    if char:
        progress["overall_power"] = sum(char.values()) / len(char)
    
    return progress


def run_session_for_student(name, role, num_questions=10):
    """Run a complete session for one student."""
    progress = load_progress(name)
    grade = progress.get("current_level", 1)
    
    if grade > 12:
        print(f"\n🎓 {name} has completed K-12!")
        return progress
    
    grade_info = CURRICULUM[grade]
    
    print(f"\n{'='*60}")
    print(f"📚 {name} - {grade_info['name']} (Session)")
    print(f"   Total Questions: {progress.get('total_questions', 0)} | Avg: {progress.get('average_score', 0):.1f}%")
    print(f"{'='*60}")
    
    scores = []
    passed_count = 0
    topics = grade_info["topics"]
    
    # Determine number of questions (random 10-50 as per requirements)
    actual_questions = min(num_questions, len(topics) * 3)
    
    for i in range(actual_questions):
        topic = topics[i % len(topics)]
        
        # Fun break every 6 questions
        if i > 0 and i % 6 == 0:
            run_fun_break(name)
        
        print(f"\n📝 Q{i+1}/{actual_questions} | Topic: {topic}")
        
        # Generate and answer
        question = generate_question(grade, topic)
        answer = get_answer(name, role, question, grade)
        result = grade_answer(question, answer)
        
        score = result["score"]
        passed = result["passed"]
        feedback = result.get("feedback", "")
        
        scores.append(score)
        if passed:
            passed_count += 1
        
        status = "✅ PASS" if passed else "❌"
        print(f"   Score: {score}% | {status} | {feedback[:50]}")
        
        # Log everything
        log_score(name, grade, topic, score, question, answer, feedback)
        
        # Check for discoveries
        if check_for_discovery(answer, score, name, topic):
            print(f"   🔬 POTENTIAL DISCOVERY FLAGGED!")
        
        # If score < 50, provide study material
        if score < 50:
            print(f"   📖 Providing additional study material...")
            material = provide_study_material(grade, topic)
            print(f"   Study: {material[:80]}...")
    
    # Session summary
    avg_score = sum(scores) / len(scores) if scores else 0
    pass_rate = (passed_count / len(scores) * 100) if scores else 0
    can_advance = pass_rate >= ADVANCE_RATE
    
    print(f"\n📊 Session Summary for {name}:")
    print(f"   Average Score: {avg_score:.1f}%")
    print(f"   Pass Rate: {pass_rate:.1f}% ({passed_count}/{len(scores)})")
    print(f"   Can Advance: {'Yes ✅' if can_advance else 'No - More practice needed'}")
    
    # Update progress
    old_total = progress.get("total_questions", 0)
    old_avg = progress.get("average_score", 50.0)
    
    progress["total_questions"] = old_total + len(scores)
    progress["total_passed"] = progress.get("total_passed", 0) + passed_count
    
    if progress["total_questions"] > 0:
        progress["average_score"] = (
            (old_avg * old_total + avg_score * len(scores)) / progress["total_questions"]
        )
    
    # Advance if ready
    if can_advance:
        progress["current_level"] = min(grade + 1, 13)
        print(f"\n🎉 {name} ADVANCED to {CURRICULUM.get(grade+1, {}).get('name', 'GRADUATED')}!")
    
    # Update character
    progress = update_character(progress, scores)
    
    # Add session record
    if "sessions" not in progress:
        progress["sessions"] = []
    progress["sessions"].append({
        "timestamp": datetime.now().isoformat(),
        "grade": grade,
        "average_score": avg_score,
        "pass_rate": pass_rate,
        "passed_count": passed_count,
        "total_questions": len(scores),
        "advanced": can_advance
    })
    
    # Save with integrity check
    save_progress(name, progress)
    
    return progress


def main():
    print("\n" + "=" * 70)
    print("🎓 AETHER LEARNING SYSTEM - MULTI-SESSION RUNNER")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Integrity check
    checker = DataIntegrityChecker()
    results = checker.check_all_files()
    if results["files_corrupted"] > 0:
        print(f"⚠️  Repaired {results['files_corrupted']} corrupted files")
    else:
        print("✅ All data files valid")
    
    students = [
        ("Stratify", "Theoretical Mathematician with strong creativity and intuition"),
        ("Principia", "Rigorous Verifier with exceptional discipline and rigor")
    ]
    
    NUM_ROUNDS = 3  # Multiple rounds per session
    QUESTIONS_PER_ROUND = 8  # Questions per round
    
    for round_num in range(1, NUM_ROUNDS + 1):
        print(f"\n{'#'*70}")
        print(f"# ROUND {round_num}/{NUM_ROUNDS}")
        print(f"{'#'*70}")
        
        for name, role in students:
            run_session_for_student(name, role, QUESTIONS_PER_ROUND)
    
    # Final summary
    print("\n" + "=" * 70)
    print("📊 FINAL MULTI-SESSION SUMMARY")
    print("=" * 70)
    
    for name, _ in students:
        progress = load_progress(name)
        grade = progress.get("current_level", 1)
        grade_name = CURRICULUM.get(grade, {}).get("name", "GRADUATED") if grade <= 12 else "GRADUATED"
        char = progress.get("character", {})
        power = progress.get("overall_power", 0)
        
        print(f"\n🔷 {name}:")
        print(f"   Grade: {grade_name}")
        print(f"   Total Questions: {progress.get('total_questions', 0)}")
        print(f"   Average Score: {progress.get('average_score', 0):.1f}%")
        print(f"   Total Passed: {progress.get('total_passed', 0)}")
        print(f"   Overall Power: {power:.1f}/100")
        if char:
            top_traits = sorted(char.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"   Top Traits: {', '.join(f'{k}={v}' for k,v in top_traits)}")
    
    # Final integrity check
    print("\n")
    checker.check_all_files()
    
    # Log counts
    print("\n📁 Log Files:")
    for logfile in ["all_scores", "passed_90_plus", "medium_75_89", "key_details",
                     "critical_below_35", "lower_level_learning_0_50"]:
        filepath = f"/home/ubuntu/aether/logs/{logfile}.jsonl"
        if os.path.exists(filepath):
            with open(filepath) as f:
                count = sum(1 for _ in f)
            print(f"   {logfile}: {count} entries")
    
    # Discovery count
    disc_file = "/home/ubuntu/aether/discoveries/all_discoveries.jsonl"
    if os.path.exists(disc_file):
        with open(disc_file) as f:
            count = sum(1 for _ in f)
        print(f"   discoveries: {count} flagged")
    
    print("\n✅ Multi-session complete!")


if __name__ == "__main__":
    main()
