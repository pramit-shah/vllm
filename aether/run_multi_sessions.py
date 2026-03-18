#!/usr/bin/env python3
"""
AETHER Learning System - Optimized Multi-Session Runner
Faster execution, robust grading, comprehensive logging.
"""

import json
import os
import sys
import random
import re
from datetime import datetime
from openai import OpenAI

sys.path.insert(0, '/home/ubuntu/aether')
from core.data_integrity import DataIntegrityChecker

# LoRA training data collection
try:
    from vllm_integration.lora_data_collector import LoRADataCollector
    lora_collector = LoRADataCollector()
    COLLECT_LORA = True
except Exception:
    COLLECT_LORA = False

client = OpenAI()

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
    10: {"name": "Grade 10 - Geometry", "topics": ["geometric_proofs", "triangle_congruence", "similarity", "trigonometry_intro", "logical_reasoning", "proof_structure"]},
    # Added logical_reasoning and proof_structure to help break through the proof plateau
    11: {"name": "Grade 11 - Algebra II", "topics": ["complex_numbers", "logarithms", "sequences_series", "conic_sections"]},
    12: {"name": "Grade 12 - Calculus", "topics": ["derivatives", "integrals", "differential_equations_intro", "applications_of_calculus"]},
}

PASS_THRESHOLD = 95
ADVANCE_RATE = 75

BREAK_ACTIVITIES = [
    "What comes next: 1, 1, 2, 3, 5, 8, 13, ?",
    "What's the pattern: 2, 6, 12, 20, 30, ?",
    "Fill a 3x3 grid with 1-9 so all rows/columns/diagonals sum to 15",
]


def load_progress(name):
    filepath = f"/home/ubuntu/aether/memory/{name.lower()}_full_record.json"
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except:
        return {"name": name, "total_questions": 0, "total_passed": 0,
                "average_score": 50.0, "current_level": 1, "sessions": [],
                "character": {}}


def save_progress(name, data):
    filepath = f"/home/ubuntu/aether/memory/{name.lower()}_full_record.json"
    data["last_updated"] = datetime.now().isoformat()
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def log_score(name, grade, topic, score, question, answer, feedback):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "framework": name, "grade": grade, "topic": topic,
        "score": score, "question_preview": question[:100],
        "answer_preview": answer[:100], "feedback": feedback
    }
    with open("/home/ubuntu/aether/logs/all_scores.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")
    if score >= 90:
        with open("/home/ubuntu/aether/logs/passed_90_plus.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")
    elif score >= 75:
        with open("/home/ubuntu/aether/logs/medium_75_89.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")
    elif score >= 50:
        with open("/home/ubuntu/aether/logs/key_details.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")
    else:
        with open("/home/ubuntu/aether/logs/critical_below_35.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")
    # Record conversations
    folder = "high_score_75_plus" if score >= 75 else "low_score_74_minus"
    with open(f"/home/ubuntu/aether/records/{folder}/conversations.jsonl", "a") as f:
        f.write(json.dumps({**entry, "full_answer": answer}) + "\n")


def check_for_discovery(answer, score, name, topic):
    indicators = ["novel", "new approach", "alternatively", "my own method",
                   "I discovered", "unique solution", "different way",
                   "generalize", "pattern I noticed", "conjecture"]
    found = any(ind.lower() in answer.lower() for ind in indicators)
    if found and score >= 35:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "framework": name, "topic": topic, "score": score,
            "type": "potential_discovery",
            "answer_preview": answer[:300],
            "status": "AWAITING_MANUS_REVIEW"
        }
        with open("/home/ubuntu/aether/discoveries/all_discoveries.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")
        return True
    return False


def ask_and_grade(name, role, grade, topic):
    """Combined: generate question, get answer, grade - all in fewer API calls."""
    grade_name = CURRICULUM[grade]["name"]
    
    # Generate question
    q_resp = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": f"Create ONE specific math problem for {grade_name}, topic: {topic}. Just the problem, no hints. Be specific with numbers."}],
        max_tokens=150, temperature=0.8
    )
    question = q_resp.choices[0].message.content
    
    # Get answer
    a_resp = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": f"You are {name}, a {role} AI student in {grade_name}.\nSolve step-by-step:\n{question}"}],
        max_tokens=400, temperature=0.7
    )
    answer = a_resp.choices[0].message.content
    
    # Grade - with robust parsing
    g_resp = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": f"""Grade this math answer 0-100. Be fair and accurate.
