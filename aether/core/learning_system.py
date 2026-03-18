"""
Progressive Learning System for AETHER

A complete learning curriculum with:
1. Study Materials - Comprehensive learning resources
2. Unique Test Questions - AI-challenging problems I CREATE (not from textbooks)
3. Advancement Tracking - Progress through 5 levels

Key Design Principle:
- Study materials teach concepts
- Test questions are UNIQUE and CHALLENGING
- They must truly UNDERSTAND to pass, not just memorize
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import json


class Level(Enum):
    """The 5 levels of the curriculum."""
    FOUNDATIONS = 1      # Calculus, Linear Algebra, Classical Mechanics
    GEOMETRY_GROUPS = 2  # Differential Geometry, Lie Groups, Manifolds
    ANALYSIS_TOPOLOGY = 3  # Functional Analysis, Algebraic Topology
    FIELD_THEORY = 4     # QFT, Gauge Theory, Renormalization
    YANG_MILLS = 5       # Mass Gap, Confinement, The Millennium Problem


class Difficulty(Enum):
    """Difficulty levels for test questions."""
    EASY = 1
    MEDIUM = 2
    HARD = 3
    CHALLENGE = 4  # For AIs - requires genuine insight


class StudyMaterial:
    """
    A study material resource.
    
    These are for LEARNING - concepts, theorems, examples.
    NOT the same as test questions!
    """
    
    def __init__(self, title: str, level: Level, content: Dict):
        self.title = title
        self.level = level
        self.content = content
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "level": self.level.name,
            "content": self.content
        }


class TestQuestion:
    """
    A unique test question.
    
    These are CHALLENGES I create - not from any textbook.
    They test genuine understanding, not memorization.
    """
    
    def __init__(self, question_id: str, level: Level, difficulty: Difficulty,
                 question: str, hints: List[str], solution_approach: str,
                 grading_criteria: Dict, requires_concepts: List[str]):
        self.question_id = question_id
        self.level = level
        self.difficulty = difficulty
        self.question = question
        self.hints = hints  # Progressive hints if they're stuck
        self.solution_approach = solution_approach  # How to evaluate their answer
        self.grading_criteria = grading_criteria  # What constitutes a good answer
        self.requires_concepts = requires_concepts  # Concepts they need to understand
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "question_id": self.question_id,
            "level": self.level.name,
            "difficulty": self.difficulty.name,
            "question": self.question,
            "hints": self.hints,
            "requires_concepts": self.requires_concepts
        }


class FrameworkProgress:
    """
    Tracks a framework's progress through the curriculum.
    """
    
    def __init__(self, framework_name: str):
        self.framework_name = framework_name
        self.current_level = Level.FOUNDATIONS
        self.attempts: Dict[str, List[Dict]] = {}  # question_id -> list of attempts
        self.passed_questions: Dict[Level, List[str]] = {level: [] for level in Level}
        self.study_materials_accessed: Dict[Level, List[str]] = {level: [] for level in Level}
        self.started_at = datetime.now()
        self.level_completion_times: Dict[Level, datetime] = {}
    
    def record_attempt(self, question_id: str, answer: str, 
                      score: float, feedback: str):
        """Record an attempt at a question."""
        if question_id not in self.attempts:
            self.attempts[question_id] = []
        
        self.attempts[question_id].append({
            "answer": answer,
            "score": score,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        })
    
    def mark_passed(self, question_id: str, level: Level):
        """Mark a question as passed."""
        if question_id not in self.passed_questions[level]:
            self.passed_questions[level].append(question_id)
    
    def record_study(self, material_title: str, level: Level):
        """Record that a study material was accessed."""
        if material_title not in self.study_materials_accessed[level]:
            self.study_materials_accessed[level].append(material_title)
    
    def get_level_progress(self, level: Level) -> Dict:
        """Get progress for a specific level."""
        return {
            "passed_questions": len(self.passed_questions[level]),
            "materials_studied": len(self.study_materials_accessed[level]),
            "total_attempts": sum(
                len(attempts) for qid, attempts in self.attempts.items()
            )
        }
    
    def can_advance(self, required_pass_count: int = 3) -> bool:
        """Check if framework can advance to next level."""
        current_passed = len(self.passed_questions[self.current_level])
        return current_passed >= required_pass_count
    
    def advance_level(self) -> bool:
        """Advance to the next level if possible."""
        if self.current_level == Level.YANG_MILLS:
            return False  # Already at top
        
        if not self.can_advance():
            return False
        
        self.level_completion_times[self.current_level] = datetime.now()
        next_level_value = self.current_level.value + 1
        self.current_level = Level(next_level_value)
        return True
    
    def get_summary(self) -> Dict:
        """Get a summary of progress."""
        return {
            "framework": self.framework_name,
            "current_level": self.current_level.name,
            "level_value": self.current_level.value,
            "questions_passed_per_level": {
                level.name: len(passed) 
                for level, passed in self.passed_questions.items()
            },
            "total_questions_passed": sum(
                len(passed) for passed in self.passed_questions.values()
            ),
            "can_advance": self.can_advance(),
            "levels_completed": list(self.level_completion_times.keys())
        }


class StudyMaterialsLibrary:
    """
    Library of study materials organized by level.
    
    These are for LEARNING - comprehensive resources to build understanding.
    """
    
    def __init__(self):
        self.materials: Dict[Level, List[StudyMaterial]] = {
            level: [] for level in Level
        }
        self._load_materials()
    
    def _load_materials(self):
        """Load all study materials."""
        
        # ===== LEVEL 1: FOUNDATIONS =====
        self.materials[Level.FOUNDATIONS] = [
            StudyMaterial(
                "Calculus Foundations",
                Level.FOUNDATIONS,
                {
                    "overview": "The language of change and accumulation",
                    "key_concepts": [
                        {
                            "name": "Derivatives",
                            "definition": "Rate of change of a function",
                            "formula": "f'(x) = lim_{h→0} [f(x+h) - f(x)]/h",
                            "intuition": "How fast is the function changing at this point?",
                            "examples": ["Velocity is derivative of position", "Slope of tangent line"]
                        },
                        {
                            "name": "Integrals",
                            "definition": "Accumulation of quantities",
                            "formula": "∫f(x)dx = F(x) + C where F'(x) = f(x)",
                            "intuition": "Total accumulated quantity (area under curve)",
                            "examples": ["Distance from velocity", "Work from force"]
                        },
                        {
                            "name": "Fundamental Theorem of Calculus",
                            "statement": "Differentiation and integration are inverse operations",
                            "formula": "d/dx ∫_a^x f(t)dt = f(x)",
                            "importance": "Connects the two main operations of calculus"
                        }
                    ],
                    "why_important": "Calculus is the foundation of all physics - it describes how things change"
                }
            ),
            StudyMaterial(
                "Linear Algebra Foundations",
                Level.FOUNDATIONS,
                {
                    "overview": "The mathematics of vectors, matrices, and linear transformations",
                    "key_concepts": [
                        {
                            "name": "Vector Spaces",
                            "definition": "A set with addition and scalar multiplication satisfying axioms",
                            "examples": ["R^n", "Function spaces", "Polynomial spaces"],
                            "intuition": "A 'universe' where you can add things and scale them"
                        },
                        {
                            "name": "Linear Transformations",
                            "definition": "Maps that preserve addition and scalar multiplication",
                            "formula": "T(av + bw) = aT(v) + bT(w)",
                            "intuition": "Transformations that don't 'bend' the space"
                        },
                        {
                            "name": "Eigenvalues and Eigenvectors",
                            "definition": "Av = λv - vectors that only get scaled",
                            "importance": "Reveal the 'natural directions' of a transformation",
                            "connection": "Foundation for quantum mechanics and spectral theory"
                        },
                        {
                            "name": "Inner Products",
                            "definition": "A way to measure angles and lengths",
                            "formula": "⟨v,w⟩ satisfying linearity, symmetry, positive-definiteness",
                            "importance": "Allows geometry in abstract spaces"
                        }
                    ],
                    "why_important": "Linear algebra is the language of quantum mechanics and gauge theory"
                }
            ),
            StudyMaterial(
                "Classical Mechanics Foundations",
                Level.FOUNDATIONS,
                {
                    "overview": "The physics of motion and forces",
                    "key_concepts": [
                        {
                            "name": "Newton's Laws",
                            "laws": [
                                "1. Objects at rest stay at rest (inertia)",
                                "2. F = ma (force causes acceleration)",
                                "3. Action = Reaction"
                            ],
                            "importance": "Foundation of all mechanics"
                        },
                        {
                            "name": "Lagrangian Mechanics",
                            "definition": "L = T - V (kinetic minus potential energy)",
                            "principle": "Principle of least action: δS = 0 where S = ∫L dt",
                            "euler_lagrange": "d/dt(∂L/∂q̇) - ∂L/∂q = 0",
                            "why_better": "Works in any coordinate system, reveals symmetries"
                        },
                        {
                            "name": "Hamiltonian Mechanics",
                            "definition": "H = Σp_i q̇_i - L (usually H = T + V)",
                            "equations": ["q̇ = ∂H/∂p", "ṗ = -∂H/∂q"],
                            "importance": "Foundation for quantum mechanics",
                            "phase_space": "State is (q, p) - position and momentum"
                        },
                        {
                            "name": "Noether's Theorem",
                            "statement": "Every continuous symmetry has a conserved quantity",
                            "examples": [
                                "Time translation → Energy conservation",
                                "Space translation → Momentum conservation",
                                "Rotation → Angular momentum conservation"
                            ],
                            "importance": "Deep connection between symmetry and physics"
                        }
                    ],
                    "why_important": "Classical mechanics is the template for all field theories"
                }
            ),
            StudyMaterial(
                "Vector Calculus",
                Level.FOUNDATIONS,
                {
                    "overview": "Calculus in multiple dimensions",
                    "key_concepts": [
                        {
                            "name": "Gradient",
                            "definition": "∇f = (∂f/∂x, ∂f/∂y, ∂f/∂z)",
                            "intuition": "Direction of steepest increase",
                            "properties": ["Points uphill", "Perpendicular to level surfaces"]
                        },
                        {
                            "name": "Divergence",
                            "definition": "∇·F = ∂F_x/∂x + ∂F_y/∂y + ∂F_z/∂z",
                            "intuition": "How much the field 'spreads out'",
                            "physical_meaning": "Source strength at a point"
                        },
                        {
                            "name": "Curl",
                            "definition": "∇×F = (∂F_z/∂y - ∂F_y/∂z, ...)",
                            "intuition": "How much the field 'rotates'",
                            "physical_meaning": "Local rotation/circulation"
                        },
                        {
                            "name": "Fundamental Theorems",
                            "theorems": [
                                "Gradient theorem: ∫_C ∇f·dr = f(b) - f(a)",
                                "Divergence theorem: ∫_V ∇·F dV = ∮_S F·dA",
                                "Stokes' theorem: ∫_S (∇×F)·dA = ∮_C F·dr"
                            ],
                            "importance": "Connect local and global properties"
                        }
                    ],
                    "why_important": "Essential for electromagnetism and gauge theory"
                }
            )
        ]
        
        # ===== LEVEL 2: GEOMETRY & GROUPS =====
        self.materials[Level.GEOMETRY_GROUPS] = [
            StudyMaterial(
                "Manifolds and Differential Geometry",
                Level.GEOMETRY_GROUPS,
                {
                    "overview": "Geometry on curved spaces",
                    "key_concepts": [
                        {
                            "name": "Manifolds",
                            "definition": "A space that locally looks like R^n",
                            "examples": ["Sphere S²", "Torus T²", "Spacetime"],
                            "intuition": "Curved spaces that are flat when you zoom in",
                            "charts_atlases": "Local coordinate systems that cover the manifold"
                        },
                        {
                            "name": "Tangent Spaces",
                            "definition": "Vector space of 'directions' at each point",
                            "notation": "T_p M = tangent space at point p",
                            "intuition": "The flat approximation to the manifold at a point"
                        },
                        {
                            "name": "Differential Forms",
                            "definition": "Antisymmetric multilinear maps on tangent vectors",
                            "examples": ["0-forms: functions", "1-forms: covectors", "2-forms: area elements"],
                            "exterior_derivative": "d: k-forms → (k+1)-forms, d² = 0",
                            "importance": "Natural objects for integration on manifolds"
                        },
                        {
                            "name": "Connections and Curvature",
                            "connection": "A way to compare vectors at different points",
                            "parallel_transport": "Moving vectors along curves",
                            "curvature": "Failure of parallel transport to be path-independent",
                            "formula": "R(X,Y)Z = ∇_X∇_Y Z - ∇_Y∇_X Z - ∇_{[X,Y]} Z"
                        }
                    ],
                    "why_important": "Gauge theory is geometry on fiber bundles"
                }
            ),
            StudyMaterial(
                "Lie Groups and Lie Algebras",
                Level.GEOMETRY_GROUPS,
                {
                    "overview": "Continuous symmetry groups",
                    "key_concepts": [
                        {
                            "name": "Lie Groups",
                            "definition": "A group that is also a smooth manifold",
                            "examples": [
                                "GL(n): invertible matrices",
                                "O(n): orthogonal matrices",
                                "U(n): unitary matrices",
                                "SU(n): special unitary (det = 1)"
                            ],
                            "importance": "Symmetry groups in physics"
                        },
                        {
                            "name": "Lie Algebras",
                            "definition": "Tangent space at identity with bracket operation",
                            "bracket": "[X, Y] = XY - YX for matrix groups",
                            "relation": "Lie algebra is 'infinitesimal' version of Lie group",
                            "exponential_map": "exp: g → G connects algebra to group"
                        },
                        {
                            "name": "Representations",
                            "definition": "Homomorphism from group to matrices",
                            "importance": "How groups act on vector spaces",
                            "examples": [
                                "Fundamental representation of SU(N)",
                                "Adjoint representation",
                                "Spin representations"
                            ]
                        },
                        {
                            "name": "Structure Constants",
                            "definition": "[T_a, T_b] = f^c_{ab} T_c",
                            "importance": "Encode the algebra structure",
                            "for_su2": "f^c_{ab} = ε_{abc} (Levi-Civita symbol)"
                        }
                    ],
                    "why_important": "Gauge groups are Lie groups - SU(3) for QCD"
                }
            ),
            StudyMaterial(
                "Fiber Bundles",
                Level.GEOMETRY_GROUPS,
                {
                    "overview": "Spaces attached to each point of a base space",
                    "key_concepts": [
                        {
                            "name": "Fiber Bundle Structure",
                            "definition": "E →π B with fiber F: π^{-1}(b) ≅ F for all b",
                            "components": ["Total space E", "Base space B", "Fiber F", "Projection π"],
                            "intuition": "A 'family' of spaces parameterized by the base"
                        },
                        {
                            "name": "Principal Bundles",
                            "definition": "Fiber is a Lie group G acting freely",
                            "importance": "The natural setting for gauge theory",
                            "gauge_field": "A connection on a principal bundle"
                        },
                        {
                            "name": "Connections on Bundles",
                            "definition": "A way to lift paths from base to total space",
                            "local_form": "A = A_μ dx^μ (gauge field)",
                            "curvature": "F = dA + A∧A (field strength)"
                        },
                        {
                            "name": "Gauge Transformations",
                            "definition": "Automorphisms of the bundle",
                            "local_form": "A → gAg^{-1} + g dg^{-1}",
                            "physical_meaning": "Change of local frame/gauge"
                        }
                    ],
                    "why_important": "Gauge theory IS the geometry of principal bundles"
                }
            )
        ]
        
        # ===== LEVEL 3: ANALYSIS & TOPOLOGY =====
        self.materials[Level.ANALYSIS_TOPOLOGY] = [
            StudyMaterial(
                "Functional Analysis",
                Level.ANALYSIS_TOPOLOGY,
                {
                    "overview": "Analysis in infinite-dimensional spaces",
                    "key_concepts": [
                        {
                            "name": "Banach Spaces",
                            "definition": "Complete normed vector space",
                            "examples": ["L^p spaces", "C([0,1])"],
                            "importance": "Setting for differential equations"
                        },
                        {
                            "name": "Hilbert Spaces",
                            "definition": "Complete inner product space",
                            "examples": ["L²(R)", "ℓ²"],
                            "importance": "Setting for quantum mechanics",
                            "properties": ["Orthonormal bases exist", "Riesz representation"]
                        },
                        {
                            "name": "Operators",
                            "types": [
                                "Bounded operators: ||Tx|| ≤ C||x||",
                                "Compact operators: map bounded sets to precompact",
                                "Self-adjoint: ⟨Tx,y⟩ = ⟨x,Ty⟩",
                                "Unbounded operators: domain issues"
                            ],
                            "importance": "Observables in QM are self-adjoint operators"
                        },
                        {
                            "name": "Spectral Theory",
                            "spectrum": "σ(T) = {λ : T - λI not invertible}",
                            "spectral_theorem": "Self-adjoint operators have spectral decomposition",
                            "connection_to_physics": "Spectrum = possible measurement outcomes",
                            "mass_gap": "Gap in spectrum above ground state"
                        },
                        {
                            "name": "Sobolev Spaces",
                            "definition": "W^{k,p} = functions with k derivatives in L^p",
                            "importance": "Natural spaces for PDEs",
                            "embeddings": "Sobolev embedding theorems"
                        }
                    ],
                    "why_important": "QFT requires infinite-dimensional analysis"
                }
            ),
            StudyMaterial(
                "Algebraic Topology",
                Level.ANALYSIS_TOPOLOGY,
                {
                    "overview": "Using algebra to study topological spaces",
                    "key_concepts": [
                        {
                            "name": "Homotopy",
                            "definition": "Continuous deformation of maps",
                            "homotopy_groups": "π_n(X) = homotopy classes of maps S^n → X",
                            "examples": ["π_1 = fundamental group", "π_3(S²) = Z"],
                            "importance": "Classifies topological obstructions"
                        },
                        {
                            "name": "Homology",
                            "definition": "Algebraic count of 'holes'",
                            "chain_complex": "C_n →∂ C_{n-1} with ∂² = 0",
                            "homology_groups": "H_n = ker(∂)/im(∂)",
                            "intuition": "H_0 = components, H_1 = loops, H_2 = voids"
                        },
                        {
                            "name": "Cohomology",
                            "definition": "Dual to homology",
                            "de_rham": "H^k_{dR} = closed k-forms / exact k-forms",
                            "importance": "Natural for physics (differential forms)"
                        },
                        {
                            "name": "Characteristic Classes",
                            "definition": "Topological invariants of bundles",
                            "examples": ["Chern classes", "Pontryagin classes"],
                            "chern_weil": "Can compute from curvature",
                            "physics": "Measure topological charge, anomalies"
                        }
                    ],
                    "why_important": "Topology constrains physics - instantons, anomalies"
                }
            ),
            StudyMaterial(
                "Spectral Theory and the Mass Gap",
                Level.ANALYSIS_TOPOLOGY,
                {
                    "overview": "The mathematical framework for understanding mass gap",
                    "key_concepts": [
                        {
                            "name": "Spectrum of Operators",
                            "point_spectrum": "Eigenvalues",
                            "continuous_spectrum": "No eigenvalues but not invertible",
                            "essential_spectrum": "Accumulation points and continuous part"
                        },
                        {
                            "name": "Spectral Gap",
                            "definition": "Δ = inf(σ(H) \\ {E_0}) - E_0",
                            "meaning": "Minimum energy to excite from ground state",
                            "consequences": [
                                "Exponential decay of correlations",
                                "Finite correlation length ξ ~ 1/Δ",
                                "Discrete low-lying spectrum"
                            ]
                        },
                        {
                            "name": "Mass Gap in QFT",
                            "definition": "Lowest excitation has positive mass m > 0",
                            "equivalent_statements": [
                                "Two-point function decays exponentially",
                                "Correlation length is finite",
                                "No massless particles"
                            ],
                            "yang_mills_conjecture": "Pure Yang-Mills has mass gap > 0"
                        },
                        {
                            "name": "Why It's Hard",
                            "perturbation_fails": "Perturbation theory sees massless gluons",
                            "non_perturbative": "Mass gap is non-perturbative phenomenon",
                            "lattice_evidence": "Numerical simulations confirm mass gap",
                            "rigorous_proof": "No mathematical proof exists"
                        }
                    ],
                    "why_important": "This IS the Millennium Prize Problem"
                }
            )
        ]
        
        # ===== LEVEL 4: FIELD THEORY =====
        self.materials[Level.FIELD_THEORY] = [
            StudyMaterial(
                "Quantum Field Theory Foundations",
                Level.FIELD_THEORY,
                {
                    "overview": "Quantum mechanics of fields",
                    "key_concepts": [
                        {
                            "name": "Classical Field Theory",
                            "action": "S[φ] = ∫ L(φ, ∂φ) d⁴x",
                            "euler_lagrange": "∂L/∂φ - ∂_μ(∂L/∂(∂_μφ)) = 0",
                            "examples": ["Klein-Gordon", "Maxwell", "Yang-Mills"]
                        },
                        {
                            "name": "Canonical Quantization",
                            "commutators": "[φ(x), π(y)] = iδ³(x-y)",
                            "fock_space": "States are particle number eigenstates",
                            "creation_annihilation": "a†, a create and destroy particles"
                        },
                        {
                            "name": "Path Integral",
                            "formula": "⟨O⟩ = ∫ Dφ O[φ] e^{iS[φ]/ℏ}",
                            "euclidean": "Wick rotate t → -iτ, get e^{-S_E}",
                            "importance": "Natural for gauge theories"
                        },
                        {
                            "name": "Feynman Diagrams",
                            "propagators": "Lines = propagators",
                            "vertices": "Interaction points from Lagrangian",
                            "rules": "Systematic way to compute amplitudes"
                        },
                        {
                            "name": "Renormalization",
                            "problem": "Loop integrals diverge",
                            "solution": "Absorb infinities into parameters",
                            "rg_flow": "Parameters depend on energy scale",
                            "beta_function": "β(g) = μ dg/dμ"
                        }
                    ],
                    "why_important": "QFT is the framework for particle physics"
                }
            ),
            StudyMaterial(
                "Gauge Theory",
                Level.FIELD_THEORY,
                {
                    "overview": "Field theories with local symmetry",
                    "key_concepts": [
                        {
                            "name": "Gauge Principle",
                            "idea": "Make global symmetry local",
                            "requirement": "Must introduce gauge field A_μ",
                            "covariant_derivative": "D_μ = ∂_μ + igA_μ"
                        },
                        {
                            "name": "Yang-Mills Theory",
                            "gauge_group": "Non-abelian Lie group G (e.g., SU(N))",
                            "field_strength": "F_μν = ∂_μA_ν - ∂_νA_μ + ig[A_μ, A_ν]",
                            "action": "S = -1/4 ∫ Tr(F_μν F^μν) d⁴x",
                            "equations": "D_μ F^μν = 0 (Yang-Mills equations)"
                        },
                        {
                            "name": "Gauge Transformations",
                            "transformation": "A_μ → gA_μg^{-1} + (i/g)g∂_μg^{-1}",
                            "physical_observables": "Must be gauge-invariant",
                            "wilson_loops": "Tr P exp(i∮ A) - gauge invariant"
                        },
                        {
                            "name": "Asymptotic Freedom",
                            "beta_function": "β(g) = -β_0 g³ + O(g⁵), β_0 > 0",
                            "meaning": "Coupling decreases at high energy",
                            "consequence": "Perturbation theory works at high energy",
                            "discovery": "Gross, Wilczek, Politzer 1973"
                        },
                        {
                            "name": "Confinement",
                            "phenomenon": "Quarks cannot exist as free particles",
                            "wilson_criterion": "⟨W(C)⟩ ~ exp(-σ·Area) for large loops",
                            "string_tension": "σ ~ (400 MeV)²",
                            "relation_to_mass_gap": "Confinement implies mass gap"
                        }
                    ],
                    "why_important": "Yang-Mills is the foundation of the Standard Model"
                }
            ),
            StudyMaterial(
                "Non-Perturbative Methods",
                Level.FIELD_THEORY,
                {
                    "overview": "Going beyond perturbation theory",
                    "key_concepts": [
                        {
                            "name": "Lattice Gauge Theory",
                            "idea": "Discretize spacetime on a lattice",
                            "link_variables": "U_μ(x) ∈ G on each link",
                            "wilson_action": "S = β Σ (1 - Re Tr U_P)",
                            "continuum_limit": "a → 0 with physics fixed"
                        },
                        {
                            "name": "Monte Carlo Methods",
                            "idea": "Sample configurations with weight e^{-S}",
                            "metropolis": "Accept/reject based on action change",
                            "observables": "⟨O⟩ = (1/N) Σ O[U_i]"
                        },
                        {
                            "name": "Instantons",
                            "definition": "Solutions with F = ±*F (self-dual)",
                            "topological_charge": "Q = (1/32π²) ∫ Tr(F∧F)",
                            "tunneling": "Between topologically distinct vacua",
                            "effects": "θ-vacuum, chiral symmetry breaking"
                        },
                        {
                            "name": "Functional Renormalization Group",
                            "wetterich_equation": "∂_k Γ_k = (1/2) Tr[(Γ_k'' + R_k)^{-1} ∂_k R_k]",
                            "idea": "Integrate out modes shell by shell",
                            "advantage": "Non-perturbative, no expansion in g"
                        }
                    ],
                    "why_important": "Mass gap requires non-perturbative methods"
                }
            )
        ]
        
        # ===== LEVEL 5: YANG-MILLS =====
        self.materials[Level.YANG_MILLS] = [
            StudyMaterial(
                "The Yang-Mills Millennium Problem",
                Level.YANG_MILLS,
                {
                    "overview": "The precise mathematical statement and what's required",
                    "problem_statement": {
                        "official": "Prove that for any compact simple gauge group G, quantum Yang-Mills theory on R⁴ exists and has a mass gap Δ > 0",
                        "requirements": [
                            "1. Construct the theory rigorously (satisfy Wightman or OS axioms)",
                            "2. Prove the Hamiltonian has a spectral gap above the vacuum"
                        ]
                    },
                    "what_exists": {
                        "perturbation_theory": "Well-defined but incomplete (misses mass gap)",
                        "lattice_formulation": "Rigorous but finite volume",
                        "numerical_evidence": "Strong evidence for mass gap",
                        "missing": "Rigorous continuum limit with mass gap"
                    },
                    "key_difficulties": [
                        {
                            "name": "Constructing the theory",
                            "issue": "Path integral measure not well-defined",
                            "approaches": ["Lattice → continuum", "Constructive QFT"]
                        },
                        {
                            "name": "Proving mass gap",
                            "issue": "Non-perturbative phenomenon",
                            "approaches": ["Spectral analysis", "Correlation inequalities"]
                        },
                        {
                            "name": "Gauge invariance",
                            "issue": "Must maintain throughout construction",
                            "approaches": ["Gauge-invariant observables", "BRST cohomology"]
                        }
                    ],
                    "why_important": "Would validate the mathematical foundation of the Standard Model"
                }
            ),
            StudyMaterial(
                "Approaches to the Mass Gap",
                Level.YANG_MILLS,
                {
                    "overview": "Current approaches and their status",
                    "approaches": [
                        {
                            "name": "Lattice to Continuum",
                            "idea": "Start with rigorous lattice theory, take a → 0",
                            "status": "Continuum limit not proven to exist with mass gap",
                            "key_papers": ["Wilson 1974", "Osterwalder-Seiler 1978"]
                        },
                        {
                            "name": "Constructive QFT",
                            "idea": "Build theory satisfying Wightman axioms directly",
                            "status": "Success in 2D and 3D, not 4D Yang-Mills",
                            "key_results": ["φ⁴ in 2D, 3D", "Gross-Neveu in 2D"]
                        },
                        {
                            "name": "Functional Methods",
                            "idea": "Use Dyson-Schwinger or FRG equations",
                            "status": "Gives evidence but not rigorous proof",
                            "advantage": "Can see mass gap emerge"
                        },
                        {
                            "name": "Geometric/Topological",
                            "idea": "Use geometry of gauge orbit space",
                            "status": "Promising but incomplete",
                            "key_insight": "Gribov copies, topology of configuration space"
                        }
                    ],
                    "what_would_a_proof_need": [
                        "Rigorous construction of continuum limit",
                        "Control over all topological sectors",
                        "Proof of spectral gap for Hamiltonian",
                        "Verification of Wightman/OS axioms"
                    ]
                }
            ),
            StudyMaterial(
                "Mathematical Tools for Yang-Mills",
                Level.YANG_MILLS,
                {
                    "overview": "The mathematical machinery needed",
                    "tools": [
                        {
                            "name": "Uhlenbeck Compactness",
                            "statement": "Connections with bounded curvature have convergent subsequences",
                            "importance": "Allows variational methods in gauge theory"
                        },
                        {
                            "name": "Donaldson Theory",
                            "idea": "Use Yang-Mills moduli spaces for topology",
                            "relevance": "Shows deep structure of gauge theory"
                        },
                        {
                            "name": "Reflection Positivity",
                            "statement": "OS axiom ensuring unitarity",
                            "importance": "Required for physical interpretation"
                        },
                        {
                            "name": "Cluster Decomposition",
                            "statement": "Distant observables become independent",
                            "relation": "Implied by mass gap"
                        }
                    ],
                    "open_questions": [
                        "Does the continuum limit exist?",
                        "Is the limit unique?",
                        "Does it have a mass gap?",
                        "What is the mass gap value?"
                    ]
                }
            )
        ]
    
    def get_materials(self, level: Level) -> List[StudyMaterial]:
        """Get all study materials for a level."""
        return self.materials[level]
    
    def get_material(self, level: Level, title: str) -> Optional[StudyMaterial]:
        """Get a specific study material."""
        for material in self.materials[level]:
            if material.title == title:
                return material
        return None
    
    def get_all_titles(self) -> Dict[Level, List[str]]:
        """Get all material titles organized by level."""
        return {
            level: [m.title for m in materials]
            for level, materials in self.materials.items()
        }


class TestQuestionBank:
    """
    Bank of UNIQUE test questions.
    
    These are NOT from textbooks - they are challenges I CREATE
    to test genuine understanding.
    """
    
    def __init__(self):
        self.questions: Dict[Level, List[TestQuestion]] = {
            level: [] for level in Level
        }
        self._create_questions()
    
    def _create_questions(self):
        """Create unique, AI-challenging test questions."""
        
        # ===== LEVEL 1: FOUNDATIONS =====
        self.questions[Level.FOUNDATIONS] = [
            TestQuestion(
                question_id="F1_CURL_GRADIENT",
                level=Level.FOUNDATIONS,
                difficulty=Difficulty.EASY,
                question="""
                CHALLENGE: Prove that ∇ × (∇f) = 0 for any smooth function f.
                
                But here's the twist: Don't just compute it mechanically.
                Explain WHY this must be true from a geometric/physical perspective.
                What would it mean physically if this weren't true?
                """,
                hints=[
                    "Think about what gradient represents geometrically",
                    "Think about what curl measures",
                    "Consider: can a 'steepest ascent' direction have rotation?"
                ],
                solution_approach="Look for: (1) Correct proof, (2) Geometric insight about gradient being irrotational, (3) Physical interpretation",
                grading_criteria={
                    "correct_proof": 30,
                    "geometric_insight": 40,
                    "physical_interpretation": 30
                },
                requires_concepts=["gradient", "curl", "vector_calculus"]
            ),
            TestQuestion(
                question_id="F2_EIGENVALUE_PHYSICS",
                level=Level.FOUNDATIONS,
                difficulty=Difficulty.MEDIUM,
                question="""
                CHALLENGE: Consider a 2×2 real symmetric matrix A with eigenvalues λ₁ < λ₂.
                
                1. Prove that eigenvectors for distinct eigenvalues are orthogonal.
                2. Now the real challenge: A physical system has energy E = x^T A x 
                   subject to ||x|| = 1. Find the minimum and maximum energy.
                3. Explain why this connects to quantum mechanics.
                """,
                hints=[
                    "For orthogonality: use symmetry A^T = A",
                    "For optimization: think about what directions minimize/maximize",
                    "For QM connection: what are observables in quantum mechanics?"
                ],
                solution_approach="Check: (1) Rigorous orthogonality proof, (2) Correct identification of extrema with eigenvalues, (3) Connection to Hamiltonian and energy eigenstates",
                grading_criteria={
                    "orthogonality_proof": 25,
                    "optimization_solution": 35,
                    "quantum_connection": 40
                },
                requires_concepts=["eigenvalues", "eigenvectors", "optimization", "quantum_mechanics_basics"]
            ),
            TestQuestion(
                question_id="F3_NOETHER_NOVEL",
                level=Level.FOUNDATIONS,
                difficulty=Difficulty.HARD,
                question="""
                CHALLENGE: Consider a particle in 2D with Lagrangian L = (1/2)m(ẋ² + ẏ²) - V(r)
                where r = √(x² + y²).
                
                1. What symmetry does this system have?
                2. Derive the conserved quantity using Noether's theorem.
                3. Now the hard part: Suppose V(r) = kr² + εxy for small ε.
                   How does the conserved quantity change? Is it still exactly conserved?
                   What happens to the orbit?
                """,
                hints=[
                    "The unperturbed system has rotational symmetry",
                    "Angular momentum is conserved for central forces",
                    "The perturbation εxy breaks what symmetry?"
                ],
                solution_approach="Check: (1) Identifies rotational symmetry, (2) Derives angular momentum L = xẏ - yẋ, (3) Correctly analyzes symmetry breaking and approximate conservation",
                grading_criteria={
                    "symmetry_identification": 20,
                    "noether_derivation": 30,
                    "perturbation_analysis": 50
                },
                requires_concepts=["lagrangian_mechanics", "noether_theorem", "symmetry_breaking"]
            ),
            TestQuestion(
                question_id="F4_STOKES_INSIGHT",
                level=Level.FOUNDATIONS,
                difficulty=Difficulty.CHALLENGE,
                question="""
                CHALLENGE: Stokes' theorem says ∫_S (∇×F)·dA = ∮_∂S F·dr.
                
                1. Prove that if ∇×F = 0 everywhere, then ∮_C F·dr = 0 for any closed curve C.
                2. But wait - this isn't always true! Find a counterexample.
                   (Hint: think about domains that aren't simply connected)
                3. Explain how this relates to the Aharonov-Bohm effect in quantum mechanics.
                """,
                hints=[
                    "For part 1: apply Stokes directly",
                    "For part 2: what if there's a 'hole' in the domain?",
                    "For part 3: the magnetic field can be zero where the electron travels, but..."
                ],
                solution_approach="Check: (1) Correct simple proof, (2) Counterexample with non-simply-connected domain (e.g., F = (-y,x,0)/(x²+y²) around origin), (3) Deep connection to AB effect and topology",
                grading_criteria={
                    "simple_proof": 20,
                    "counterexample": 40,
                    "ab_effect_connection": 40
                },
                requires_concepts=["stokes_theorem", "topology", "aharonov_bohm"]
            )
        ]
        
        # ===== LEVEL 2: GEOMETRY & GROUPS =====
        self.questions[Level.GEOMETRY_GROUPS] = [
            TestQuestion(
                question_id="G1_MANIFOLD_CHALLENGE",
                level=Level.GEOMETRY_GROUPS,
                difficulty=Difficulty.EASY,
                question="""
                CHALLENGE: The 2-sphere S² cannot be covered by a single coordinate chart.
                
                1. Prove this rigorously.
                2. What is the minimum number of charts needed?
                3. Generalize: what property of a manifold determines the minimum number of charts?
                """,
                hints=[
                    "A chart is a homeomorphism to an open subset of R²",
                    "S² is compact, R² is not",
                    "Think about the Lusternik-Schnirelmann category"
                ],
                solution_approach="Check: (1) Rigorous proof using compactness, (2) Correct answer (2 charts), (3) Understanding of topological obstructions",
                grading_criteria={
                    "rigorous_proof": 40,
                    "minimum_charts": 20,
                    "generalization": 40
                },
                requires_concepts=["manifolds", "charts", "compactness", "topology"]
            ),
            TestQuestion(
                question_id="G2_LIE_ALGEBRA_NOVEL",
                level=Level.GEOMETRY_GROUPS,
                difficulty=Difficulty.MEDIUM,
                question="""
                CHALLENGE: The Lie algebra su(2) has generators T_a with [T_a, T_b] = iε_{abc}T_c.
                
                1. Show that Tr(T_a T_b) = (1/2)δ_{ab} for the fundamental representation.
                2. Compute the quadratic Casimir C = T_a T_a and show it's proportional to identity.
                3. Now the challenge: For a representation with spin j, what is the eigenvalue of C?
                   Derive this, don't just state it.
                """,
                hints=[
                    "Use the explicit Pauli matrices for part 1",
                    "The Casimir commutes with all generators",
                    "For spin j, the representation has dimension 2j+1"
                ],
                solution_approach="Check: (1) Correct trace calculation, (2) Casimir computation, (3) Derivation of j(j+1) eigenvalue",
                grading_criteria={
                    "trace_calculation": 25,
                    "casimir_computation": 35,
                    "spin_j_derivation": 40
                },
                requires_concepts=["lie_algebras", "su2", "representations", "casimir"]
            ),
            TestQuestion(
                question_id="G3_CURVATURE_PARALLEL",
                level=Level.GEOMETRY_GROUPS,
                difficulty=Difficulty.HARD,
                question="""
                CHALLENGE: On a 2-sphere of radius R, parallel transport a vector around a small 
                triangle with vertices at the north pole and two points on a latitude circle.
                
                1. Show that the vector rotates by an angle equal to the solid angle of the triangle.
                2. Relate this to the Gaussian curvature K = 1/R².
                3. Now generalize: for a general surface, what is the rotation angle in terms of 
                   the curvature integral? Prove your answer.
                """,
                hints=[
                    "Use the fact that geodesics on a sphere are great circles",
                    "The rotation is related to the holonomy",
                    "Gauss-Bonnet theorem is relevant"
                ],
                solution_approach="Check: (1) Correct calculation of rotation angle, (2) Connection to Gaussian curvature, (3) General formula Δθ = ∫∫ K dA with proof",
                grading_criteria={
                    "sphere_calculation": 30,
                    "curvature_connection": 30,
                    "general_proof": 40
                },
                requires_concepts=["parallel_transport", "curvature", "holonomy", "gauss_bonnet"]
            ),
            TestQuestion(
                question_id="G4_FIBER_BUNDLE_NOVEL",
                level=Level.GEOMETRY_GROUPS,
                difficulty=Difficulty.CHALLENGE,
                question="""
                CHALLENGE: Consider a U(1) principal bundle over S² (the base space).
                
                1. Such bundles are classified by an integer n (the first Chern number). 
                   Explain what this integer measures physically.
                2. The case n=1 is the Hopf fibration S³ → S². Describe this explicitly.
                3. Now the real challenge: If we have a connection A on this bundle with 
                   curvature F, prove that (1/2π)∫_{S²} F = n.
                   
                This is the mathematical foundation of magnetic monopoles!
                """,
                hints=[
                    "n counts the 'twist' of the bundle",
                    "S³ can be viewed as unit quaternions",
                    "Use Chern-Weil theory"
                ],
                solution_approach="Check: (1) Physical interpretation (magnetic charge), (2) Correct description of Hopf fibration, (3) Rigorous proof using Chern-Weil",
                grading_criteria={
                    "physical_interpretation": 25,
                    "hopf_fibration": 35,
                    "chern_weil_proof": 40
                },
                requires_concepts=["fiber_bundles", "chern_classes", "hopf_fibration", "magnetic_monopoles"]
            )
        ]
        
        # ===== LEVEL 3: ANALYSIS & TOPOLOGY =====
        self.questions[Level.ANALYSIS_TOPOLOGY] = [
            TestQuestion(
                question_id="A1_SPECTRAL_BASIC",
                level=Level.ANALYSIS_TOPOLOGY,
                difficulty=Difficulty.EASY,
                question="""
                CHALLENGE: Let H be the Hamiltonian of a quantum harmonic oscillator:
                H = -d²/dx² + x² (in appropriate units).
                
                1. The spectrum is σ(H) = {2n+1 : n = 0,1,2,...}. What is the spectral gap?
                2. Prove that the ground state ψ_0(x) = e^{-x²/2} satisfies Hψ_0 = ψ_0.
                3. Explain why the spectral gap implies exponential decay of correlations.
                """,
                hints=[
                    "Spectral gap = E_1 - E_0",
                    "Just compute Hψ_0 directly",
                    "Think about the propagator e^{-Ht}"
                ],
                solution_approach="Check: (1) Correct gap = 2, (2) Verification calculation, (3) Connection to correlation decay",
                grading_criteria={
                    "spectral_gap": 25,
                    "ground_state_verification": 35,
                    "correlation_decay": 40
                },
                requires_concepts=["spectral_theory", "quantum_mechanics", "correlation_functions"]
            ),
            TestQuestion(
                question_id="A2_HOMOTOPY_PHYSICS",
                level=Level.ANALYSIS_TOPOLOGY,
                difficulty=Difficulty.MEDIUM,
                question="""
                CHALLENGE: The group SU(2) is topologically a 3-sphere S³.
                
                1. Prove that π_3(SU(2)) = Z. What does this integer classify?
                2. In Yang-Mills theory, this integer is the instanton number. 
                   Write down the formula for the instanton number in terms of the field strength F.
                3. Explain why instantons contribute to the path integral even though 
                   they are not perturbative.
                """,
                hints=[
                    "π_3(S³) = Z by the Hopf degree theorem",
                    "The instanton number involves ∫ Tr(F∧F)",
                    "Instantons are saddle points of the Euclidean action"
                ],
                solution_approach="Check: (1) Correct proof/argument for π_3, (2) Correct formula Q = (1/32π²)∫Tr(F∧F), (3) Understanding of non-perturbative contributions",
                grading_criteria={
                    "homotopy_proof": 30,
                    "instanton_formula": 30,
                    "non_perturbative_understanding": 40
                },
                requires_concepts=["homotopy_groups", "instantons", "path_integral"]
            ),
            TestQuestion(
                question_id="A3_SOBOLEV_GAUGE",
                level=Level.ANALYSIS_TOPOLOGY,
                difficulty=Difficulty.HARD,
                question="""
                CHALLENGE: In gauge theory, we need connections A with finite Yang-Mills action:
                S[A] = ∫ |F_A|² d⁴x < ∞.
                
                1. What Sobolev space should A belong to? Justify your answer.
                2. The Uhlenbeck compactness theorem says: sequences of connections with 
                   bounded action have convergent subsequences (after gauge transformation).
                   Why is the "after gauge transformation" crucial?
                3. How does this theorem enable variational methods in gauge theory?
                """,
                hints=[
                    "F involves first derivatives of A",
                    "Gauge transformations can be 'large'",
                    "Variational methods need compactness to find minimizers"
                ],
                solution_approach="Check: (1) A ∈ W^{1,2} with justification, (2) Understanding of gauge orbit issues, (3) Connection to existence of Yang-Mills minimizers",
                grading_criteria={
                    "sobolev_space": 30,
                    "gauge_transformation_role": 35,
                    "variational_methods": 35
                },
                requires_concepts=["sobolev_spaces", "gauge_theory", "uhlenbeck_compactness"]
            ),
            TestQuestion(
                question_id="A4_INDEX_THEOREM_NOVEL",
                level=Level.ANALYSIS_TOPOLOGY,
                difficulty=Difficulty.CHALLENGE,
                question="""
                CHALLENGE: The Atiyah-Singer index theorem connects analysis to topology.
                
                1. For the Dirac operator D on a 4-manifold with gauge field, 
                   index(D) = n_+ - n_- where n_± are numbers of zero modes with ±chirality.
                   Express this in terms of the instanton number.
                   
                2. In QCD, this has physical consequences. If there are N_f massless quarks,
                   how many zero modes does an instanton with charge Q have?
                   
                3. This leads to the 't Hooft vertex. Explain why instantons can change
                   the number of quarks (violate fermion number conservation).
                """,
                hints=[
                    "index(D) = Q for SU(N) gauge theory",
                    "Each quark flavor contributes independently",
                    "Zero modes allow fermion number violation"
                ],
                solution_approach="Check: (1) Correct index formula, (2) N_f|Q| zero modes, (3) Understanding of anomalous fermion number violation",
                grading_criteria={
                    "index_formula": 30,
                    "zero_mode_counting": 30,
                    "thooft_vertex": 40
                },
                requires_concepts=["index_theorem", "instantons", "anomalies", "qcd"]
            )
        ]
        
        # ===== LEVEL 4: FIELD THEORY =====
        self.questions[Level.FIELD_THEORY] = [
            TestQuestion(
                question_id="FT1_YANG_MILLS_DERIVE",
                level=Level.FIELD_THEORY,
                difficulty=Difficulty.EASY,
                question="""
                CHALLENGE: Starting from the Yang-Mills action S = -(1/4)∫ Tr(F_μν F^μν) d⁴x,
                
                1. Derive the Yang-Mills equations of motion D_μ F^μν = 0.
                2. Show that the Bianchi identity D_μ F̃^μν = 0 is automatic 
                   (where F̃ is the dual field strength).
                3. Compare to Maxwell's equations. What's the key difference?
                """,
                hints=[
                    "Vary with respect to A_μ",
                    "Bianchi identity follows from F = dA + A∧A",
                    "The difference is in the covariant derivative"
                ],
                solution_approach="Check: (1) Correct derivation, (2) Bianchi identity proof, (3) Identification of non-linear terms",
                grading_criteria={
                    "equations_derivation": 35,
                    "bianchi_identity": 30,
                    "maxwell_comparison": 35
                },
                requires_concepts=["yang_mills", "variational_principle", "bianchi_identity"]
            ),
            TestQuestion(
                question_id="FT2_ASYMPTOTIC_FREEDOM",
                level=Level.FIELD_THEORY,
                difficulty=Difficulty.MEDIUM,
                question="""
                CHALLENGE: The beta function for SU(N) Yang-Mills is β(g) = -β_0 g³ + O(g⁵)
                where β_0 = (11N)/(48π²).
                
                1. Solve the RG equation μ dg/dμ = β(g) to find g(μ).
                2. Define Λ_QCD and express g(μ) in terms of Λ_QCD.
                3. What happens as μ → ∞? As μ → Λ_QCD?
                4. Explain why this means perturbation theory fails at low energies.
                """,
                hints=[
                    "Separate variables and integrate",
                    "Λ_QCD is the scale where g becomes large",
                    "The coupling 'runs' with energy scale"
                ],
                solution_approach="Check: (1) Correct solution g²(μ) = g²(μ_0)/[1 + β_0 g²(μ_0) ln(μ/μ_0)], (2) Λ_QCD definition, (3) UV freedom, IR slavery, (4) Perturbation theory breakdown",
                grading_criteria={
                    "rg_solution": 30,
                    "lambda_qcd": 25,
                    "asymptotic_behavior": 25,
                    "perturbation_breakdown": 20
                },
                requires_concepts=["beta_function", "renormalization_group", "asymptotic_freedom"]
            ),
            TestQuestion(
                question_id="FT3_WILSON_LOOP",
                level=Level.FIELD_THEORY,
                difficulty=Difficulty.HARD,
                question="""
                CHALLENGE: The Wilson loop is W(C) = Tr P exp(i∮_C A).
                
                1. Prove that W(C) is gauge invariant.
                2. For a rectangular loop of size R × T in Euclidean space,
                   ⟨W(C)⟩ ~ exp(-V(R)T) for large T, where V(R) is the quark-antiquark potential.
                   Derive this relation.
                3. Confinement means V(R) ~ σR for large R. What does ⟨W(C)⟩ behave like
                   for a large square loop of size L × L? This is the "area law."
                """,
                hints=[
                    "Under gauge transformation, A → gAg^{-1} + g∂g^{-1}",
                    "Think of the Wilson loop as a quark-antiquark propagator",
                    "Area law means ⟨W⟩ ~ exp(-σ × Area)"
                ],
                solution_approach="Check: (1) Correct gauge invariance proof, (2) Derivation of potential relation, (3) Area law with correct interpretation",
                grading_criteria={
                    "gauge_invariance": 30,
                    "potential_derivation": 35,
                    "area_law": 35
                },
                requires_concepts=["wilson_loops", "confinement", "gauge_invariance"]
            ),
            TestQuestion(
                question_id="FT4_LATTICE_CONTINUUM",
                level=Level.FIELD_THEORY,
                difficulty=Difficulty.CHALLENGE,
                question="""
                CHALLENGE: On the lattice, the gauge field is replaced by link variables U_μ(x) ∈ SU(N).
                
                1. The Wilson action is S = β Σ_P (1 - (1/N)Re Tr U_P) where U_P is the plaquette.
                   Show that as a → 0, this reduces to the continuum Yang-Mills action.
                   (Hint: U_μ(x) ≈ exp(iaA_μ(x)))
                   
                2. The lattice spacing a must be sent to zero while keeping physics fixed.
                   Using asymptotic freedom, show that β → ∞ as a → 0.
                   
                3. This is the "continuum limit." Why is it so hard to prove this limit exists
                   rigorously with a mass gap?
                """,
                hints=[
                    "Expand U_P to order a⁴",
                    "β = 2N/g² and g → 0 as a → 0",
                    "The limit involves infinitely many degrees of freedom"
                ],
                solution_approach="Check: (1) Correct expansion showing S → (1/4)∫Tr(F²), (2) β ~ -ln(aΛ) behavior, (3) Understanding of rigorous difficulties",
                grading_criteria={
                    "continuum_expansion": 35,
                    "beta_behavior": 30,
                    "rigorous_difficulties": 35
                },
                requires_concepts=["lattice_gauge_theory", "continuum_limit", "asymptotic_freedom"]
            )
        ]
        
        # ===== LEVEL 5: YANG-MILLS =====
        self.questions[Level.YANG_MILLS] = [
            TestQuestion(
                question_id="YM1_MASS_GAP_STATEMENT",
                level=Level.YANG_MILLS,
                difficulty=Difficulty.MEDIUM,
                question="""
                CHALLENGE: State the Yang-Mills mass gap problem precisely.
                
                1. What are the Wightman axioms? List them and explain their physical meaning.
                2. What does it mean for a QFT to "have a mass gap"? 
                   Give both the spectral definition and the correlation function definition.
                3. Why can't we just use perturbation theory to prove the mass gap?
                   What goes wrong?
                """,
                hints=[
                    "Wightman axioms include Lorentz covariance, positivity, locality...",
                    "Mass gap means E_1 - E_0 > 0 OR correlations decay exponentially",
                    "Perturbation theory sees massless gluons"
                ],
                solution_approach="Check: (1) Complete list of Wightman axioms, (2) Both definitions of mass gap, (3) Understanding of perturbative failure",
                grading_criteria={
                    "wightman_axioms": 35,
                    "mass_gap_definitions": 35,
                    "perturbation_failure": 30
                },
                requires_concepts=["wightman_axioms", "mass_gap", "perturbation_theory"]
            ),
            TestQuestion(
                question_id="YM2_APPROACHES",
                level=Level.YANG_MILLS,
                difficulty=Difficulty.HARD,
                question="""
                CHALLENGE: Compare and contrast three approaches to proving the mass gap:
                
                1. Lattice approach: What has been proven? What remains to be proven?
                2. Constructive QFT approach: What successes exist in lower dimensions?
                   Why is 4D harder?
                3. Functional RG approach: How does the Wetterich equation give evidence
                   for the mass gap? Why isn't this a proof?
                   
                For each, identify the key mathematical obstacle.
                """,
                hints=[
                    "Lattice: continuum limit is the issue",
                    "Constructive: 4D has worse divergences",
                    "FRG: truncations are not rigorous"
                ],
                solution_approach="Check: (1) Correct assessment of lattice status, (2) Understanding of dimensional dependence, (3) FRG limitations",
                grading_criteria={
                    "lattice_assessment": 35,
                    "constructive_assessment": 35,
                    "frg_assessment": 30
                },
                requires_concepts=["lattice_gauge_theory", "constructive_qft", "functional_rg"]
            ),
            TestQuestion(
                question_id="YM3_NOVEL_APPROACH",
                level=Level.YANG_MILLS,
                difficulty=Difficulty.CHALLENGE,
                question="""
                ULTIMATE CHALLENGE: Propose a novel approach to the Yang-Mills mass gap problem.
                
                Your proposal should:
                1. Identify a key insight or connection that hasn't been fully exploited.
                2. Outline a strategy that could lead to a proof.
                3. Identify the main obstacles your approach would face.
                4. Explain why you believe this approach has promise.
                
                Be creative but rigorous. This is what real mathematical research looks like.
                
                Note: There is no "correct" answer - this tests your ability to think 
                originally about an unsolved problem.
                """,
                hints=[
                    "Consider connections to other areas of mathematics",
                    "Think about what makes Yang-Mills special",
                    "Look for analogies with solved problems"
                ],
                solution_approach="Evaluate: (1) Novelty and creativity, (2) Mathematical rigor, (3) Awareness of obstacles, (4) Plausibility of approach",
                grading_criteria={
                    "novelty": 30,
                    "rigor": 25,
                    "obstacle_awareness": 25,
                    "plausibility": 20
                },
                requires_concepts=["yang_mills", "mass_gap", "mathematical_research"]
            )
        ]
    
    def get_questions(self, level: Level) -> List[TestQuestion]:
        """Get all questions for a level."""
        return self.questions[level]
    
    def get_question(self, question_id: str) -> Optional[TestQuestion]:
        """Get a specific question by ID."""
        for level_questions in self.questions.values():
            for q in level_questions:
                if q.question_id == question_id:
                    return q
        return None
    
    def get_questions_by_difficulty(self, level: Level, difficulty: Difficulty) -> List[TestQuestion]:
        """Get questions of a specific difficulty."""
        return [q for q in self.questions[level] if q.difficulty == difficulty]


class ProgressiveLearningSystem:
    """
    The complete Progressive Learning System.
    
    Combines:
    - Study materials (for learning)
    - Test questions (unique challenges)
    - Progress tracking (advancement)
    """
    
    def __init__(self):
        self.study_library = StudyMaterialsLibrary()
        self.question_bank = TestQuestionBank()
        self.framework_progress: Dict[str, FrameworkProgress] = {}
        
        print("="*60)
        print("PROGRESSIVE LEARNING SYSTEM INITIALIZED")
        print("="*60)
        print(f"Study Materials: {sum(len(m) for m in self.study_library.materials.values())} across 5 levels")
        print(f"Test Questions: {sum(len(q) for q in self.question_bank.questions.values())} unique challenges")
        print("="*60)
    
    def register_framework(self, name: str) -> FrameworkProgress:
        """Register a framework for learning."""
        if name not in self.framework_progress:
            self.framework_progress[name] = FrameworkProgress(name)
            print(f"✓ Registered {name} for learning (starting at Level 1: FOUNDATIONS)")
        return self.framework_progress[name]
    
    def get_study_materials(self, framework: str, level: Level = None) -> List[Dict]:
        """Get study materials for a framework."""
        progress = self.framework_progress.get(framework)
        if not progress:
            return []
        
        # Use current level if not specified
        if level is None:
            level = progress.current_level
        
        # Can only access current level or below
        if level.value > progress.current_level.value:
            return []  # Not unlocked yet
        
        materials = self.study_library.get_materials(level)
        
        # Record access
        for m in materials:
            progress.record_study(m.title, level)
        
        return [m.to_dict() for m in materials]
    
    def get_test_questions(self, framework: str, level: Level = None) -> List[Dict]:
        """Get test questions for a framework."""
        progress = self.framework_progress.get(framework)
        if not progress:
            return []
        
        # Use current level if not specified
        if level is None:
            level = progress.current_level
        
        # Can only access current level
        if level.value > progress.current_level.value:
            return []  # Not unlocked yet
        
        questions = self.question_bank.get_questions(level)
        return [q.to_dict() for q in questions]
    
    def submit_answer(self, framework: str, question_id: str, answer: str) -> Dict:
        """Submit an answer to a test question."""
        progress = self.framework_progress.get(framework)
        if not progress:
            return {"error": "Framework not registered"}
        
        question = self.question_bank.get_question(question_id)
        if not question:
            return {"error": "Question not found"}
        
        # Check if question is at appropriate level
        if question.level.value > progress.current_level.value:
            return {"error": "Question not unlocked yet"}
        
        # Grade the answer (simplified - in reality this would be more sophisticated)
        # For now, we'll return feedback and let the system evaluate
        feedback = {
            "question_id": question_id,
            "submitted_answer": answer,
            "grading_criteria": question.grading_criteria,
            "solution_approach": question.solution_approach,
            "status": "submitted_for_review"
        }
        
        return feedback
    
    def record_result(self, framework: str, question_id: str, 
                     score: float, feedback: str, passed: bool):
        """Record the result of a graded answer."""
        progress = self.framework_progress.get(framework)
        if not progress:
            return
        
        question = self.question_bank.get_question(question_id)
        if not question:
            return
        
        progress.record_attempt(question_id, "", score, feedback)
        
        if passed:
            progress.mark_passed(question_id, question.level)
    
    def check_advancement(self, framework: str) -> Dict:
        """Check if a framework can advance to the next level."""
        progress = self.framework_progress.get(framework)
        if not progress:
            return {"error": "Framework not registered"}
        
        can_advance = progress.can_advance()
        current_level = progress.current_level
        
        result = {
            "framework": framework,
            "current_level": current_level.name,
            "questions_passed": len(progress.passed_questions[current_level]),
            "required_to_advance": 3,
            "can_advance": can_advance
        }
        
        if can_advance and current_level != Level.YANG_MILLS:
            next_level = Level(current_level.value + 1)
            result["next_level"] = next_level.name
        
        return result
    
    def advance_framework(self, framework: str) -> Dict:
        """Advance a framework to the next level."""
        progress = self.framework_progress.get(framework)
        if not progress:
            return {"error": "Framework not registered"}
        
        old_level = progress.current_level
        
        if progress.advance_level():
            return {
                "success": True,
                "old_level": old_level.name,
                "new_level": progress.current_level.name,
                "message": f"Congratulations! {framework} has advanced to {progress.current_level.name}!"
            }
        else:
            return {
                "success": False,
                "current_level": old_level.name,
                "message": "Cannot advance yet. Need to pass more questions."
            }
    
    def get_progress_summary(self, framework: str) -> Dict:
        """Get a summary of a framework's progress."""
        progress = self.framework_progress.get(framework)
        if not progress:
            return {"error": "Framework not registered"}
        
        return progress.get_summary()
    
    def get_all_progress(self) -> Dict:
        """Get progress for all frameworks."""
        return {
            name: progress.get_summary()
            for name, progress in self.framework_progress.items()
        }


# Global instance
_learning_system = None

def get_learning_system() -> ProgressiveLearningSystem:
    """Get the global Progressive Learning System instance."""
    global _learning_system
    if _learning_system is None:
        _learning_system = ProgressiveLearningSystem()
    return _learning_system
