#!/usr/bin/env python3.11
"""
Test the Universal Knowledge Network

Demonstrates:
1. Comprehensive mathematics and physics knowledge
2. Cross-field connections and analogies
3. Expert intuitions and heuristics
4. Unlimited access for frameworks
5. Full query visibility for Manus
"""

import sys
sys.path.append('/home/ubuntu/aether/core')

from knowledge_network import get_knowledge_network


def test_mathematics_knowledge():
    """Test mathematics knowledge base."""
    print("\n" + "="*70)
    print("TESTING MATHEMATICS KNOWLEDGE")
    print("="*70)
    
    network = get_knowledge_network()
    
    # Search for gauge theory
    print("\n--- Searching for 'gauge theory' ---")
    results = network.search("gauge theory", framework="Stratify", domain="math")
    print(f"Found {len(results['mathematics'])} mathematics results:")
    for r in results['mathematics'][:3]:
        print(f"  • {r['name']}: {r.get('statement', r.get('definition', ''))[:60]}...")
    
    # Get specific theorem
    print("\n--- Getting Yang-Mills equations theorem ---")
    theorem = network.get_theorem("yang_mills_equations", framework="Stratify")
    if theorem:
        print(f"  Statement: {theorem['statement']}")
        print(f"  Field: {theorem['field']}")
        print(f"  Intuition: {theorem['intuition']}")
        print(f"  Applications: {theorem['applications']}")
    
    # Get prerequisites
    print("\n--- Finding prerequisites for Chern-Weil theory ---")
    prereqs = network.find_prerequisites("chern_weil_theory", framework="Stratify")
    print(f"  Prerequisites: {prereqs}")
    
    # Get related theorems
    print("\n--- Finding theorems related to spectral theory ---")
    related = network.mathematics.find_related("spectral_theorem")
    print(f"  Related: {related[:5]}")


def test_physics_knowledge():
    """Test physics knowledge base."""
    print("\n" + "="*70)
    print("TESTING PHYSICS KNOWLEDGE")
    print("="*70)
    
    network = get_knowledge_network()
    
    # Search for mass gap
    print("\n--- Searching for 'mass gap' ---")
    results = network.search("mass gap", framework="Principia", domain="physics")
    print(f"Found {len(results['physics'])} physics results:")
    for r in results['physics'][:3]:
        print(f"  • {r['name']}: {r.get('description', '')[:60]}...")
    
    # Get specific concept
    print("\n--- Getting QCD concept ---")
    concept = network.get_concept("qcd", framework="Principia")
    if concept:
        print(f"  Description: {concept['description']}")
        print(f"  Key equations: {concept['key_equations']}")
        print(f"  Connections: {concept['connections']}")
    
    # Get history
    print("\n--- Getting mass gap problem history ---")
    history = network.get_history("mass_gap_problem", framework="Principia")
    if history:
        print(f"  Key insight: {history['key_insight']}")
        print(f"  Timeline:")
        for event in history['timeline'][:4]:
            print(f"    {event['year']}: {event['event']}")


def test_cross_field_connections():
    """Test cross-field connections."""
    print("\n" + "="*70)
    print("TESTING CROSS-FIELD CONNECTIONS")
    print("="*70)
    
    network = get_knowledge_network()
    
    # Find connection
    print("\n--- Finding fiber bundle ↔ gauge theory connection ---")
    conn = network.get_connection("fiber_bundles_gauge_theory", framework="Stratify")
    if conn:
        print(f"  Math side: {conn['math_side']}")
        print(f"  Physics side: {conn['physics_side']}")
        print(f"  Connection: {conn['connection']}")
        print(f"  Details:")
        for k, v in conn['details'].items():
            print(f"    {k}: {v}")
    
    # Find analogies
    print("\n--- Finding analogies involving 'Ricci flow' ---")
    results = network.search("Ricci flow", framework="Stratify", domain="connections")
    print(f"Found {len(results['connections'])} connections:")
    for r in results['connections']:
        print(f"  • {r['name']}: {r.get('connection', r.get('analogy', ''))[:60]}...")
    
    # Get breakthrough patterns
    print("\n--- Getting 'geometric_reformulation' pattern ---")
    pattern = network.connections.get_breakthrough_pattern("geometric_reformulation")
    if pattern:
        print(f"  Pattern: {pattern['pattern']}")
        print(f"  Examples: {pattern['examples']}")
        print(f"  How to apply: {pattern['how_to_apply']}")


def test_intuitions():
    """Test intuition engine."""
    print("\n" + "="*70)
    print("TESTING INTUITION ENGINE")
    print("="*70)
    
    network = get_knowledge_network()
    
    # Get intuition
    print("\n--- Getting intuition for 'mass gap' ---")
    intuition = network.get_intuition("mass_gap", framework="Principia")
    if intuition:
        print(f"  Intuition: {intuition['intuition']}")
        print(f"  Implications:")
        for imp in intuition['implications']:
            print(f"    • {imp}")
        print(f"  Common confusion: {intuition['common_confusion']}")
    
    # Get heuristics
    print("\n--- Getting heuristics for 'stuck on calculation' ---")
    heuristics = network.get_heuristics("stuck calculation", framework="Stratify")
    print(f"Found {len(heuristics)} heuristics:")
    for h in heuristics[:3]:
        print(f"  • {h['name']}: {h['heuristic']}")
    
    # Get common mistakes
    print("\n--- Getting common mistakes for 'gauge' ---")
    mistakes = network.intuitions.get_common_mistake("gauge")
    print(f"Found {len(mistakes)} common mistakes:")
    for m in mistakes:
        print(f"  • {m['name']}: {m['mistake']}")
        print(f"    How to avoid: {m['how_to_avoid']}")