Q: {question}
A: {answer}

Scoring: Correctness(50) + Reasoning(30) + Clarity(20)
Reply ONLY with JSON: {{"score": <number>, "feedback": "<one sentence>"}}"""}],
        max_tokens=80, temperature=0.2
    )
    
    # Parse grade
    g_text = g_resp.choices[0].message.content.strip()
    score = 80  # reasonable default
    feedback = "Graded"
    
    try:
        start = g_text.find('{')
        end = g_text.rfind('}') + 1
        if start >= 0 and end > start:
            result = json.loads(g_text[start:end])
            score = max(0, min(100, int(result.get("score", 80))))
            feedback = result.get("feedback", "Graded")
        else:
            nums = re.findall(r'\d+', g_text)
            if nums:
                score = max(0, min(100, int(nums[0])))
    except:
        nums = re.findall(r'\d+', g_text)
        if nums:
            score = max(0, min(100, int(nums[0])))
    
    return question, answer, score, feedback


def update_character(progress, session_scores):
    char = progress.get("character", {})
    avg = sum(session_scores) / len(session_scores) if session_scores else 50
    
    char["discipline"] = min(100, char.get("discipline", 50) + 2)
    char["perseverance"] = min(100, char.get("perseverance", 50) + 1)
    char["curiosity"] = min(100, char.get("curiosity", 50) + 1)
    
    if avg >= 90:
        char["intelligence"] = min(100, char.get("intelligence", 50) + 3)
    elif avg >= 75:
        char["intelligence"] = min(100, char.get("intelligence", 50) + 1)
    
    if all(s >= 70 for s in session_scores):
        char["rigor"] = min(100, char.get("rigor", 50) + 2)
    if all(s >= 50 for s in session_scores):
        char["focus"] = min(100, char.get("focus", 50) + 1)
    
    # Wisdom grows with grade level
    grade = progress.get("current_level", 1)
    char["wisdom"] = min(100, char.get("wisdom", 50) + (1 if grade >= 6 else 0))
    
    # Creativity for high scores
    if any(s >= 95 for s in session_scores):
        char["creativity"] = min(100, char.get("creativity", 50) + 1)
    
    # Collaboration grows each session
    char["collaboration"] = min(100, char.get("collaboration", 50) + 1)
    
    # Intuition for pattern recognition
    char["intuition"] = min(100, char.get("intuition", 50) + (1 if avg >= 85 else 0))
    
    progress["character"] = char
    if char:
        progress["overall_power"] = sum(char.values()) / len(char)
    return progress


def run_session(name, role, num_questions=10):
    progress = load_progress(name)
    grade = progress.get("current_level", 1)
    
    if grade > 12:
        print(f"🎓 {name} has GRADUATED K-12!")
        return progress
    
    grade_info = CURRICULUM[grade]
    topics = grade_info["topics"]
    
    print(f"\n{'='*55}")
    print(f"📚 {name} - {grade_info['name']} | Q:{progress.get('total_questions',0)} | Avg:{progress.get('average_score',0):.0f}%")
    print(f"{'='*55}")
    
    scores = []
    passed = 0
    
    for i in range(num_questions):
        topic = topics[i % len(topics)]
        
        # Fun break every 8 questions
        if i > 0 and i % 8 == 0:
            print(f"  🎮 Break time!")
        
        question, answer, score, feedback = ask_and_grade(name, role, grade, topic)
        
        is_pass = score >= PASS_THRESHOLD
        scores.append(score)
        if is_pass:
            passed += 1
        
        status = "✅" if is_pass else "❌"
        print(f"  Q{i+1}: {topic[:20]:20s} | {score:3d}% {status} | {feedback[:40]}")
        
        log_score(name, grade, topic, score, question, answer, feedback)
        
        # Collect high-quality answers for LoRA fine-tuning
        if COLLECT_LORA and score >= 90:
            lora_collector.add_example(
                framework=name, question=question, answer=answer,
                score=score, topic=topic, grade=grade, feedback=feedback
            )
        
        if check_for_discovery(answer, score, name, topic):
            print(f"       🔬 DISCOVERY FLAGGED!")
    
    avg = sum(scores) / len(scores) if scores else 0
    pass_rate = (passed / len(scores) * 100) if scores else 0
    can_advance = pass_rate >= ADVANCE_RATE
    
    print(f"  ─── Avg: {avg:.0f}% | Pass: {pass_rate:.0f}% ({passed}/{len(scores)}) | {'ADVANCE ✅' if can_advance else 'PRACTICE'}")
    
    # Update progress
    old_total = progress.get("total_questions", 0)
    old_avg = progress.get("average_score", 50.0)
    progress["total_questions"] = old_total + len(scores)
    progress["total_passed"] = progress.get("total_passed", 0) + passed
    if progress["total_questions"] > 0:
        progress["average_score"] = (old_avg * old_total + avg * len(scores)) / progress["total_questions"]
    
    if can_advance:
        progress["current_level"] = min(grade + 1, 13)
        next_name = CURRICULUM.get(grade + 1, {}).get("name", "GRADUATED")
        print(f"  🎉 {name} → {next_name}!")
    
    progress = update_character(progress, scores)
    
    if "sessions" not in progress:
        progress["sessions"] = []
    progress["sessions"].append({
        "timestamp": datetime.now().isoformat(),
        "grade": grade, "average_score": avg,
        "pass_rate": pass_rate, "passed_count": passed,
        "total_questions": len(scores), "advanced": can_advance
    })
    
    save_progress(name, progress)
    return progress


def main():
    print("=" * 55)
    print("🎓 AETHER LEARNING SYSTEM")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 55)
    
    # Integrity check
    checker = DataIntegrityChecker()
    results = checker.check_all_files()
    print(f"{'✅' if results['files_corrupted'] == 0 else '⚠️'} Data integrity check complete")
    
    students = [
        ("Stratify", "Theoretical Mathematician with strong creativity and intuition"),
        ("Principia", "Rigorous Verifier with exceptional discipline and rigor")
    ]
    
    NUM_ROUNDS = 3
    QUESTIONS_PER_ROUND = 12
    
    for rnd in range(1, NUM_ROUNDS + 1):
        print(f"\n{'#'*55}")
        print(f"# ROUND {rnd}/{NUM_ROUNDS}")
        print(f"{'#'*55}")
        
        for name, role in students:
            run_session(name, role, QUESTIONS_PER_ROUND)
    
    # Final summary
    print("\n" + "=" * 55)
    print("📊 FINAL SUMMARY")
    print("=" * 55)
    
    for name, _ in students:
        p = load_progress(name)
        g = p.get("current_level", 1)
        gn = CURRICULUM.get(g, {}).get("name", "GRADUATED") if g <= 12 else "GRADUATED"
        char = p.get("character", {})
        
        print(f"\n🔷 {name}: {gn}")
        print(f"   Questions: {p.get('total_questions',0)} | Avg: {p.get('average_score',0):.1f}% | Passed: {p.get('total_passed',0)}")
        print(f"   Power: {p.get('overall_power',0):.1f}/100")
        if char:
            top = sorted(char.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"   Top: {', '.join(f'{k}={v}' for k,v in top)}")
    
    # Log counts
    print("\n📁 Logs:")
    for lf in ["all_scores", "passed_90_plus", "medium_75_89", "key_details", "critical_below_35"]:
        fp = f"/home/ubuntu/aether/logs/{lf}.jsonl"
        if os.path.exists(fp):
            with open(fp) as f:
                c = sum(1 for _ in f)
            print(f"   {lf}: {c}")
    
    disc = "/home/ubuntu/aether/discoveries/all_discoveries.jsonl"
    if os.path.exists(disc):
        with open(disc) as f:
            c = sum(1 for _ in f)
        print(f"   discoveries: {c}")
    
    # Save LoRA training data
    if COLLECT_LORA:
        stats = lora_collector.save()
        print(f"\n📊 LoRA Data: {stats.get('total_examples', 0)} high-quality examples collected")
    
    print("\n✅ Complete!")


if __name__ == "__main__":
    main()
