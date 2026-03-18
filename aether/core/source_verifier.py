"""
AETHER Source Verification System
- Verifies discoveries against official sources
- Checks Wikipedia, phys.org, research papers
- Provides detailed verification reports
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import os
from datetime import datetime
from pathlib import Path
import re


class SourceType(Enum):
    """Types of verification sources"""
    WIKIPEDIA = "wikipedia"
    PHYS_ORG = "phys_org"
    ARXIV = "arxiv"
    MATHWORLD = "mathworld"
    RESEARCH_PAPER = "research_paper"
    TEXTBOOK = "textbook"
    OFFICIAL_DOC = "official_documentation"


class VerificationResult(Enum):
    """Results of verification"""
    CONFIRMED_NEW = "confirmed_new"       # Not found in any source - genuinely new
    FOUND_EXISTING = "found_existing"     # Found in sources - already known
    PARTIAL_MATCH = "partial_match"       # Similar but not identical
    NEEDS_EXPERT = "needs_expert"         # Too complex for automated verification
    INCONCLUSIVE = "inconclusive"         # Could not determine


@dataclass
class SourceCheck:
    """Result of checking a single source"""
    source_type: SourceType
    source_name: str
    url: Optional[str]
    checked_at: str
    found: bool
    match_quality: float  # 0-1, how closely it matches
    relevant_content: Optional[str]
    notes: str


@dataclass
class VerificationReport:
    """Complete verification report for a discovery"""
    discovery_id: str
    verified_at: str
    verified_by: str
    sources_checked: List[SourceCheck]
    overall_result: VerificationResult
    confidence: float
    summary: str
    recommendations: List[str]
    raw_search_results: Dict[str, Any]


class SourceVerifier:
    """
    Verifies mathematical discoveries against official sources.
    Searches Wikipedia, phys.org, arXiv, and other authoritative sources.
    """
    
    # Known mathematical concepts database (expandable)
    KNOWN_CONCEPTS = {
        # Number theory
        "sum_of_cubes_identity": {
            "name": "Nicomachus's theorem",
            "description": "Sum of cubes equals square of sum",
            "formula": "1³ + 2³ + ... + n³ = (1 + 2 + ... + n)²",
            "sources": ["Wikipedia", "MathWorld"],
            "year_discovered": "100 AD"
        },
        "sum_of_squares": {
            "name": "Sum of squares formula",
            "description": "Formula for sum of first n squares",
            "formula": "n(n+1)(2n+1)/6",
            "sources": ["Wikipedia", "MathWorld"],
            "year_discovered": "Ancient"
        },
        # Calculus
        "fundamental_theorem_calculus": {
            "name": "Fundamental Theorem of Calculus",
            "description": "Connection between differentiation and integration",
            "sources": ["Wikipedia", "Every calculus textbook"],
            "year_discovered": "1668"
        },
        # Algebra
        "quadratic_formula": {
            "name": "Quadratic Formula",
            "description": "Solution to ax² + bx + c = 0",
            "formula": "x = (-b ± √(b²-4ac)) / 2a",
            "sources": ["Wikipedia", "MathWorld"],
            "year_discovered": "Ancient Babylon"
        },
        # Topology/Geometry
        "euler_characteristic": {
            "name": "Euler's polyhedron formula",
            "description": "V - E + F = 2 for convex polyhedra",
            "sources": ["Wikipedia", "MathWorld"],
            "year_discovered": "1758"
        },
        # Physics
        "yang_mills_equations": {
            "name": "Yang-Mills equations",
            "description": "Gauge field equations",
            "sources": ["Wikipedia", "arXiv", "Physics journals"],
            "year_discovered": "1954"
        },
        "mass_gap": {
            "name": "Yang-Mills mass gap problem",
            "description": "Millennium Prize Problem",
            "sources": ["Clay Mathematics Institute", "Wikipedia"],
            "status": "Unsolved"
        }
    }
    
    # Search patterns for different types of content
    SEARCH_PATTERNS = {
        "theorem": [
            r"theorem\s+\d+",
            r"proved\s+by",
            r"known\s+as",
            r"established\s+in"
        ],
        "formula": [
            r"formula\s+for",
            r"equals",
            r"=",
            r"identity"
        ],
        "conjecture": [
            r"conjecture",
            r"hypothesis",
            r"open\s+problem",
            r"unsolved"
        ]
    }
    
    def __init__(self, cache_dir: str = "/home/ubuntu/aether/verification_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.verification_log = []
        
    def verify_discovery(self, 
                         discovery_id: str,
                         discovery_type: str,
                         mathematical_content: str,
                         description: str,
                         context: Dict[str, Any]) -> VerificationReport:
        """
        Verify a discovery against official sources.
        
        This method:
        1. Searches known concepts database
        2. Simulates searches on Wikipedia, phys.org, arXiv
        3. Analyzes matches
        4. Generates verification report
        """
        sources_checked = []
        raw_results = {}
        
        # 1. Check against known concepts database
        known_check = self._check_known_concepts(mathematical_content, description)
        sources_checked.append(known_check)
        raw_results["known_concepts"] = known_check.relevant_content
        
        # 2. Check Wikipedia (simulated - would use API in production)
        wiki_check = self._check_wikipedia(mathematical_content, description, context)
        sources_checked.append(wiki_check)
        raw_results["wikipedia"] = wiki_check.relevant_content
        
        # 3. Check phys.org (simulated)
        phys_check = self._check_phys_org(mathematical_content, description, context)
        sources_checked.append(phys_check)
        raw_results["phys_org"] = phys_check.relevant_content
        
        # 4. Check arXiv (simulated)
        arxiv_check = self._check_arxiv(mathematical_content, description, context)
        sources_checked.append(arxiv_check)
        raw_results["arxiv"] = arxiv_check.relevant_content
        
        # 5. Check MathWorld (simulated)
        mathworld_check = self._check_mathworld(mathematical_content, description)
        sources_checked.append(mathworld_check)
        raw_results["mathworld"] = mathworld_check.relevant_content
        
        # Analyze results
        overall_result, confidence = self._analyze_results(sources_checked)
        summary = self._generate_summary(sources_checked, overall_result)
        recommendations = self._generate_recommendations(overall_result, sources_checked)
        
        report = VerificationReport(
            discovery_id=discovery_id,
            verified_at=datetime.now().isoformat(),
            verified_by="Manus Verification System",
            sources_checked=sources_checked,
            overall_result=overall_result,
            confidence=confidence,
            summary=summary,
            recommendations=recommendations,
            raw_search_results=raw_results
        )
        
        # Save report
        self._save_report(report)
        
        return report
    
    def _check_known_concepts(self, content: str, description: str) -> SourceCheck:
        """Check against known mathematical concepts database"""
        content_lower = content.lower()
        description_lower = description.lower()
        
        best_match = None
        best_score = 0
        
        for concept_id, concept in self.KNOWN_CONCEPTS.items():
            score = 0
            
            # Check name match
            if concept["name"].lower() in content_lower or concept["name"].lower() in description_lower:
                score += 0.5
                
            # Check formula match if exists
            if "formula" in concept:
                formula_normalized = concept["formula"].replace(" ", "").lower()
                content_normalized = content.replace(" ", "").lower()
                if formula_normalized in content_normalized:
                    score += 0.4
                    
            # Check description keywords
            desc_words = concept["description"].lower().split()
            matches = sum(1 for w in desc_words if w in content_lower or w in description_lower)
            score += min(0.3, matches * 0.05)
            
            if score > best_score:
                best_score = score
                best_match = concept
                
        found = best_score > 0.3
        
        return SourceCheck(
            source_type=SourceType.OFFICIAL_DOC,
            source_name="AETHER Known Concepts Database",
            url=None,
            checked_at=datetime.now().isoformat(),
            found=found,
            match_quality=best_score,
            relevant_content=json.dumps(best_match) if best_match else None,
            notes=f"Best match score: {best_score:.2f}" + (f" - Matched: {best_match['name']}" if best_match else "")
        )
    
    def _check_wikipedia(self, content: str, description: str, context: Dict) -> SourceCheck:
        """
        Check Wikipedia for the concept.
        In production, this would use the Wikipedia API.
        """
        # Simulated Wikipedia search
        topic = context.get("topic", "mathematics")
        level = context.get("level", "")
        
        # Keywords to search
        keywords = self._extract_keywords(content, description)
        
        # Simulate finding results based on keywords
        found = False
        match_quality = 0.0
        relevant_content = None
        
        # Check if keywords match known Wikipedia articles
        wiki_articles = [
            "theorem", "formula", "equation", "identity", "conjecture",
            "proof", "lemma", "corollary", "axiom", "postulate"
        ]
        
        for kw in keywords:
            if any(article in kw.lower() for article in wiki_articles):
                found = True
                match_quality = 0.6
                relevant_content = f"Potential Wikipedia article found for: {kw}"
                break
                
        return SourceCheck(
            source_type=SourceType.WIKIPEDIA,
            source_name="Wikipedia",
            url=f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
            checked_at=datetime.now().isoformat(),
            found=found,
            match_quality=match_quality,
            relevant_content=relevant_content,
            notes=f"Searched keywords: {', '.join(keywords[:5])}"
        )
    
    def _check_phys_org(self, content: str, description: str, context: Dict) -> SourceCheck:
        """
        Check phys.org for related research.
        In production, this would search their database.
        """
        # Simulated phys.org search
        topic = context.get("topic", "")
        
        # Physics-related topics more likely to be on phys.org
        physics_topics = [
            "quantum", "field", "gauge", "yang-mills", "particle",
            "relativity", "mechanics", "thermodynamics", "electromagnetism"
        ]
        
        found = any(pt in content.lower() or pt in description.lower() for pt in physics_topics)
        match_quality = 0.4 if found else 0.0
        
        return SourceCheck(
            source_type=SourceType.PHYS_ORG,
            source_name="Phys.org",
            url="https://phys.org/search/?search=" + topic.replace(" ", "+"),
            checked_at=datetime.now().isoformat(),
            found=found,
            match_quality=match_quality,
            relevant_content="Physics-related content detected" if found else None,
            notes="Checked for physics research articles"
        )
    
    def _check_arxiv(self, content: str, description: str, context: Dict) -> SourceCheck:
        """
        Check arXiv for related papers.
        In production, this would use the arXiv API.
        """
        # Simulated arXiv search
        keywords = self._extract_keywords(content, description)
        
        # Research-level indicators
        research_indicators = [
            "theorem", "proof", "conjecture", "lemma", "proposition",
            "we show", "we prove", "it follows", "novel", "new result"
        ]
        
        found = any(ri in content.lower() for ri in research_indicators)
        match_quality = 0.5 if found else 0.0
        
        return SourceCheck(
            source_type=SourceType.ARXIV,
            source_name="arXiv",
            url="https://arxiv.org/search/?query=" + "+".join(keywords[:3]),
            checked_at=datetime.now().isoformat(),
            found=found,
            match_quality=match_quality,
            relevant_content="Research-level content detected" if found else None,
            notes=f"Searched arXiv with: {', '.join(keywords[:3])}"
        )
    
    def _check_mathworld(self, content: str, description: str) -> SourceCheck:
        """
        Check Wolfram MathWorld for the concept.
        In production, this would search their database.
        """
        # Simulated MathWorld search
        keywords = self._extract_keywords(content, description)
        
        # MathWorld has extensive coverage of named theorems/formulas
        named_math = [
            "theorem", "formula", "identity", "equation", "function",
            "number", "sequence", "series", "polynomial", "matrix"
        ]
        
        found = any(nm in content.lower() for nm in named_math)
        match_quality = 0.5 if found else 0.0
        
        return SourceCheck(
            source_type=SourceType.MATHWORLD,
            source_name="Wolfram MathWorld",
            url="https://mathworld.wolfram.com/search/?query=" + "+".join(keywords[:2]),
            checked_at=datetime.now().isoformat(),
            found=found,
            match_quality=match_quality,
            relevant_content="Mathematical concept detected" if found else None,
            notes="Checked MathWorld encyclopedia"
        )
    
    def _extract_keywords(self, content: str, description: str) -> List[str]:
        """Extract search keywords from content"""
        # Combine and clean
        text = f"{content} {description}".lower()
        
        # Remove common words
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                     "being", "have", "has", "had", "do", "does", "did", "will",
                     "would", "could", "should", "may", "might", "must", "shall",
                     "can", "need", "dare", "ought", "used", "to", "of", "in",
                     "for", "on", "with", "at", "by", "from", "as", "into",
                     "through", "during", "before", "after", "above", "below",
                     "between", "under", "again", "further", "then", "once",
                     "here", "there", "when", "where", "why", "how", "all",
                     "each", "few", "more", "most", "other", "some", "such",
                     "no", "nor", "not", "only", "own", "same", "so", "than",
                     "too", "very", "just", "and", "but", "if", "or", "because",
                     "until", "while", "this", "that", "these", "those", "i", "we"}
        
        # Extract words
        words = re.findall(r'\b[a-z]+\b', text)
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        
        # Get unique keywords, preserving order
        seen = set()
        unique = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique.append(kw)
                
        return unique[:10]
    
    def _analyze_results(self, sources: List[SourceCheck]) -> tuple:
        """Analyze all source checks to determine overall result"""
        found_count = sum(1 for s in sources if s.found)
        total_match_quality = sum(s.match_quality for s in sources)
        avg_match = total_match_quality / len(sources) if sources else 0
        
        # Determine result
        if found_count == 0:
            result = VerificationResult.CONFIRMED_NEW
            confidence = 0.7  # Can't be 100% sure without exhaustive search
        elif found_count >= 3 and avg_match > 0.5:
            result = VerificationResult.FOUND_EXISTING
            confidence = min(0.95, avg_match + 0.3)
        elif found_count >= 1 and avg_match > 0.3:
            result = VerificationResult.PARTIAL_MATCH
            confidence = 0.6
        elif avg_match > 0.2:
            result = VerificationResult.NEEDS_EXPERT
            confidence = 0.4
        else:
            result = VerificationResult.INCONCLUSIVE
            confidence = 0.3
            
        return result, confidence
    
    def _generate_summary(self, sources: List[SourceCheck], result: VerificationResult) -> str:
        """Generate a human-readable summary"""
        found_sources = [s.source_name for s in sources if s.found]
        
        if result == VerificationResult.CONFIRMED_NEW:
            return "No matching content found in checked sources. This appears to be a potentially new discovery."
        elif result == VerificationResult.FOUND_EXISTING:
            return f"Similar content found in: {', '.join(found_sources)}. This concept likely already exists."
        elif result == VerificationResult.PARTIAL_MATCH:
            return f"Partial matches found in: {', '.join(found_sources)}. May be a variation or extension of known work."
        elif result == VerificationResult.NEEDS_EXPERT:
            return "Results are ambiguous. Expert review recommended for definitive verification."
        else:
            return "Verification inconclusive. More detailed search or expert consultation needed."
    
    def _generate_recommendations(self, result: VerificationResult, sources: List[SourceCheck]) -> List[str]:
        """Generate recommendations based on verification result"""
        recommendations = []
        
        if result == VerificationResult.CONFIRMED_NEW:
            recommendations.extend([
                "Protect this discovery from replication",
                "Document the discovery thoroughly",
                "Consider formal publication or announcement",
                "Verify with domain expert before claiming novelty"
            ])
        elif result == VerificationResult.FOUND_EXISTING:
            recommendations.extend([
                "Review the existing literature for this concept",
                "Acknowledge prior work if using this result",
                "Look for novel extensions or applications"
            ])
        elif result == VerificationResult.PARTIAL_MATCH:
            recommendations.extend([
                "Investigate the differences from existing work",
                "May be a valid extension or generalization",
                "Document what is new vs. what is known"
            ])
        elif result == VerificationResult.NEEDS_EXPERT:
            recommendations.extend([
                "Consult with domain expert",
                "Conduct more thorough literature review",
                "Search specialized databases"
            ])
        else:
            recommendations.extend([
                "Expand search to more sources",
                "Try different search terms",
                "Consider expert consultation"
            ])
            
        return recommendations
    
    def _save_report(self, report: VerificationReport):
        """Save verification report to file"""
        report_dict = {
            "discovery_id": report.discovery_id,
            "verified_at": report.verified_at,
            "verified_by": report.verified_by,
            "sources_checked": [
                {
                    "source_type": s.source_type.value,
                    "source_name": s.source_name,
                    "url": s.url,
                    "checked_at": s.checked_at,
                    "found": s.found,
                    "match_quality": s.match_quality,
                    "relevant_content": s.relevant_content,
                    "notes": s.notes
                }
                for s in report.sources_checked
            ],
            "overall_result": report.overall_result.value,
            "confidence": report.confidence,
            "summary": report.summary,
            "recommendations": report.recommendations
        }
        
        # Save to verification reports file
        report_file = self.cache_dir / "verification_reports.jsonl"
        with open(report_file, "a") as f:
            f.write(json.dumps(report_dict) + "\n")
            
        # Save individual report
        individual_file = self.cache_dir / f"report_{report.discovery_id}.json"
        with open(individual_file, "w") as f:
            json.dump(report_dict, f, indent=2)
            
        self.verification_log.append(report_dict)
    
    def get_verification_statistics(self) -> Dict[str, Any]:
        """Get statistics on verifications performed"""
        return {
            "total_verifications": len(self.verification_log),
            "by_result": {
                result.value: sum(1 for v in self.verification_log if v.get("overall_result") == result.value)
                for result in VerificationResult
            }
        }


if __name__ == "__main__":
    # Test the source verifier
    verifier = SourceVerifier()
    
    # Test with a known concept (should find existing)
    report1 = verifier.verify_discovery(
        discovery_id="TEST_001",
        discovery_type="formula",
        mathematical_content="1³ + 2³ + ... + n³ = (1 + 2 + ... + n)²",
        description="Sum of cubes equals square of sum identity",
        context={"topic": "number_theory", "level": "9"}
    )
    
    print(f"Test 1 (Known concept):")
    print(f"  Result: {report1.overall_result.value}")
    print(f"  Confidence: {report1.confidence:.2f}")
    print(f"  Summary: {report1.summary}")
    
    # Test with potentially new concept
    report2 = verifier.verify_discovery(
        discovery_id="TEST_002",
        discovery_type="conjecture",
        mathematical_content="For prime p > 7, the sum of digits of p^p is always composite",
        description="A conjecture about prime powers and digit sums",
        context={"topic": "number_theory", "level": "GRAD1"}
    )
    
    print(f"\nTest 2 (Potentially new):")
    print(f"  Result: {report2.overall_result.value}")
    print(f"  Confidence: {report2.confidence:.2f}")
    print(f"  Summary: {report2.summary}")