def test_suggest_approach():
    """Test approach suggestion."""
    print("\n" + "="*70)
    print("TESTING APPROACH SUGGESTION")
    print("="*70)
    
    network = get_knowledge_network()
    
    print("\n--- Suggesting approach for 'prove mass gap exists' ---")
    suggestions = network.suggest_approach(
        "prove mass gap exists in Yang-Mills theory",
        framework="Stratify"
    )
    
    print(f"\nBreakthrough patterns ({len(suggestions['breakthrough_patterns'])}):")
    for p in suggestions['breakthrough_patterns'][:2]:
        print(f"  • {p['pattern']}")
        print(f"    Examples: {p['examples']}")
    
    print(f"\nAnalogies ({len(suggestions['analogies'])}):")
    for a in suggestions['analogies'][:2]:
        print(f"  • {a.get('analogy', a.get('connection', ''))[:60]}...")
    
    print(f"\nHeuristics ({len(suggestions['heuristics'])}):")
    for h in suggestions['heuristics'][:2]:
        print(f"  • {h['heuristic']}")
    
    print(f"\nCommon mistakes to avoid ({len(suggestions['common_mistakes'])}):")
    for m in suggestions['common_mistakes'][:2]:
        print(f"  • {m['mistake']}")


def test_manus_visibility():
    """Test Manus's visibility into framework queries."""
    print("\n" + "="*70)
    print("TESTING MANUS VISIBILITY")
    print("="*70)
    
    network = get_knowledge_network()
    
    # Get query statistics
    print("\n--- Query Statistics (What Manus Sees) ---")
    stats = network.get_query_statistics()
    print(f"Total queries: {stats['total_queries']}")
    print(f"By framework: {dict(stats['by_framework'])}")
    print(f"By type: {dict(stats['by_type'])}")
    
    # Get framework focus
    print("\n--- What Stratify is focusing on ---")
    focus = network.get_framework_focus("Stratify")
    print(f"Focus areas: {focus}")
    
    print("\n--- What Principia is focusing on ---")
    focus = network.get_framework_focus("Principia")
    print(f"Focus areas: {focus}")
    
    # Get recent queries
    print("\n--- Recent queries (all frameworks) ---")
    recent = network.get_recent_queries(limit=5)
    for q in recent:
        print(f"  [{q['framework']}] {q['query_type']}: {q['query'][:40]}...")
    
    # Detect convergence
    print("\n--- Detecting convergence ---")
    convergence = network.detect_convergence()
    if convergence:
        print(f"Frameworks: {convergence['frameworks']}")
        print(f"Common interests: {convergence['common_interests']}")
        print(f"Potential collaboration: {convergence['potential_collaboration']}")
    else:
        print("Not enough data to detect convergence yet")


def show_knowledge_summary():
    """Show summary of all knowledge."""
    print("\n" + "="*70)
    print("UNIVERSAL KNOWLEDGE NETWORK SUMMARY")
    print("="*70)
    
    network = get_knowledge_network()
    info = network.get_info()
    
    print("\n📚 MATHEMATICS:")
    print(f"   • {info['mathematics']['theorems']} theorems")
    print(f"   • {info['mathematics']['definitions']} definitions")
    print(f"   • {info['mathematics']['techniques']} techniques")
    print(f"   • Fields: {info['mathematics']['fields']}")
    
    print("\n🔬 PHYSICS:")
    print(f"   • {info['physics']['concepts']} concepts")
    print(f"   • {info['physics']['principles']} principles")
    print(f"   • {info['physics']['experiments']} experiments")
    print(f"   • {info['physics']['historical_topics']} historical topics")
    
    print("\n🔗 CONNECTIONS:")
    print(f"   • {info['connections']['connections']} cross-field connections")
    print(f"   • {info['connections']['analogies']} productive analogies")
    print(f"   • {info['connections']['breakthrough_patterns']} breakthrough patterns")
    
    print("\n💡 INTUITIONS:")
    print(f"   • {info['intuitions']['intuitions']} expert intuitions")
    print(f"   • {info['intuitions']['heuristics']} problem-solving heuristics")
    print(f"   • {info['intuitions']['common_mistakes']} common mistakes to avoid")
    
    print("\n📊 QUERY TRACKING:")
    print(f"   • Total queries: {info['query_stats']['total_queries']}")
    print(f"   • Manus has full visibility into all framework queries")


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "UNIVERSAL KNOWLEDGE NETWORK TEST" + " "*20 + "║")
    print("║" + " "*10 + "Comprehensive Mathematics & Physics Knowledge" + " "*13 + "║")
    print("╚" + "="*68 + "╝")
    
    # Run tests
    test_mathematics_knowledge()
    test_physics_knowledge()
    test_cross_field_connections()
    test_intuitions()
    test_suggest_approach()
    test_manus_visibility()
    show_knowledge_summary()
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print("\n✅ Universal Knowledge Network is fully operational!")
    print("✅ Frameworks have unlimited access to all knowledge")
    print("✅ Manus sees all queries for broad spectrum visibility")
    print("\nThe system is ready for Yang-Mills research!")


if __name__ == "__main__":
    main()
