"""
Universal Knowledge Network for AETHER

This is the comprehensive knowledge system that lives in Manus's space.
Frameworks have UNLIMITED access, but Manus sees ALL queries.

Architecture:
- Mathematics: Complete theorem database across all fields
- Physics: Complete physics knowledge from classical to QFT
- History: How problems were actually solved
- Connections: Cross-field links and analogies
- Intuitions: How experts think about problems

Key Design:
- Frameworks access through virtual interfaces (feels unlimited)
- Manus owns the data (sees everything)
- Query tracking gives Manus broad spectrum visibility
"""

from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from collections import defaultdict
import json


class QueryTracker:
    """
    Tracks all queries made by frameworks.
    Gives Manus visibility into their thought processes.
    """
    
    def __init__(self):
        self.queries: List[Dict] = []
        self.query_patterns: Dict[str, List[str]] = defaultdict(list)
        self.framework_interests: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    
    def log_query(self, framework: str, query_type: str, query: str, 
                  results_count: int, context: Dict = None):
        """Log a query from a framework."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "framework": framework,
            "query_type": query_type,
            "query": query,
            "results_count": results_count,
            "context": context or {}
        }
        self.queries.append(entry)
        
        # Track patterns
        self.query_patterns[framework].append(query)
        
        # Track interests
        for word in query.lower().split():
            if len(word) > 3:  # Skip short words
                self.framework_interests[framework][word] += 1
    
    def get_framework_focus(self, framework: str) -> List[str]:
        """Get what a framework is focusing on."""
        interests = self.framework_interests[framework]
        sorted_interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_interests[:10]]
    
    def get_recent_queries(self, framework: str = None, limit: int = 10) -> List[Dict]:
        """Get recent queries, optionally filtered by framework."""
        queries = self.queries
        if framework:
            queries = [q for q in queries if q["framework"] == framework]
        return queries[-limit:]
    
    def get_query_statistics(self) -> Dict:
        """Get statistics about all queries."""
        stats = {
            "total_queries": len(self.queries),
            "by_framework": defaultdict(int),
            "by_type": defaultdict(int),
            "recent_activity": []
        }
        
        for query in self.queries:
            stats["by_framework"][query["framework"]] += 1
            stats["by_type"][query["query_type"]] += 1
        
        # Recent activity summary
        for query in self.queries[-5:]:
            stats["recent_activity"].append({
                "framework": query["framework"],
                "query": query["query"][:50] + "..." if len(query["query"]) > 50 else query["query"]
            })
        
        return dict(stats)
    
    def detect_convergence(self) -> Optional[Dict]:
        """Detect if frameworks are converging on similar topics."""
        if len(self.framework_interests) < 2:
            return None
        
        frameworks = list(self.framework_interests.keys())
        if len(frameworks) < 2:
            return None
        
        # Find common interests
        interests_1 = set(self.framework_interests[frameworks[0]].keys())
        interests_2 = set(self.framework_interests[frameworks[1]].keys())
        
        common = interests_1 & interests_2
        
        if common:
            return {
                "frameworks": frameworks,
                "common_interests": list(common),
                "potential_collaboration": len(common) > 3
            }
        
        return None


class MathematicsKnowledge:
    """
    Comprehensive mathematics knowledge base.
    
    Covers all major areas relevant to Yang-Mills:
    - Differential Geometry
    - Topology (Algebraic, Differential, Geometric)
    - Functional Analysis
    - Lie Theory and Representation Theory
    - Algebraic Geometry
    - Category Theory
    - Analysis (Real, Complex, Harmonic)
    """
    
    def __init__(self):
        self.theorems = self._load_theorems()
        self.definitions = self._load_definitions()
        self.techniques = self._load_techniques()
        self.fields = self._build_field_index()
    
    def _load_theorems(self) -> Dict[str, Dict]:
        """Load comprehensive theorem database."""
        return {
            # ===== DIFFERENTIAL GEOMETRY =====
            "stokes_theorem": {
                "statement": "∫_M dω = ∫_{∂M} ω for any differential form ω on a manifold M with boundary ∂M",
                "field": "differential_geometry",
                "importance": "fundamental",
                "prerequisites": ["manifolds", "differential_forms", "integration"],
                "applications": ["gauge_theory", "topology", "physics"],
                "intuition": "The integral of a derivative over a region equals the integral over the boundary",
                "history": "Generalization of fundamental theorem of calculus to higher dimensions"
            },
            "frobenius_theorem": {
                "statement": "A distribution D on a manifold is integrable if and only if it is involutive",
                "field": "differential_geometry",
                "importance": "fundamental",
                "prerequisites": ["distributions", "lie_brackets", "foliations"],
                "applications": ["gauge_fixing", "integrability", "pde"],
                "intuition": "Tells us when we can find surfaces tangent to a family of planes",
                "history": "Ferdinand Frobenius, 1877"
            },
            "gauss_bonnet": {
                "statement": "∫_M K dA = 2πχ(M) for a compact 2-manifold M",
                "field": "differential_geometry",
                "importance": "fundamental",
                "prerequisites": ["gaussian_curvature", "euler_characteristic"],
                "applications": ["topology", "physics", "string_theory"],
                "intuition": "Total curvature is a topological invariant",
                "history": "Connects local geometry to global topology"
            },
            "chern_weil_theory": {
                "statement": "Characteristic classes can be computed from curvature forms",
                "field": "differential_geometry",
                "importance": "fundamental",
                "prerequisites": ["connections", "curvature", "cohomology"],
                "applications": ["instantons", "topological_charge", "index_theory"],
                "intuition": "Curvature encodes topological information",
                "history": "Shiing-Shen Chern, André Weil, 1940s"
            },
            
            # ===== TOPOLOGY =====
            "poincare_lemma": {
                "statement": "On a contractible manifold, every closed form is exact",
                "field": "topology",
                "importance": "fundamental",
                "prerequisites": ["differential_forms", "cohomology", "contractibility"],
                "applications": ["gauge_theory", "de_rham_cohomology"],
                "intuition": "No holes means no non-trivial closed forms",
                "history": "Henri Poincaré, foundation of algebraic topology"
            },
            "hurewicz_theorem": {
                "statement": "First non-trivial homotopy group equals first non-trivial homology group",
                "field": "topology",
                "importance": "fundamental",
                "prerequisites": ["homotopy_groups", "homology"],
                "applications": ["classification", "obstruction_theory"],
                "intuition": "Connects two ways of measuring holes",
                "history": "Witold Hurewicz, 1935"
            },
            "atiyah_singer_index": {
                "statement": "Index of elliptic operator equals topological index",
                "field": "topology",
                "importance": "fundamental",
                "prerequisites": ["elliptic_operators", "k_theory", "characteristic_classes"],
                "applications": ["anomalies", "instantons", "string_theory"],
                "intuition": "Analytical and topological information are equivalent",
                "history": "Atiyah-Singer, 1963, Fields Medal work"
            },
            
            # ===== FUNCTIONAL ANALYSIS =====
            "sobolev_embedding": {
                "statement": "W^{k,p}(Ω) ↪ L^q(Ω) for appropriate k, p, q depending on dimension",
                "field": "functional_analysis",
                "importance": "fundamental",
                "prerequisites": ["sobolev_spaces", "lp_spaces"],
                "applications": ["pde", "regularity", "existence_proofs"],
                "intuition": "Derivatives give you integrability",
                "history": "Sergei Sobolev, 1930s"
            },
            "rellich_kondrachov": {
                "statement": "Sobolev embeddings are compact for bounded domains",
                "field": "functional_analysis",
                "importance": "fundamental",
                "prerequisites": ["sobolev_spaces", "compact_operators"],
                "applications": ["variational_methods", "eigenvalue_problems"],
                "intuition": "Bounded sequences have convergent subsequences",
                "history": "Foundation of modern PDE theory"
            },
            "spectral_theorem": {
                "statement": "Self-adjoint operators have spectral decomposition",
                "field": "functional_analysis",
                "importance": "fundamental",
                "prerequisites": ["hilbert_spaces", "self_adjoint_operators"],
                "applications": ["quantum_mechanics", "mass_gap", "spectral_theory"],
                "intuition": "Generalization of diagonalization to infinite dimensions",
                "history": "von Neumann, 1929"
            },
            "hahn_banach": {
                "statement": "Linear functionals can be extended preserving norm",
                "field": "functional_analysis",
                "importance": "fundamental",
                "prerequisites": ["normed_spaces", "linear_functionals"],
                "applications": ["duality", "optimization", "distribution_theory"],
                "intuition": "You can always extend linear maps",
                "history": "Hahn 1927, Banach 1929"
            },
            
            # ===== LIE THEORY =====
            "lie_algebra_correspondence": {
                "statement": "Simply connected Lie groups correspond bijectively to Lie algebras",
                "field": "lie_theory",
                "importance": "fundamental",
                "prerequisites": ["lie_groups", "lie_algebras", "exponential_map"],
                "applications": ["gauge_theory", "representation_theory", "physics"],
                "intuition": "Infinitesimal structure determines global structure",
                "history": "Sophus Lie, 1870s"
            },
            "peter_weyl": {
                "statement": "L²(G) decomposes into irreducible representations for compact G",
                "field": "lie_theory",
                "importance": "fundamental",
                "prerequisites": ["compact_groups", "representations", "harmonic_analysis"],
                "applications": ["qcd", "standard_model", "harmonic_analysis"],
                "intuition": "Fourier analysis on groups",
                "history": "Peter-Weyl, 1927"
            },
            "cartan_classification": {
                "statement": "Simple Lie algebras classified into A, B, C, D, E, F, G series",
                "field": "lie_theory",
                "importance": "fundamental",
                "prerequisites": ["simple_lie_algebras", "root_systems"],
                "applications": ["gauge_theory", "grand_unification", "string_theory"],
                "intuition": "Complete classification of symmetry types",
                "history": "Wilhelm Killing, Élie Cartan, 1890s"
            },
            
            # ===== GAUGE THEORY =====
            "yang_mills_equations": {
                "statement": "D*F = 0 where F is curvature and D is covariant derivative",
                "field": "gauge_theory",
                "importance": "fundamental",
                "prerequisites": ["connections", "curvature", "hodge_star"],
                "applications": ["qcd", "standard_model", "instantons"],
                "intuition": "Generalization of Maxwell's equations to non-abelian groups",
                "history": "Yang-Mills, 1954"
            },
            "bianchi_identity": {
                "statement": "DF = 0 (covariant derivative of curvature vanishes)",
                "field": "gauge_theory",
                "importance": "fundamental",
                "prerequisites": ["connections", "curvature"],
                "applications": ["consistency", "conservation_laws"],
                "intuition": "Curvature satisfies a constraint",
                "history": "Luigi Bianchi, generalized to gauge theory"
            },
            "uhlenbeck_compactness": {
                "statement": "Sequences of connections with bounded curvature have convergent subsequences",
                "field": "gauge_theory",
                "importance": "fundamental",
                "prerequisites": ["connections", "sobolev_spaces", "gauge_transformations"],
                "applications": ["moduli_spaces", "instantons", "donaldson_theory"],
                "intuition": "Gauge theory has good compactness properties",
                "history": "Karen Uhlenbeck, 1982, foundational for gauge theory analysis"
            },
            
            # ===== QUANTUM FIELD THEORY =====
            "wick_theorem": {
                "statement": "Time-ordered products decompose into normal-ordered products and contractions",
                "field": "qft",
                "importance": "fundamental",
                "prerequisites": ["quantum_fields", "normal_ordering", "propagators"],
                "applications": ["feynman_diagrams", "perturbation_theory"],
                "intuition": "Systematic way to compute correlation functions",
                "history": "Gian-Carlo Wick, 1950"
            },
            "osterwalder_schrader": {
                "statement": "Euclidean QFT satisfying OS axioms corresponds to Minkowski QFT",
                "field": "qft",
                "importance": "fundamental",
                "prerequisites": ["euclidean_qft", "wightman_axioms", "analytic_continuation"],
                "applications": ["constructive_qft", "lattice_qft", "rigorous_qft"],
                "intuition": "Euclidean and Minkowski formulations are equivalent",
                "history": "Osterwalder-Schrader, 1973-1975"
            },
            "lsz_reduction": {
                "statement": "S-matrix elements from correlation functions via LSZ formula",
                "field": "qft",
                "importance": "fundamental",
                "prerequisites": ["s_matrix", "correlation_functions", "asymptotic_states"],
                "applications": ["scattering_amplitudes", "particle_physics"],
                "intuition": "Connects field theory to observable scattering",
                "history": "Lehmann-Symanzik-Zimmermann, 1955"
            },
            
            # ===== RENORMALIZATION =====
            "callan_symanzik": {
                "statement": "(μ∂/∂μ + β∂/∂g + γ)Γ = 0 (RG equation)",
                "field": "renormalization",
                "importance": "fundamental",
                "prerequisites": ["renormalization_group", "beta_function", "anomalous_dimensions"],
                "applications": ["asymptotic_freedom", "running_coupling", "critical_phenomena"],
                "intuition": "Physics is independent of arbitrary scale",
                "history": "Callan, Symanzik, 1970"
            },
            "asymptotic_freedom": {
                "statement": "Non-abelian gauge theories have β < 0 at weak coupling",
                "field": "renormalization",
                "importance": "fundamental",
                "prerequisites": ["beta_function", "perturbation_theory", "yang_mills"],
                "applications": ["qcd", "confinement", "mass_gap"],
                "intuition": "Coupling decreases at high energy",
                "history": "Gross-Wilczek, Politzer, 1973, Nobel Prize 2004"
            },
            "wetterich_equation": {
                "statement": "∂_k Γ_k = (1/2) Tr[(Γ_k'' + R_k)^{-1} ∂_k R_k]",
                "field": "renormalization",
                "importance": "fundamental",
                "prerequisites": ["effective_action", "functional_rg", "regulator"],
                "applications": ["non_perturbative_rg", "phase_transitions", "mass_gap"],
                "intuition": "Exact flow equation for effective action",
                "history": "Christof Wetterich, 1993"
            }
        }
    
    def _load_definitions(self) -> Dict[str, Dict]:
        """Load mathematical definitions."""
        return {
            "manifold": {
                "definition": "A topological space locally homeomorphic to Euclidean space",
                "field": "differential_geometry",
                "intuition": "A space that looks flat when you zoom in",
                "examples": ["sphere", "torus", "projective_space"]
            },
            "fiber_bundle": {
                "definition": "A space E with projection π: E → B such that fibers π^{-1}(b) are homeomorphic",
                "field": "topology",
                "intuition": "A family of spaces parameterized by a base space",
                "examples": ["tangent_bundle", "principal_bundle", "vector_bundle"]
            },
            "connection": {
                "definition": "A way to compare vectors at different points (parallel transport)",
                "field": "differential_geometry",
                "intuition": "Tells you how to move vectors around",
                "examples": ["levi_civita", "yang_mills", "spin_connection"]
            },
            "curvature": {
                "definition": "Measure of failure of parallel transport to be path-independent",
                "field": "differential_geometry",
                "intuition": "How much space is curved",
                "examples": ["riemann_tensor", "field_strength", "ricci_curvature"]
            },
            "gauge_group": {
                "definition": "The structure group of a principal bundle (local symmetry)",
                "field": "gauge_theory",
                "intuition": "The symmetry that acts at each point",
                "examples": ["U(1)", "SU(2)", "SU(3)"]
            },
            "mass_gap": {
                "definition": "Positive difference between vacuum and first excited state energy",
                "field": "qft",
                "intuition": "Minimum energy needed to create a particle",
                "examples": ["yang_mills_mass_gap", "spectral_gap"]
            }
        }
    
    def _load_techniques(self) -> Dict[str, Dict]:
        """Load mathematical techniques."""
        return {
            "variational_methods": {
                "description": "Find solutions by minimizing functionals",
                "field": "analysis",
                "when_to_use": ["existence_proofs", "pde", "optimization"],
                "key_steps": ["define_functional", "show_coercivity", "find_minimum"]
            },
            "compactness_arguments": {
                "description": "Extract convergent subsequences from bounded sequences",
                "field": "analysis",
                "when_to_use": ["existence_proofs", "convergence", "limits"],
                "key_steps": ["show_boundedness", "apply_compactness", "identify_limit"]
            },
            "gauge_fixing": {
                "description": "Choose representative from gauge equivalence class",
                "field": "gauge_theory",
                "when_to_use": ["simplify_equations", "remove_redundancy", "quantization"],
                "key_steps": ["choose_gauge", "verify_accessibility", "handle_gribov"]
            },
            "dimensional_regularization": {
                "description": "Regulate divergences by continuing to d dimensions",
                "field": "qft",
                "when_to_use": ["loop_calculations", "renormalization", "anomalies"],
                "key_steps": ["continue_to_d", "expand_in_epsilon", "extract_poles"]
            },
            "lattice_discretization": {
                "description": "Replace continuum with discrete lattice",
                "field": "qft",
                "when_to_use": ["non_perturbative", "numerical", "rigorous_construction"],
                "key_steps": ["discretize_action", "monte_carlo", "continuum_limit"]
            }
        }
    
    def _build_field_index(self) -> Dict[str, List[str]]:
        """Build index of theorems by field."""
        index = defaultdict(list)
        for name, theorem in self.theorems.items():
            index[theorem["field"]].append(name)
        return dict(index)
    
    def search(self, query: str, field: str = None) -> List[Dict]:
        """Search for theorems, definitions, or techniques."""
        results = []
        query_lower = query.lower()
        
        # Search theorems
        for name, theorem in self.theorems.items():
            if field and theorem["field"] != field:
                continue
            searchable = f"{name} {theorem['statement']} {theorem['field']} {' '.join(theorem.get('applications', []))}".lower()
            if query_lower in searchable:
                results.append({"type": "theorem", "name": name, **theorem})
        
        # Search definitions
        for name, defn in self.definitions.items():
            if field and defn["field"] != field:
                continue
            searchable = f"{name} {defn['definition']} {defn['field']}".lower()
            if query_lower in searchable:
                results.append({"type": "definition", "name": name, **defn})
        
        # Search techniques
        for name, tech in self.techniques.items():
            if field and tech["field"] != field:
                continue
            searchable = f"{name} {tech['description']} {tech['field']}".lower()
            if query_lower in searchable:
                results.append({"type": "technique", "name": name, **tech})
        
        return results
    
    def get_theorem(self, name: str) -> Optional[Dict]:
        """Get a specific theorem."""
        return self.theorems.get(name)
    
    def get_definition(self, name: str) -> Optional[Dict]:
        """Get a specific definition."""
        return self.definitions.get(name)
    
    def get_technique(self, name: str) -> Optional[Dict]:
        """Get a specific technique."""
        return self.techniques.get(name)
    
    def get_by_field(self, field: str) -> Dict[str, List]:
        """Get all content in a field."""
        return {
            "theorems": [{"name": name, **self.theorems[name]} 
                        for name in self.fields.get(field, [])],
            "definitions": [{"name": name, **defn} 
                           for name, defn in self.definitions.items() 
                           if defn["field"] == field],
            "techniques": [{"name": name, **tech} 
                          for name, tech in self.techniques.items() 
                          if tech["field"] == field]
        }
    
    def get_prerequisites(self, theorem_name: str) -> List[str]:
        """Get prerequisites for understanding a theorem."""
        if theorem_name in self.theorems:
            return self.theorems[theorem_name].get("prerequisites", [])
        return []
    
    def get_applications(self, theorem_name: str) -> List[str]:
        """Get applications of a theorem."""
        if theorem_name in self.theorems:
            return self.theorems[theorem_name].get("applications", [])
        return []
    
    def find_related(self, theorem_name: str) -> List[str]:
        """Find related theorems."""
        if theorem_name not in self.theorems:
            return []
        
        theorem = self.theorems[theorem_name]
        related = []
        
        # Same field
        for name in self.fields.get(theorem["field"], []):
            if name != theorem_name:
                related.append(name)
        
        # Shared applications
        apps = set(theorem.get("applications", []))
        for name, other in self.theorems.items():
            if name == theorem_name:
                continue
            other_apps = set(other.get("applications", []))
            if apps & other_apps:
                if name not in related:
                    related.append(name)
        
        return related[:10]
    
    def get_info(self) -> Dict:
        """Get information about the knowledge base."""
        return {
            "theorems": len(self.theorems),
            "definitions": len(self.definitions),
            "techniques": len(self.techniques),
            "fields": list(self.fields.keys())
        }


class PhysicsKnowledge:
    """
    Comprehensive physics knowledge base.
    
    Covers the complete development from classical to quantum:
    - Classical Mechanics (Lagrangian, Hamiltonian)
    - Electromagnetism (Maxwell, Gauge theory origins)
    - Quantum Mechanics (Foundations)
    - Quantum Field Theory (Complete development)
    - Statistical Mechanics (Path integrals, Phase transitions)
    - General Relativity (Geometry connections)
    - Standard Model (Yang-Mills applications)
    """
    
    def __init__(self):
        self.concepts = self._load_concepts()
        self.principles = self._load_principles()
        self.experiments = self._load_experiments()
        self.history = self._load_history()
    
    def _load_concepts(self) -> Dict[str, Dict]:
        """Load physics concepts."""
        return {
            # ===== CLASSICAL MECHANICS =====
            "lagrangian_mechanics": {
                "description": "Formulation of mechanics using L = T - V and principle of least action",
                "field": "classical_mechanics",
                "key_equations": ["L = T - V", "δS = 0", "d/dt(∂L/∂q̇) = ∂L/∂q"],
                "importance": "Foundation for all modern physics, leads to symmetries and conservation",
                "connections": ["hamiltonian_mechanics", "field_theory", "quantum_mechanics"]
            },
            "hamiltonian_mechanics": {
                "description": "Formulation using H = T + V and phase space",
                "field": "classical_mechanics",
                "key_equations": ["H = Σp_i q̇_i - L", "q̇ = ∂H/∂p", "ṗ = -∂H/∂q"],
                "importance": "Foundation for quantum mechanics and statistical mechanics",
                "connections": ["quantum_mechanics", "statistical_mechanics", "symplectic_geometry"]
            },
            "noether_theorem": {
                "description": "Every continuous symmetry corresponds to a conserved quantity",
                "field": "classical_mechanics",
                "key_equations": ["symmetry → conservation law"],
                "importance": "Fundamental connection between symmetry and physics",
                "connections": ["gauge_theory", "conservation_laws", "lie_groups"]
            },
            
            # ===== ELECTROMAGNETISM =====
            "maxwell_equations": {
                "description": "Complete theory of electromagnetism",
                "field": "electromagnetism",
                "key_equations": ["∇·E = ρ/ε₀", "∇×E = -∂B/∂t", "∇·B = 0", "∇×B = μ₀J + μ₀ε₀∂E/∂t"],
                "importance": "First gauge theory, template for Yang-Mills",
                "connections": ["gauge_theory", "special_relativity", "qed"]
            },
            "gauge_invariance_em": {
                "description": "Physics unchanged under A → A + ∇χ, φ → φ - ∂χ/∂t",
                "field": "electromagnetism",
                "key_equations": ["F_μν = ∂_μA_ν - ∂_νA_μ (invariant)"],
                "importance": "First example of gauge symmetry, leads to Yang-Mills",
                "connections": ["yang_mills", "fiber_bundles", "qed"]
            },
            
            # ===== QUANTUM MECHANICS =====
            "schrodinger_equation": {
                "description": "Fundamental equation of quantum mechanics",
                "field": "quantum_mechanics",
                "key_equations": ["iℏ∂ψ/∂t = Ĥψ"],
                "importance": "Foundation of quantum theory",
                "connections": ["path_integral", "qft", "spectral_theory"]
            },
            "path_integral": {
                "description": "Sum over all paths weighted by e^{iS/ℏ}",
                "field": "quantum_mechanics",
                "key_equations": ["⟨x_f|e^{-iHt/ℏ}|x_i⟩ = ∫Dx e^{iS[x]/ℏ}"],
                "importance": "Foundation for QFT, connects to statistical mechanics",
                "connections": ["qft", "statistical_mechanics", "instantons"]
            },
            "uncertainty_principle": {
                "description": "Fundamental limit on simultaneous measurement",
                "field": "quantum_mechanics",
                "key_equations": ["ΔxΔp ≥ ℏ/2"],
                "importance": "Core quantum principle",
                "connections": ["commutators", "spectral_theory", "measurement"]
            },
            
            # ===== QUANTUM FIELD THEORY =====
            "second_quantization": {
                "description": "Quantum mechanics of fields, particle creation/annihilation",
                "field": "qft",
                "key_equations": ["[a, a†] = 1", "φ(x) = ∫(a_k e^{ikx} + a†_k e^{-ikx})dk"],
                "importance": "Foundation of QFT",
                "connections": ["fock_space", "feynman_diagrams", "particle_physics"]
            },
            "feynman_diagrams": {
                "description": "Graphical representation of perturbation theory",
                "field": "qft",
                "key_equations": ["amplitude = Σ diagrams"],
                "importance": "Practical calculation tool for QFT",
                "connections": ["perturbation_theory", "renormalization", "scattering"]
            },
            "renormalization": {
                "description": "Systematic removal of infinities in QFT",
                "field": "qft",
                "key_equations": ["bare = physical + counterterm"],
                "importance": "Makes QFT predictive",
                "connections": ["rg_flow", "asymptotic_freedom", "effective_field_theory"]
            },
            "asymptotic_freedom_physics": {
                "description": "Coupling decreases at high energy in non-abelian gauge theories",
                "field": "qft",
                "key_equations": ["β(g) = -β₀g³ + O(g⁵), β₀ > 0 for SU(N)"],
                "importance": "Explains why quarks are free at high energy",
                "connections": ["qcd", "confinement", "mass_gap"]
            },
            
            # ===== YANG-MILLS THEORY =====
            "yang_mills_theory": {
                "description": "Non-abelian gauge theory with gauge group G",
                "field": "yang_mills",
                "key_equations": ["L = -1/4 F^a_μν F^{aμν}", "F = dA + A∧A"],
                "importance": "Foundation of Standard Model",
                "connections": ["qcd", "electroweak", "instantons", "mass_gap"]
            },
            "confinement": {
                "description": "Quarks cannot exist as free particles",
                "field": "yang_mills",
                "key_equations": ["V(r) ~ σr (linear potential)"],
                "importance": "Key non-perturbative phenomenon in QCD",
                "connections": ["mass_gap", "wilson_loops", "lattice_qcd"]
            },
            "mass_gap_physics": {
                "description": "Lowest excitation has positive energy",
                "field": "yang_mills",
                "key_equations": ["E_1 - E_0 = Δ > 0"],
                "importance": "Millennium Prize Problem",
                "connections": ["confinement", "spectral_theory", "correlation_length"]
            },
            "instantons_physics": {
                "description": "Tunneling between topologically distinct vacua",
                "field": "yang_mills",
                "key_equations": ["F = ±*F (self-dual)", "Q = (1/32π²)∫F∧F"],
                "importance": "Non-perturbative effects, vacuum structure",
                "connections": ["topology", "theta_vacuum", "chiral_anomaly"]
            },
            
            # ===== STANDARD MODEL =====
            "standard_model": {
                "description": "SU(3)×SU(2)×U(1) gauge theory of fundamental interactions",
                "field": "particle_physics",
                "key_equations": ["L = L_gauge + L_fermion + L_Higgs + L_Yukawa"],
                "importance": "Complete theory of known particles",
                "connections": ["qcd", "electroweak", "higgs_mechanism"]
            },
            "qcd": {
                "description": "SU(3) Yang-Mills theory of strong interactions",
                "field": "particle_physics",
                "key_equations": ["L = -1/4 G^a_μν G^{aμν} + ψ̄(iD̸ - m)ψ"],
                "importance": "Theory of quarks and gluons",
                "connections": ["confinement", "asymptotic_freedom", "mass_gap"]
            },
            "higgs_mechanism": {
                "description": "Spontaneous symmetry breaking gives mass to gauge bosons",
                "field": "particle_physics",
                "key_equations": ["⟨φ⟩ ≠ 0", "m_W = gv/2"],
                "importance": "Explains W, Z masses",
                "connections": ["electroweak", "symmetry_breaking", "goldstone"]
            },
            
            # ===== STATISTICAL MECHANICS =====
            "partition_function": {
                "description": "Z = Σ e^{-βE_n} encodes all thermodynamics",
                "field": "statistical_mechanics",
                "key_equations": ["Z = Tr e^{-βH}", "F = -kT ln Z"],
                "importance": "Foundation of statistical mechanics",
                "connections": ["path_integral", "phase_transitions", "euclidean_qft"]
            },
            "phase_transitions": {
                "description": "Abrupt changes in system properties",
                "field": "statistical_mechanics",
                "key_equations": ["order parameter", "critical exponents"],
                "importance": "Universal phenomena across physics",
                "connections": ["rg_flow", "conformal_field_theory", "lattice_models"]
            },
            "euclidean_qft_connection": {
                "description": "QFT in imaginary time = statistical mechanics",
                "field": "statistical_mechanics",
                "key_equations": ["t → -iτ", "⟨O⟩ = (1/Z)∫Dφ O e^{-S_E}"],
                "importance": "Connects QFT to statistical mechanics",
                "connections": ["lattice_qcd", "monte_carlo", "path_integral"]
            }
        }
    
    def _load_principles(self) -> Dict[str, Dict]:
        """Load fundamental physics principles."""
        return {
            "least_action": {
                "statement": "Physical trajectories extremize the action S = ∫L dt",
                "importance": "Foundation of all physics",
                "applications": ["mechanics", "field_theory", "quantum_mechanics"]
            },
            "gauge_principle": {
                "statement": "Local symmetry requires introduction of gauge fields",
                "importance": "Origin of all fundamental forces",
                "applications": ["electromagnetism", "yang_mills", "gravity"]
            },
            "symmetry_breaking": {
                "statement": "Ground state may have less symmetry than the Lagrangian",
                "importance": "Explains mass generation, phase transitions",
                "applications": ["higgs", "superconductivity", "magnetism"]
            },
            "renormalization_group": {
                "statement": "Physics at different scales related by RG flow",
                "importance": "Unifies UV and IR physics",
                "applications": ["critical_phenomena", "qft", "effective_theories"]
            },
            "unitarity": {
                "statement": "Probability is conserved in quantum mechanics",
                "importance": "Fundamental consistency requirement",
                "applications": ["s_matrix", "optical_theorem", "causality"]
            }
        }
    
    def _load_experiments(self) -> Dict[str, Dict]:
        """Load key experiments."""
        return {
            "deep_inelastic_scattering": {
                "description": "Probing proton structure with high-energy electrons",
                "year": 1968,
                "result": "Discovery of quarks, parton model",
                "connection_to_theory": "Confirmed QCD, asymptotic freedom"
            },
            "jet_production": {
                "description": "Observation of collimated particle jets",
                "year": 1975,
                "result": "Direct evidence for gluons",
                "connection_to_theory": "Confirmed non-abelian gauge theory"
            },
            "lattice_qcd_spectrum": {
                "description": "Numerical calculation of hadron masses",
                "year": "1980s-present",
                "result": "Agreement with experiment at ~1% level",
                "connection_to_theory": "Confirms QCD, provides mass gap evidence"
            },
            "higgs_discovery": {
                "description": "Discovery of Higgs boson at LHC",
                "year": 2012,
                "result": "Confirmed electroweak symmetry breaking",
                "connection_to_theory": "Validates Standard Model"
            }
        }
    
    def _load_history(self) -> Dict[str, Dict]:
        """Load historical development."""
        return {
            "gauge_theory_development": {
                "timeline": [
                    {"year": 1918, "event": "Weyl proposes gauge invariance"},
                    {"year": 1929, "event": "Weyl connects to electromagnetism"},
                    {"year": 1954, "event": "Yang-Mills non-abelian gauge theory"},
                    {"year": 1964, "event": "Higgs mechanism proposed"},
                    {"year": 1967, "event": "Weinberg-Salam electroweak theory"},
                    {"year": 1973, "event": "Asymptotic freedom discovered"},
                    {"year": 1974, "event": "QCD established as theory of strong force"},
                    {"year": 2000, "event": "Yang-Mills mass gap becomes Millennium Problem"}
                ],
                "key_insight": "Local symmetry requires gauge fields, non-abelian leads to confinement"
            },
            "mass_gap_problem": {
                "timeline": [
                    {"year": 1954, "event": "Yang-Mills theory proposed"},
                    {"year": 1973, "event": "Asymptotic freedom suggests confinement"},
                    {"year": 1974, "event": "Wilson proposes lattice gauge theory"},
                    {"year": "1980s", "event": "Lattice QCD provides numerical evidence"},
                    {"year": 2000, "event": "Clay Institute poses Millennium Problem"},
                    {"year": "present", "event": "Still unsolved mathematically"}
                ],
                "key_insight": "Numerical evidence strong, rigorous proof elusive"
            }
        }
    
    def search(self, query: str, field: str = None) -> List[Dict]:
        """Search physics knowledge."""
        results = []
        query_lower = query.lower()
        
        # Search concepts
        for name, concept in self.concepts.items():
            if field and concept["field"] != field:
                continue
            searchable = f"{name} {concept['description']} {concept['field']}".lower()
            if query_lower in searchable:
                results.append({"type": "concept", "name": name, **concept})
        
        # Search principles
        for name, principle in self.principles.items():
            searchable = f"{name} {principle['statement']}".lower()
            if query_lower in searchable:
                results.append({"type": "principle", "name": name, **principle})
        
        # Search experiments
        for name, exp in self.experiments.items():
            searchable = f"{name} {exp['description']} {exp['result']}".lower()
            if query_lower in searchable:
                results.append({"type": "experiment", "name": name, **exp})
        
        return results
    
    def get_concept(self, name: str) -> Optional[Dict]:
        """Get a specific concept."""
        return self.concepts.get(name)
    
    def get_principle(self, name: str) -> Optional[Dict]:
        """Get a specific principle."""
        return self.principles.get(name)
    
    def get_history(self, topic: str) -> Optional[Dict]:
        """Get historical development of a topic."""
        return self.history.get(topic)
    
    def get_connections(self, concept_name: str) -> List[str]:
        """Get connections from a concept."""
        if concept_name in self.concepts:
            return self.concepts[concept_name].get("connections", [])
        return []
    
    def get_info(self) -> Dict:
        """Get information about the knowledge base."""
        return {
            "concepts": len(self.concepts),
            "principles": len(self.principles),
            "experiments": len(self.experiments),
            "historical_topics": len(self.history)
        }


class CrossFieldConnections:
    """
    Maps connections between mathematics and physics.
    
    This is where the deep insights live - the analogies and
    correspondences that have led to breakthroughs.
    """
    
    def __init__(self):
        self.connections = self._load_connections()
        self.analogies = self._load_analogies()
        self.breakthrough_patterns = self._load_breakthrough_patterns()
    
    def _load_connections(self) -> Dict[str, Dict]:
        """Load cross-field connections."""
        return {
            # ===== GEOMETRY ↔ PHYSICS =====
            "fiber_bundles_gauge_theory": {
                "math_side": "fiber_bundles",
                "physics_side": "gauge_theory",
                "connection": "Gauge fields ARE connections on principal bundles",
                "importance": "Fundamental",
                "details": {
                    "base_space": "spacetime",
                    "fiber": "gauge group G",
                    "connection": "gauge field A_μ",
                    "curvature": "field strength F_μν",
                    "parallel_transport": "Wilson lines"
                },
                "history": "Recognized in 1970s, unified geometry and physics"
            },
            "curvature_field_strength": {
                "math_side": "curvature_tensor",
                "physics_side": "field_strength",
                "connection": "Field strength is curvature of gauge connection",
                "importance": "Fundamental",
                "details": {
                    "math_formula": "R = dω + ω∧ω",
                    "physics_formula": "F = dA + A∧A",
                    "same_structure": True
                },
                "history": "Yang-Mills 1954, geometric interpretation later"
            },
            "characteristic_classes_anomalies": {
                "math_side": "characteristic_classes",
                "physics_side": "anomalies",
                "connection": "Anomalies are obstructions measured by characteristic classes",
                "importance": "Fundamental",
                "details": {
                    "chern_class": "gauge_anomaly",
                    "pontryagin_class": "gravitational_anomaly",
                    "index_theorem": "anomaly_cancellation"
                },
                "history": "Atiyah-Singer index theorem applied to physics"
            },
            
            # ===== TOPOLOGY ↔ PHYSICS =====
            "homotopy_instantons": {
                "math_side": "homotopy_groups",
                "physics_side": "instantons",
                "connection": "Instantons classified by π_3(G)",
                "importance": "Fundamental",
                "details": {
                    "π_3(SU(2))": "Z → instanton number",
                    "π_3(SU(3))": "Z → QCD instantons",
                    "physical_meaning": "tunneling between vacua"
                },
                "history": "Belavin-Polyakov-Schwartz-Tyupkin 1975"
            },
            "cohomology_conservation_laws": {
                "math_side": "de_rham_cohomology",
                "physics_side": "conservation_laws",
                "connection": "Conserved currents are closed forms, charges are cohomology classes",
                "importance": "Fundamental",
                "details": {
                    "closed_form": "conserved current (∂_μJ^μ = 0)",
                    "exact_form": "trivial current",
                    "cohomology_class": "conserved charge"
                },
                "history": "Noether's theorem in geometric language"
            },
            
            # ===== ANALYSIS ↔ PHYSICS =====
            "spectral_theory_mass_gap": {
                "math_side": "spectral_theory",
                "physics_side": "mass_gap",
                "connection": "Mass gap = spectral gap of Hamiltonian",
                "importance": "Fundamental for Millennium Problem",
                "details": {
                    "spectrum": "energy levels",
                    "ground_state": "vacuum",
                    "spectral_gap": "mass of lightest particle",
                    "continuous_spectrum": "scattering states"
                },
                "history": "Central to Yang-Mills problem formulation"
            },
            "sobolev_spaces_regularity": {
                "math_side": "sobolev_spaces",
                "physics_side": "field_regularity",
                "connection": "Physical fields live in appropriate Sobolev spaces",
                "importance": "Fundamental for rigorous QFT",
                "details": {
                    "finite_action": "W^{1,2} connection",
                    "regularity": "smoothness of solutions",
                    "compactness": "existence of minimizers"
                },
                "history": "Uhlenbeck's work on gauge theory"
            },
            
            # ===== ALGEBRA ↔ PHYSICS =====
            "lie_groups_symmetries": {
                "math_side": "lie_groups",
                "physics_side": "symmetry_groups",
                "connection": "Physical symmetries are Lie groups",
                "importance": "Fundamental",
                "details": {
                    "U(1)": "electromagnetism",
                    "SU(2)": "weak force",
                    "SU(3)": "strong force (QCD)",
                    "Poincare": "spacetime symmetry"
                },
                "history": "Weyl, Wigner, 1920s-1930s"
            },
            "representation_theory_particles": {
                "math_side": "representation_theory",
                "physics_side": "particle_classification",
                "connection": "Particles are irreducible representations",
                "importance": "Fundamental",
                "details": {
                    "spin": "SU(2) representation",
                    "color": "SU(3) representation",
                    "mass": "Casimir invariant"
                },
                "history": "Wigner's classification 1939"
            },
            
            # ===== PROBABILITY ↔ PHYSICS =====
            "path_integral_measure_theory": {
                "math_side": "measure_theory",
                "physics_side": "path_integral",
                "connection": "Path integral is functional integral (measure on path space)",
                "importance": "Fundamental but mathematically difficult",
                "details": {
                    "challenge": "no Lebesgue measure on infinite dimensions",
                    "solutions": ["lattice regularization", "constructive QFT"],
                    "status": "rigorous for some theories, not Yang-Mills"
                },
                "history": "Feynman 1948, rigorous work ongoing"
            },
            
            # ===== GEOMETRY ↔ RG FLOW =====
            "ricci_flow_rg_flow": {
                "math_side": "ricci_flow",
                "physics_side": "rg_flow",
                "connection": "Both are gradient flows that simplify structure",
                "importance": "Deep analogy, potential breakthrough",
                "details": {
                    "ricci_flow": "∂g/∂t = -2Ric (geometry simplifies)",
                    "rg_flow": "∂Γ/∂k = ... (physics simplifies at IR)",
                    "both": "flow to fixed points",
                    "surgery": "handle singularities similarly"
                },
                "history": "Perelman used for Poincaré, RG analogy noted"
            }
        }
    
    def _load_analogies(self) -> Dict[str, Dict]:
        """Load productive analogies that led to breakthroughs."""
        return {
            "em_weak_unification": {
                "analogy": "Electromagnetism : Weak force :: U(1) : SU(2)",
                "led_to": "Electroweak unification",
                "lesson": "Similar mathematical structure suggests unification"
            },
            "superconductor_higgs": {
                "analogy": "Superconductor : Higgs mechanism :: condensed matter : particle physics",
                "led_to": "Understanding of mass generation",
                "lesson": "Same physics in different contexts"
            },
            "string_gauge": {
                "analogy": "String worldsheet : Gauge theory :: 2D : 4D",
                "led_to": "AdS/CFT correspondence",
                "lesson": "Lower dimensional theories can encode higher dimensional ones"
            },
            "lattice_continuum": {
                "analogy": "Lattice : Continuum :: regularization : physical theory",
                "led_to": "Non-perturbative QCD",
                "lesson": "Discretization can make problems tractable"
            },
            "classical_quantum": {
                "analogy": "Classical mechanics : Quantum mechanics :: deterministic : probabilistic",
                "led_to": "Path integral formulation",
                "lesson": "Sum over classical paths gives quantum amplitude"
            }
        }
    
    def _load_breakthrough_patterns(self) -> Dict[str, Dict]:
        """Load patterns that have led to breakthroughs."""
        return {
            "symmetry_principle": {
                "pattern": "Identify symmetry → Derive consequences",
                "examples": ["Noether theorem", "gauge theory", "supersymmetry"],
                "how_to_apply": "Look for hidden symmetries in the problem"
            },
            "geometric_reformulation": {
                "pattern": "Reformulate problem geometrically → New insights",
                "examples": ["gauge theory as fiber bundles", "GR as geometry"],
                "how_to_apply": "Ask: what is the natural geometric setting?"
            },
            "analogy_transfer": {
                "pattern": "Find analogy in solved problem → Transfer solution",
                "examples": ["superconductor → Higgs", "Ricci flow → RG flow"],
                "how_to_apply": "Look for similar structures in other fields"
            },
            "regularization_limit": {
                "pattern": "Regularize → Solve → Take limit",
                "examples": ["lattice QCD", "dimensional regularization"],
                "how_to_apply": "Make problem finite, then carefully remove cutoff"
            },
            "duality": {
                "pattern": "Find dual description → Solve in easier regime",
                "examples": ["electric-magnetic duality", "AdS/CFT", "Montonen-Olive"],
                "how_to_apply": "Look for equivalent but simpler formulations"
            },
            "index_theorem_application": {
                "pattern": "Use index theorem → Topological constraints",
                "examples": ["anomaly cancellation", "instanton counting"],
                "how_to_apply": "Topological invariants constrain physics"
            }
        }
    
    def find_connection(self, concept: str) -> List[Dict]:
        """Find connections involving a concept."""
        results = []
        concept_lower = concept.lower()
        
        for name, conn in self.connections.items():
            searchable = f"{name} {conn['math_side']} {conn['physics_side']} {conn['connection']}".lower()
            if concept_lower in searchable:
                results.append({"name": name, **conn})
        
        return results
    
    def find_analogy(self, concept: str) -> List[Dict]:
        """Find analogies involving a concept."""
        results = []
        concept_lower = concept.lower()
        
        for name, analogy in self.analogies.items():
            searchable = f"{name} {analogy['analogy']} {analogy['led_to']}".lower()
            if concept_lower in searchable:
                results.append({"name": name, **analogy})
        
        return results
    
    def get_breakthrough_pattern(self, name: str) -> Optional[Dict]:
        """Get a specific breakthrough pattern."""
        return self.breakthrough_patterns.get(name)
    
    def suggest_approach(self, problem_description: str) -> List[Dict]:
        """Suggest approaches based on breakthrough patterns."""
        suggestions = []
        desc_lower = problem_description.lower()
        
        # Pattern matching for suggestions
        if "symmetry" in desc_lower:
            suggestions.append(self.breakthrough_patterns["symmetry_principle"])
        
        if "geometry" in desc_lower or "geometric" in desc_lower:
            suggestions.append(self.breakthrough_patterns["geometric_reformulation"])
        
        if "similar" in desc_lower or "like" in desc_lower:
            suggestions.append(self.breakthrough_patterns["analogy_transfer"])
        
        if "infinite" in desc_lower or "diverge" in desc_lower:
            suggestions.append(self.breakthrough_patterns["regularization_limit"])
        
        if "dual" in desc_lower or "equivalent" in desc_lower:
            suggestions.append(self.breakthrough_patterns["duality"])
        
        if "topolog" in desc_lower:
            suggestions.append(self.breakthrough_patterns["index_theorem_application"])
        
        # If no specific match, suggest all
        if not suggestions:
            suggestions = list(self.breakthrough_patterns.values())
        
        return suggestions
    
    def get_info(self) -> Dict:
        """Get information about the connections."""
        return {
            "connections": len(self.connections),
            "analogies": len(self.analogies),
            "breakthrough_patterns": len(self.breakthrough_patterns)
        }


class IntuitionEngine:
    """
    Captures how experts think about problems.
    
    This is the "secret sauce" - the intuitions and heuristics
    that mathematicians and physicists use but rarely write down.
    """
    
    def __init__(self):
        self.intuitions = self._load_intuitions()
        self.heuristics = self._load_heuristics()
        self.common_mistakes = self._load_common_mistakes()
    
    def _load_intuitions(self) -> Dict[str, Dict]:
        """Load expert intuitions."""
        return {
            "gauge_theory_intuition": {
                "concept": "gauge_theory",
                "intuition": "Gauge symmetry is redundancy in description, not physical symmetry",
                "implications": [
                    "Physical observables must be gauge-invariant",
                    "Gauge fixing is choosing coordinates, not breaking symmetry",
                    "Different gauges are like different coordinate systems"
                ],
                "common_confusion": "Thinking gauge symmetry is like rotation symmetry"
            },
            "mass_gap_intuition": {
                "concept": "mass_gap",
                "intuition": "Mass gap means correlations decay exponentially",
                "implications": [
                    "Correlation length is finite: ξ ~ 1/m",
                    "No long-range forces between color charges",
                    "Spectrum is discrete, not continuous from zero"
                ],
                "common_confusion": "Confusing mass gap with confinement (related but different)"
            },
            "path_integral_intuition": {
                "concept": "path_integral",
                "intuition": "Quantum mechanics = sum over all classical possibilities",
                "implications": [
                    "Classical path dominates when ℏ → 0",
                    "Quantum effects from interference of paths",
                    "Euclidean version = statistical mechanics"
                ],
                "common_confusion": "Taking 'sum over paths' too literally"
            },
            "renormalization_intuition": {
                "concept": "renormalization",
                "intuition": "Physics at different scales is related but different",
                "implications": [
                    "UV divergences reflect ignorance of short distances",
                    "Effective theories valid at each scale",
                    "RG flow tells you how physics changes with scale"
                ],
                "common_confusion": "Thinking renormalization is just 'subtracting infinities'"
            },
            "topology_physics_intuition": {
                "concept": "topology_in_physics",
                "intuition": "Topology captures global, robust features",
                "implications": [
                    "Topological quantities are quantized (integers)",
                    "Cannot be changed by smooth deformations",
                    "Often related to boundary conditions"
                ],
                "common_confusion": "Thinking topology is just 'counting holes'"
            },
            "symmetry_breaking_intuition": {
                "concept": "symmetry_breaking",
                "intuition": "Ground state can have less symmetry than the laws",
                "implications": [
                    "Symmetry is hidden, not destroyed",
                    "Goldstone bosons for continuous symmetries",
                    "Order parameter distinguishes phases"
                ],
                "common_confusion": "Thinking the symmetry is 'gone'"
            }
        }
    
    def _load_heuristics(self) -> Dict[str, Dict]:
        """Load problem-solving heuristics."""
        return {
            "dimensional_analysis": {
                "heuristic": "Check dimensions first - wrong dimensions means wrong answer",
                "when_to_use": "Always, especially when stuck",
                "example": "Mass gap Δ ~ Λ_QCD (only scale in pure Yang-Mills)"
            },
            "symmetry_check": {
                "heuristic": "If result doesn't respect symmetry, it's wrong",
                "when_to_use": "Checking calculations",
                "example": "Gauge-invariant quantities only"
            },
            "limiting_cases": {
                "heuristic": "Check behavior in extreme limits",
                "when_to_use": "Understanding new results",
                "example": "Weak coupling (perturbative), strong coupling (lattice)"
            },
            "count_degrees_of_freedom": {
                "heuristic": "Count independent components carefully",
                "when_to_use": "Setting up problems",
                "example": "Gauge field has N²-1 components for SU(N)"
            },
            "look_for_conserved_quantities": {
                "heuristic": "Conservation laws constrain dynamics",
                "when_to_use": "Simplifying problems",
                "example": "Energy, momentum, charge conservation"
            },
            "perturbation_first": {
                "heuristic": "Try perturbation theory first, even if it fails",
                "when_to_use": "Starting new problems",
                "example": "Asymptotic freedom tells us perturbation works at high energy"
            }
        }
    
    def _load_common_mistakes(self) -> Dict[str, Dict]:
        """Load common mistakes to avoid."""
        return {
            "confusing_gauge_physical": {
                "mistake": "Treating gauge-dependent quantities as physical",
                "why_wrong": "Gauge choice is arbitrary, physics is not",
                "how_to_avoid": "Always check gauge invariance of final results"
            },
            "naive_continuum_limit": {
                "mistake": "Taking continuum limit without proper renormalization",
                "why_wrong": "Divergences must be handled carefully",
                "how_to_avoid": "Use renormalization group, check universality"
            },
            "forgetting_topology": {
                "mistake": "Ignoring topological sectors (instantons, etc.)",
                "why_wrong": "Non-perturbative effects can be crucial",
                "how_to_avoid": "Consider all topological sectors, especially for vacuum"
            },
            "perturbative_only": {
                "mistake": "Relying only on perturbation theory",
                "why_wrong": "Misses confinement, mass gap, instantons",
                "how_to_avoid": "Use lattice, functional methods, or other non-perturbative tools"
            },
            "wrong_measure": {
                "mistake": "Using wrong measure in path integral",
                "why_wrong": "Measure determines physics",
                "how_to_avoid": "Careful about gauge-fixing, ghosts, Jacobians"
            }
        }
    
    def get_intuition(self, concept: str) -> Optional[Dict]:
        """Get intuition for a concept."""
        # Direct lookup
        for name, intuition in self.intuitions.items():
            if concept.lower() in name.lower() or concept.lower() in intuition["concept"].lower():
                return intuition
        return None
    
    def get_heuristic(self, situation: str) -> List[Dict]:
        """Get relevant heuristics for a situation."""
        results = []
        situation_lower = situation.lower()
        
        for name, heuristic in self.heuristics.items():
            searchable = f"{name} {heuristic['heuristic']} {heuristic['when_to_use']}".lower()
            if any(word in searchable for word in situation_lower.split()):
                results.append({"name": name, **heuristic})
        
        if not results:
            # Return all heuristics if no specific match
            results = [{"name": name, **h} for name, h in self.heuristics.items()]
        
        return results
    
    def get_common_mistake(self, topic: str) -> List[Dict]:
        """Get common mistakes related to a topic."""
        results = []
        topic_lower = topic.lower()
        
        for name, mistake in self.common_mistakes.items():
            searchable = f"{name} {mistake['mistake']}".lower()
            if topic_lower in searchable:
                results.append({"name": name, **mistake})
        
        return results
    
    def get_info(self) -> Dict:
        """Get information about the intuition engine."""
        return {
            "intuitions": len(self.intuitions),
            "heuristics": len(self.heuristics),
            "common_mistakes": len(self.common_mistakes)
        }


class UniversalKnowledgeNetwork:
    """
    The complete Universal Knowledge Network.
    
    Lives in Manus's space, accessible to all frameworks through
    virtual interfaces. Manus sees ALL queries for broad spectrum
    visibility.
    
    Components:
    - Mathematics: Complete theorem database
    - Physics: Complete physics knowledge
    - Connections: Cross-field links
    - Intuitions: Expert thinking patterns
    - Query Tracker: Visibility for Manus
    """
    
    def __init__(self):
        print("="*60)
        print("INITIALIZING UNIVERSAL KNOWLEDGE NETWORK")
        print("="*60)
        
        # Initialize all components
        self.mathematics = MathematicsKnowledge()
        print(f"✓ Mathematics: {self.mathematics.get_info()['theorems']} theorems, "
              f"{self.mathematics.get_info()['definitions']} definitions, "
              f"{self.mathematics.get_info()['techniques']} techniques")
        
        self.physics = PhysicsKnowledge()
        print(f"✓ Physics: {self.physics.get_info()['concepts']} concepts, "
              f"{self.physics.get_info()['principles']} principles, "
              f"{self.physics.get_info()['experiments']} experiments")
        
        self.connections = CrossFieldConnections()
        print(f"✓ Connections: {self.connections.get_info()['connections']} cross-field links, "
              f"{self.connections.get_info()['analogies']} analogies, "
              f"{self.connections.get_info()['breakthrough_patterns']} patterns")
        
        self.intuitions = IntuitionEngine()
        print(f"✓ Intuitions: {self.intuitions.get_info()['intuitions']} intuitions, "
              f"{self.intuitions.get_info()['heuristics']} heuristics, "
              f"{self.intuitions.get_info()['common_mistakes']} common mistakes")
        
        # Query tracker for Manus visibility
        self.query_tracker = QueryTracker()
        print("✓ Query tracker initialized (Manus visibility enabled)")
        
        print("="*60)
        print("UNIVERSAL KNOWLEDGE NETWORK READY")
        print("="*60)
    
    def search(self, query: str, framework: str = "unknown", 
               domain: str = None) -> Dict[str, List]:
        """
        Universal search across all knowledge.
        
        Args:
            query: Search query
            framework: Name of framework making query (for tracking)
            domain: Optional domain filter ("math", "physics", "connections")
        
        Returns:
            Results from all relevant domains
        """
        results = {
            "mathematics": [],
            "physics": [],
            "connections": [],
            "intuitions": []
        }
        
        # Search mathematics
        if domain is None or domain == "math":
            results["mathematics"] = self.mathematics.search(query)
        
        # Search physics
        if domain is None or domain == "physics":
            results["physics"] = self.physics.search(query)
        
        # Search connections
        if domain is None or domain == "connections":
            results["connections"] = self.connections.find_connection(query)
            results["connections"].extend(self.connections.find_analogy(query))
        
        # Search intuitions
        if domain is None or domain == "intuitions":
            intuition = self.intuitions.get_intuition(query)
            if intuition:
                results["intuitions"].append(intuition)
        
        # Track the query (Manus sees everything!)
        total_results = sum(len(v) for v in results.values())
        self.query_tracker.log_query(
            framework=framework,
            query_type="search",
            query=query,
            results_count=total_results,
            context={"domain": domain}
        )
        
        return results
    
    def get_theorem(self, name: str, framework: str = "unknown") -> Optional[Dict]:
        """Get a specific theorem."""
        result = self.mathematics.get_theorem(name)
        
        self.query_tracker.log_query(
            framework=framework,
            query_type="get_theorem",
            query=name,
            results_count=1 if result else 0
        )
        
        return result
    
    def get_concept(self, name: str, framework: str = "unknown") -> Optional[Dict]:
        """Get a physics concept."""
        result = self.physics.get_concept(name)
        
        self.query_tracker.log_query(
            framework=framework,
            query_type="get_concept",
            query=name,
            results_count=1 if result else 0
        )
        
        return result
    
    def get_connection(self, name: str, framework: str = "unknown") -> Optional[Dict]:
        """Get a cross-field connection."""
        result = self.connections.connections.get(name)
        
        self.query_tracker.log_query(
            framework=framework,
            query_type="get_connection",
            query=name,
            results_count=1 if result else 0
        )
        
        return result
    
    def get_intuition(self, concept: str, framework: str = "unknown") -> Optional[Dict]:
        """Get expert intuition for a concept."""
        result = self.intuitions.get_intuition(concept)
        
        self.query_tracker.log_query(
            framework=framework,
            query_type="get_intuition",
            query=concept,
            results_count=1 if result else 0
        )
        
        return result
    
    def get_heuristics(self, situation: str, framework: str = "unknown") -> List[Dict]:
        """Get problem-solving heuristics."""
        results = self.intuitions.get_heuristic(situation)
        
        self.query_tracker.log_query(
            framework=framework,
            query_type="get_heuristics",
            query=situation,
            results_count=len(results)
        )
        
        return results
    
    def suggest_approach(self, problem: str, framework: str = "unknown") -> Dict:
        """
        Suggest approaches for a problem.
        
        Combines breakthrough patterns, analogies, and heuristics.
        """
        suggestions = {
            "breakthrough_patterns": self.connections.suggest_approach(problem),
            "analogies": self.connections.find_analogy(problem),
            "heuristics": self.intuitions.get_heuristic(problem),
            "common_mistakes": self.intuitions.get_common_mistake(problem)
        }
        
        self.query_tracker.log_query(
            framework=framework,
            query_type="suggest_approach",
            query=problem,
            results_count=sum(len(v) for v in suggestions.values())
        )
        
        return suggestions
    
    def get_history(self, topic: str, framework: str = "unknown") -> Optional[Dict]:
        """Get historical development of a topic."""
        result = self.physics.get_history(topic)
        
        self.query_tracker.log_query(
            framework=framework,
            query_type="get_history",
            query=topic,
            results_count=1 if result else 0
        )
        
        return result
    
    def find_prerequisites(self, concept: str, framework: str = "unknown") -> List[str]:
        """Find prerequisites for understanding a concept."""
        # Check mathematics
        prereqs = self.mathematics.get_prerequisites(concept)
        
        # Check physics connections
        if concept in self.physics.concepts:
            prereqs.extend(self.physics.concepts[concept].get("connections", []))
        
        self.query_tracker.log_query(
            framework=framework,
            query_type="find_prerequisites",
            query=concept,
            results_count=len(prereqs)
        )
        
        return list(set(prereqs))
    
    def find_applications(self, concept: str, framework: str = "unknown") -> List[str]:
        """Find applications of a concept."""
        apps = self.mathematics.get_applications(concept)
        
        self.query_tracker.log_query(
            framework=framework,
            query_type="find_applications",
            query=concept,
            results_count=len(apps)
        )
        
        return apps
    
    # ===== MANUS VISIBILITY METHODS =====
    
    def get_query_statistics(self) -> Dict:
        """Get statistics about all queries (for Manus)."""
        return self.query_tracker.get_query_statistics()
    
    def get_framework_focus(self, framework: str) -> List[str]:
        """Get what a framework is focusing on (for Manus)."""
        return self.query_tracker.get_framework_focus(framework)
    
    def get_recent_queries(self, framework: str = None, limit: int = 10) -> List[Dict]:
        """Get recent queries (for Manus)."""
        return self.query_tracker.get_recent_queries(framework, limit)
    
    def detect_convergence(self) -> Optional[Dict]:
        """Detect if frameworks are converging (for Manus)."""
        return self.query_tracker.detect_convergence()
    
    def get_info(self) -> Dict:
        """Get complete information about the knowledge network."""
        return {
            "mathematics": self.mathematics.get_info(),
            "physics": self.physics.get_info(),
            "connections": self.connections.get_info(),
            "intuitions": self.intuitions.get_info(),
            "query_stats": self.query_tracker.get_query_statistics()
        }


# Global instance
_knowledge_network = None

def get_knowledge_network() -> UniversalKnowledgeNetwork:
    """Get the global Universal Knowledge Network instance."""
    global _knowledge_network
    if _knowledge_network is None:
        _knowledge_network = UniversalKnowledgeNetwork()
    return _knowledge_network
