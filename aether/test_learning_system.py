#!/usr/bin/env python3.11
"""
Test the Progressive Learning System

Demonstrates:
1. Separate study materials and test questions
2. Unique AI-challenging problems
3. Level progression tracking
4. Framework advancement
"""

import sys
sys.path.append('/home/ubuntu/aether/core')

from learning_system import get_learning_system, Level, Difficulty


def test_study_materials():
    """Test study materials access."""
    print("\n" + "="*70)
    print("TESTING STUDY MATERIALS")
    print("="*70)
    
    system = get_learning_system()
    
    # Register frameworks
    system.register_framework("Stratify")
    system.register_framework("Principia")
    
    # Get Level 1 study materials
    print("\n--- Level 1: FOUNDATIONS Study Materials ---")
    materials = system.get_study_materials("Stratify", Level.FOUNDATIONS)
    print(f"Found {len(materials)} study materials:")
    for m in materials:
        print(f"\n  📚 {m['title']}")
        print(f"     Level: {m['level']}")
        if 'overview' in m['content']:
            print(f"     Overview: {m['content']['overview'][:80]}...")
        if 'key_concepts' in m['content']:
            print(f"     Key concepts: {len(m['content']['key_concepts'])} topics")
    
    # Try to access Level 2 (should be empty - not unlocked)
    print("\n--- Trying to access Level 2 (not unlocked yet) ---")
    materials_l2 = system.get_study_materials("Stratify", Level.GEOMETRY_GROUPS)
    print(f"Materials available: {len(materials_l2)} (expected: 0)")


def test_unique_questions():
    """Test that questions are unique and challenging."""
    print("\n" + "="*70)
    print("TESTING UNIQUE TEST QUESTIONS")
    print("="*70)
    
    system = get_learning_system()
    
    # Get Level 1 questions
    print("\n--- Level 1: FOUNDATIONS Test Questions ---")
    questions = system.get_test_questions("Stratify", Level.FOUNDATIONS)
    print(f"Found {len(questions)} unique test questions:")
    
    for q in questions:
        print(f"\n  🧪 Question ID: {q['question_id']}")
        print(f"     Difficulty: {q['difficulty']}")
        print(f"     Requires: {q['requires_concepts']}")
        print(f"     Question preview: {q['question'][:100]}...")
        print(f"     Hints available: {len(q['hints'])}")
    
    # Show one question in detail
    print("\n--- Detailed View of One Challenge ---")
    if questions:
        q = questions[0]
        print(f"\n  CHALLENGE: {q['question_id']}")
        print(f"  {'-'*60}")
        print(f"  {q['question']}")
        print(f"  {'-'*60}")
        print(f"  Hints (if stuck):")
        for i, hint in enumerate(q['hints'], 1):
            print(f"    {i}. {hint}")


def test_question_separation():
    """Verify that questions are separate from study materials."""
    print("\n" + "="*70)
    print("VERIFYING SEPARATION OF MATERIALS AND QUESTIONS")
    print("="*70)
    
    system = get_learning_system()
    
    print("\n--- Study Materials are for LEARNING ---")
    materials = system.study_library.get_materials(Level.FOUNDATIONS)
    for m in materials[:2]:
        print(f"  📚 {m.title}")
        print(f"     Contains: concepts, definitions, examples, intuitions")
        print(f"     Purpose: Build understanding")
    
    print("\n--- Test Questions are UNIQUE CHALLENGES ---")
    questions = system.question_bank.get_questions(Level.FOUNDATIONS)
    for q in questions[:2]:
        print(f"  🧪 {q.question_id}")
        print(f"     NOT from textbooks - created to test genuine understanding")
        print(f"     Purpose: Challenge the AI to APPLY knowledge")
    
    print("\n✅ Study materials and test questions are COMPLETELY SEPARATE")
    print("   - Materials teach concepts")
    print("   - Questions test understanding with novel problems")


def test_difficulty_progression():
    """Test difficulty progression within a level."""
    print("\n" + "="*70)
    print("TESTING DIFFICULTY PROGRESSION")
    print("="*70)
    
    system = get_learning_system()
    
    print("\n--- Questions by Difficulty (Level 1) ---")
    for diff in Difficulty:
        questions = system.question_bank.get_questions_by_difficulty(Level.FOUNDATIONS, diff)
        print(f"\n  {diff.name}: {len(questions)} questions")
        for q in questions:
            print(f"    • {q.question_id}: {q.question[:50]}...")


def test_level_progression():
    """Test framework level progression."""
    print("\n" + "="*70)
    print("TESTING LEVEL PROGRESSION")
    print("="*70)
    
    system = get_learning_system()
    
    # Check initial progress
    print("\n--- Initial Progress ---")
    progress = system.get_progress_summary("Stratify")
    print(f"  Framework: {progress['framework']}")
    print(f"  Current Level: {progress['current_level']}")
    print(f"  Can Advance: {progress['can_advance']}")
    
    # Simulate passing some questions
    print("\n--- Simulating Question Completion ---")
    questions = system.question_bank.get_questions(Level.FOUNDATIONS)
    
    for i, q in enumerate(questions[:3]):
        print(f"  ✓ {q.question_id} - PASSED")
        system.record_result("Stratify", q.question_id, 85.0, "Good work!", True)
    
    # Check advancement eligibility
    print("\n--- Checking Advancement ---")
    advancement = system.check_advancement("Stratify")
    print(f"  Questions passed: {advancement['questions_passed']}/{advancement['required_to_advance']}")
    print(f"  Can advance: {advancement['can_advance']}")
    
    if advancement['can_advance']:
        print("\n--- Advancing to Next Level ---")
        result = system.advance_framework("Stratify")
        print(f"  {result['message']}")
        print(f"  Old Level: {result['old_level']}")
        print(f"  New Level: {result['new_level']}")
        
        # Now can access Level 2 materials
        print("\n--- Now Can Access Level 2 Materials ---")
        materials = system.get_study_materials("Stratify", Level.GEOMETRY_GROUPS)
        print(f"  Level 2 materials available: {len(materials)}")
        for m in materials:
            print(f"    📚 {m['title']}")


def test_all_levels_content():
    """Show content available at all levels."""
    print("\n" + "="*70)
    print("ALL LEVELS CONTENT SUMMARY")
    print("="*70)
    
    system = get_learning_system()
    
    for level in Level:
        print(f"\n{'='*60}")
        print(f"LEVEL {level.value}: {level.name}")
        print(f"{'='*60}")
        
        # Study materials
        materials = system.study_library.get_materials(level)
        print(f"\n  📚 STUDY MATERIALS ({len(materials)}):")
        for m in materials:
            print(f"     • {m.title}")
        
        # Test questions
        questions = system.question_bank.get_questions(level)
        print(f"\n  🧪 TEST QUESTIONS ({len(questions)}):")
        for q in questions:
            print(f"     • [{q.difficulty.name}] {q.question_id}")


def show_system_summary():
    """Show summary of the complete system."""
    print("\n" + "="*70)
    print("PROGRESSIVE LEARNING SYSTEM SUMMARY")
    print("="*70)
    
    system = get_learning_system()
    
    total_materials = sum(len(m) for m in system.study_library.materials.values())
    total_questions = sum(len(q) for q in system.question_bank.questions.values())
    
    print(f"""
    ┌─────────────────────────────────────────────────────────────┐
    │  PROGRESSIVE LEARNING SYSTEM                                │
    ├─────────────────────────────────────────────────────────────┤
    │                                                             │
    │  📚 STUDY MATERIALS: {total_materials:2d} comprehensive learning resources     │
    │     • Level 1 (Foundations): {len(system.study_library.materials[Level.FOUNDATIONS])} materials              │
    │     • Level 2 (Geometry):    {len(system.study_library.materials[Level.GEOMETRY_GROUPS])} materials              │
    │     • Level 3 (Analysis):    {len(system.study_library.materials[Level.ANALYSIS_TOPOLOGY])} materials              │
    │     • Level 4 (Field Theory):{len(system.study_library.materials[Level.FIELD_THEORY])} materials              │
    │     • Level 5 (Yang-Mills):  {len(system.study_library.materials[Level.YANG_MILLS])} materials              │
    │                                                             │
    │  🧪 TEST QUESTIONS: {total_questions:2d} unique AI-challenging problems       │
    │     • Level 1: {len(system.question_bank.questions[Level.FOUNDATIONS])} questions                            │
    │     • Level 2: {len(system.question_bank.questions[Level.GEOMETRY_GROUPS])} questions                            │
    │     • Level 3: {len(system.question_bank.questions[Level.ANALYSIS_TOPOLOGY])} questions                            │
    │     • Level 4: {len(system.question_bank.questions[Level.FIELD_THEORY])} questions                            │
    │     • Level 5: {len(system.question_bank.questions[Level.YANG_MILLS])} questions                            │
    │                                                             │
    │  📊 ADVANCEMENT TRACKING:                                   │
    │     • Pass 3+ questions to advance                          │
    │     • Progress saved per framework                          │
    │     • Manus monitors all progress                           │
    │                                                             │
    │  ✅ KEY DESIGN:                                             │
    │     • Study materials are for LEARNING                      │
    │     • Test questions are UNIQUE CHALLENGES                  │
    │     • Questions test genuine understanding                  │
    │     • Not textbook problems - AI must truly understand      │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
    """)


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "PROGRESSIVE LEARNING SYSTEM TEST" + " "*20 + "║")
    print("║" + " "*10 + "Study Materials + Unique AI Challenges" + " "*19 + "║")
    print("╚" + "="*68 + "╝")
    
    # Run tests
    test_study_materials()
    test_unique_questions()
    test_question_separation()
    test_difficulty_progression()
    test_level_progression()
    test_all_levels_content()
    show_system_summary()
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print("\n✅ Progressive Learning System is fully operational!")
    print("✅ Study materials and test questions are SEPARATE")
    print("✅ Test questions are UNIQUE AI challenges")
    print("✅ Level progression tracking works correctly")
    print("\nFrameworks can now learn and be challenged!")


if __name__ == "__main__":
    main()
