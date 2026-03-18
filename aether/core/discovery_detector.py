"""
AETHER Discovery Detection System
- Detects potentially new mathematical problems/formulas
- Flags for Manus formal review
- Prevents replication until verified
- Tracks discovery provenance
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import json
import hashlib
import os
from datetime import datetime
from pathlib import Path


class DiscoveryType(Enum):
    """Types of potential discoveries"""
    NEW_THEOREM = "new_theorem"
    NEW_FORMULA = "new_formula"
    NEW_PROOF = "new_proof"
    NEW_METHOD = "new_method"
    NEW_CONJECTURE = "new_conjecture"
    NEW_CONNECTION = "new_connection"
    NEW_PROBLEM = "new_problem"
    NEW_INSIGHT = "new_insight"


class DiscoveryStatus(Enum):
    """Status of a discovery"""
    DETECTED = "detected"           # Just detected, not reviewed
    PENDING_REVIEW = "pending"      # Awaiting Manus review
    UNDER_VERIFICATION = "verifying"  # Being verified against sources
    VERIFIED_NEW = "verified_new"   # Confirmed as new
    VERIFIED_KNOWN = "verified_known"  # Found to already exist
    REJECTED = "rejected"           # Not a valid discovery
    PROTECTED = "protected"         # Verified and protected from replication


@dataclass
class Discovery:
    """A potential mathematical discovery"""
    id: str
    timestamp: str
    discoverer: str  # Which AI framework discovered it
    discovery_type: DiscoveryType
    title: str
    description: str
    mathematical_content: str
    context: Dict[str, Any]  # Question, level, topic that led to discovery
    score_at_discovery: int
    status: DiscoveryStatus
    verification_results: Optional[Dict[str, Any]] = None
    hash: str = ""  # Hash to prevent replication
    related_discoveries: List[str] = field(default_factory=list)
    review_notes: List[Dict[str, Any]] = field(default_factory=list)
    

class DiscoveryDetector:
    """
    Detects and manages potential mathematical discoveries.
    Ensures no replication and proper attribution.
    """
    
    # Keywords that indicate potential discoveries
    DISCOVERY_KEYWORDS = {
        DiscoveryType.NEW_THEOREM: [
            "theorem", "prove that", "i can show", "it follows that",
            "we can prove", "new result", "i've proven"
        ],
        DiscoveryType.NEW_FORMULA: [
            "formula", "equation", "i derived", "new expression",
            "relationship", "identity", "equals"
        ],
        DiscoveryType.NEW_PROOF: [
            "alternative proof", "new proof", "simpler proof",
            "elegant proof", "direct proof", "i've found a way to prove"
        ],
        DiscoveryType.NEW_METHOD: [
            "new method", "new approach", "new technique", "algorithm",
            "procedure", "i discovered a way"
        ],
        DiscoveryType.NEW_CONJECTURE: [
            "conjecture", "hypothesis", "i believe", "it seems that",
            "pattern suggests", "i suspect"
        ],
        DiscoveryType.NEW_CONNECTION: [
            "connection between", "relates to", "similar to",
            "analogy", "correspondence", "isomorphism"
        ],
        DiscoveryType.NEW_PROBLEM: [
            "open problem", "unsolved", "new question",
            "what if", "consider the case", "generalization"
        ],
        DiscoveryType.NEW_INSIGHT: [
            "insight", "observation", "notice that", "interesting",
            "key idea", "fundamental"
        ]
    }
    
    def __init__(self, storage_dir: str = "/home/ubuntu/aether/discoveries"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.discoveries: Dict[str, Discovery] = {}
        self.discovery_hashes: Set[str] = set()  # For replication prevention
        self.pending_review: List[str] = []
        
        self._load_existing_discoveries()
        
    def _load_existing_discoveries(self):
        """Load existing discoveries from storage"""
        discovery_file = self.storage_dir / "all_discoveries.jsonl"
        if discovery_file.exists():
            with open(discovery_file, "r") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        discovery = self._dict_to_discovery(data)
                        self.discoveries[discovery.id] = discovery
                        self.discovery_hashes.add(discovery.hash)
                        if discovery.status == DiscoveryStatus.PENDING_REVIEW:
                            self.pending_review.append(discovery.id)
                            
    def _dict_to_discovery(self, data: Dict) -> Discovery:
        """Convert dictionary to Discovery object"""
        return Discovery(
            id=data["id"],
            timestamp=data["timestamp"],
            discoverer=data["discoverer"],
            discovery_type=DiscoveryType(data["discovery_type"]),
            title=data["title"],
            description=data["description"],
            mathematical_content=data["mathematical_content"],
            context=data["context"],
            score_at_discovery=data["score_at_discovery"],
            status=DiscoveryStatus(data["status"]),
            verification_results=data.get("verification_results"),
            hash=data["hash"],
            related_discoveries=data.get("related_discoveries", []),
            review_notes=data.get("review_notes", [])
        )
    
    def _discovery_to_dict(self, discovery: Discovery) -> Dict:
        """Convert Discovery object to dictionary"""
        return {
            "id": discovery.id,
            "timestamp": discovery.timestamp,
            "discoverer": discovery.discoverer,
            "discovery_type": discovery.discovery_type.value,
            "title": discovery.title,
            "description": discovery.description,
            "mathematical_content": discovery.mathematical_content,
            "context": discovery.context,
            "score_at_discovery": discovery.score_at_discovery,
            "status": discovery.status.value,
            "verification_results": discovery.verification_results,
            "hash": discovery.hash,
            "related_discoveries": discovery.related_discoveries,
            "review_notes": discovery.review_notes
        }
    
    def detect_discovery(self, 
                         student: str,
                         answer: str,
                         question: str,
                         level: str,
                         topic: str,
                         score: int) -> Optional[Discovery]:
        """
        Analyze an answer for potential mathematical discoveries.
        Returns a Discovery object if found, None otherwise.
        """
        # Check score threshold (35-100% can have discoveries)
        if score < 35:
            return None
            
        # Detect discovery type
        discovery_type = self._detect_discovery_type(answer)
        if not discovery_type:
            return None
            
        # Extract mathematical content
        math_content = self._extract_mathematical_content(answer)
        if not math_content:
            return None
            
        # Generate hash to check for replication
        content_hash = self._generate_hash(math_content)
        
        # Check if this is a replication
        if content_hash in self.discovery_hashes:
            # This is a replication - do not allow
            return self._handle_replication(content_hash, student)
            
        # Create new discovery
        discovery_id = f"DISC_{student}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.discoveries)}"
        
        discovery = Discovery(
            id=discovery_id,
            timestamp=datetime.now().isoformat(),
            discoverer=student,
            discovery_type=discovery_type,
            title=self._generate_title(discovery_type, topic),
            description=self._generate_description(answer, discovery_type),
            mathematical_content=math_content,
            context={
                "question": question,
                "level": level,
                "topic": topic,
                "full_answer": answer
            },
            score_at_discovery=score,
            status=DiscoveryStatus.PENDING_REVIEW,
            hash=content_hash
        )
        
        # Store discovery
        self.discoveries[discovery_id] = discovery
        self.discovery_hashes.add(content_hash)
        self.pending_review.append(discovery_id)
        
        # Save to file
        self._save_discovery(discovery)
        
        # Flag for Manus review
        self._flag_for_manus_review(discovery)
        
        return discovery
    
    def _detect_discovery_type(self, answer: str) -> Optional[DiscoveryType]:
        """Detect the type of potential discovery"""
        answer_lower = answer.lower()
        
        # Score each type based on keyword matches
        type_scores = {}
        for dtype, keywords in self.DISCOVERY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in answer_lower)
            if score > 0:
                type_scores[dtype] = score
                
        if not type_scores:
            return None
            
        # Return the type with highest score
        return max(type_scores, key=type_scores.get)
    
    def _extract_mathematical_content(self, answer: str) -> Optional[str]:
        """Extract the core mathematical content from an answer"""
        # Look for mathematical expressions, formulas, proofs
        lines = answer.split('\n')
        math_lines = []
        
        for line in lines:
            # Check for mathematical content indicators
            if any(c in line for c in ['=', '+', '-', '*', '/', '^', '∫', '∑', '∏', '∂', '∀', '∃']):
                math_lines.append(line.strip())
            elif any(w in line.lower() for w in ['therefore', 'thus', 'hence', 'proof', 'qed']):
                math_lines.append(line.strip())
            elif any(w in line.lower() for w in ['theorem', 'lemma', 'corollary', 'proposition']):
                math_lines.append(line.strip())
                
        if math_lines:
            return '\n'.join(math_lines)
            
        # If no explicit math, return a summary
        if len(answer) > 100:
            return answer[:500]  # First 500 chars as summary
            
        return None
    
    def _generate_hash(self, content: str) -> str:
        """Generate a hash of the mathematical content for replication detection"""
        # Normalize content before hashing
        normalized = content.lower().replace(' ', '').replace('\n', '')
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def _handle_replication(self, content_hash: str, student: str) -> None:
        """Handle attempted replication of existing discovery"""
        # Find the original discovery
        original = None
        for disc in self.discoveries.values():
            if disc.hash == content_hash:
                original = disc
                break
                
        if original:
            # Log the replication attempt
            replication_log = {
                "timestamp": datetime.now().isoformat(),
                "attempted_by": student,
                "original_discovery": original.id,
                "original_discoverer": original.discoverer,
                "status": "BLOCKED"
            }
            
            log_file = self.storage_dir / "replication_attempts.jsonl"
            with open(log_file, "a") as f:
                f.write(json.dumps(replication_log) + "\n")
                
        return None  # Do not create a new discovery
    
    def _generate_title(self, dtype: DiscoveryType, topic: str) -> str:
        """Generate a title for the discovery"""
        type_names = {
            DiscoveryType.NEW_THEOREM: "Potential Theorem",
            DiscoveryType.NEW_FORMULA: "Potential Formula",
            DiscoveryType.NEW_PROOF: "Alternative Proof",
            DiscoveryType.NEW_METHOD: "New Method",
            DiscoveryType.NEW_CONJECTURE: "Conjecture",
            DiscoveryType.NEW_CONNECTION: "Mathematical Connection",
            DiscoveryType.NEW_PROBLEM: "Open Problem",
            DiscoveryType.NEW_INSIGHT: "Mathematical Insight"
        }
        return f"{type_names.get(dtype, 'Discovery')} in {topic.replace('_', ' ').title()}"
    
    def _generate_description(self, answer: str, dtype: DiscoveryType) -> str:
        """Generate a description of the discovery"""
        # Extract key sentences
        sentences = answer.replace('\n', ' ').split('.')
        key_sentences = []
        
        keywords = self.DISCOVERY_KEYWORDS.get(dtype, [])
        for sentence in sentences:
            if any(kw in sentence.lower() for kw in keywords):
                key_sentences.append(sentence.strip())
                
        if key_sentences:
            return '. '.join(key_sentences[:3]) + '.'
        return answer[:200] + "..."
    
    def _save_discovery(self, discovery: Discovery):
        """Save discovery to storage"""
        # Save to main file
        main_file = self.storage_dir / "all_discoveries.jsonl"
        with open(main_file, "a") as f:
            f.write(json.dumps(self._discovery_to_dict(discovery)) + "\n")
            
        # Save to type-specific file
        type_file = self.storage_dir / f"{discovery.discovery_type.value}.jsonl"
        with open(type_file, "a") as f:
            f.write(json.dumps(self._discovery_to_dict(discovery)) + "\n")
            
        # Save to pending review
        pending_file = self.storage_dir / "pending_review.jsonl"
        with open(pending_file, "a") as f:
            f.write(json.dumps({
                "id": discovery.id,
                "timestamp": discovery.timestamp,
                "discoverer": discovery.discoverer,
                "type": discovery.discovery_type.value,
                "title": discovery.title,
                "score": discovery.score_at_discovery,
                "status": "PENDING_MANUS_REVIEW"
            }) + "\n")
    
    def _flag_for_manus_review(self, discovery: Discovery):
        """Create a flag for Manus to review this discovery"""
        flag = {
            "discovery_id": discovery.id,
            "flagged_at": datetime.now().isoformat(),
            "discoverer": discovery.discoverer,
            "type": discovery.discovery_type.value,
            "title": discovery.title,
            "description": discovery.description,
            "mathematical_content": discovery.mathematical_content,
            "score": discovery.score_at_discovery,
            "context_level": discovery.context.get("level"),
            "context_topic": discovery.context.get("topic"),
            "priority": self._calculate_priority(discovery),
            "action_required": [
                "Verify against official sources (Wikipedia, phys.org, research papers)",
                "Check if this is genuinely new or already known",
                "If new, protect from replication",
                "Document verification process"
            ],
            "status": "AWAITING_MANUS_REVIEW"
        }
        
        flag_file = self.storage_dir / "manus_review_flags.jsonl"
        with open(flag_file, "a") as f:
            f.write(json.dumps(flag) + "\n")
            
    def _calculate_priority(self, discovery: Discovery) -> str:
        """Calculate review priority"""
        # Higher score + theorem/formula = higher priority
        score = discovery.score_at_discovery
        
        high_priority_types = [
            DiscoveryType.NEW_THEOREM,
            DiscoveryType.NEW_FORMULA,
            DiscoveryType.NEW_PROOF
        ]
        
        if discovery.discovery_type in high_priority_types and score >= 75:
            return "HIGH"
        elif score >= 90:
            return "HIGH"
        elif score >= 75:
            return "MEDIUM"
        else:
            return "NORMAL"
    
    def get_pending_reviews(self) -> List[Discovery]:
        """Get all discoveries pending Manus review"""
        return [
            self.discoveries[did] 
            for did in self.pending_review 
            if did in self.discoveries
        ]
    
    def manus_review(self, 
                     discovery_id: str,
                     is_new: bool,
                     verification_sources: List[str],
                     verification_notes: str,
                     action: str) -> Dict:
        """
        Manus reviews a discovery.
        
        Args:
            discovery_id: ID of discovery to review
            is_new: Whether this is genuinely new
            verification_sources: Sources checked (Wikipedia, papers, etc.)
            verification_notes: Notes from verification
            action: Action taken (verify_new, verify_known, reject)
        """
        if discovery_id not in self.discoveries:
            return {"error": "Discovery not found"}
            
        discovery = self.discoveries[discovery_id]
        
        # Update status based on review
        if action == "verify_new":
            discovery.status = DiscoveryStatus.VERIFIED_NEW
        elif action == "verify_known":
            discovery.status = DiscoveryStatus.VERIFIED_KNOWN
        elif action == "reject":
            discovery.status = DiscoveryStatus.REJECTED
        elif action == "protect":
            discovery.status = DiscoveryStatus.PROTECTED
            
        # Add verification results
        discovery.verification_results = {
            "reviewed_at": datetime.now().isoformat(),
            "reviewed_by": "Manus",
            "is_new": is_new,
            "sources_checked": verification_sources,
            "notes": verification_notes,
            "action": action
        }
        
        # Add review note
        discovery.review_notes.append({
            "timestamp": datetime.now().isoformat(),
            "reviewer": "Manus",
            "note": verification_notes
        })
        
        # Remove from pending
        if discovery_id in self.pending_review:
            self.pending_review.remove(discovery_id)
            
        # Save updated discovery
        self._update_discovery_file(discovery)
        
        # Log the review
        review_log = {
            "discovery_id": discovery_id,
            "reviewed_at": datetime.now().isoformat(),
            "is_new": is_new,
            "action": action,
            "sources": verification_sources,
            "notes": verification_notes
        }
        
        log_file = self.storage_dir / "review_log.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(review_log) + "\n")
            
        return {
            "discovery_id": discovery_id,
            "new_status": discovery.status.value,
            "is_new": is_new,
            "message": f"Discovery reviewed and marked as {discovery.status.value}"
        }
    
    def _update_discovery_file(self, discovery: Discovery):
        """Update the discovery in the main file"""
        # For simplicity, append the updated version
        # In production, would update in place
        update_file = self.storage_dir / "discovery_updates.jsonl"
        with open(update_file, "a") as f:
            f.write(json.dumps(self._discovery_to_dict(discovery)) + "\n")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get discovery statistics"""
        stats = {
            "total_discoveries": len(self.discoveries),
            "pending_review": len(self.pending_review),
            "by_type": {},
            "by_status": {},
            "by_discoverer": {},
            "verified_new": 0,
            "protected": 0
        }
        
        for disc in self.discoveries.values():
            # By type
            dtype = disc.discovery_type.value
            stats["by_type"][dtype] = stats["by_type"].get(dtype, 0) + 1
            
            # By status
            status = disc.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # By discoverer
            discoverer = disc.discoverer
            stats["by_discoverer"][discoverer] = stats["by_discoverer"].get(discoverer, 0) + 1
            
            # Count verified new and protected
            if disc.status == DiscoveryStatus.VERIFIED_NEW:
                stats["verified_new"] += 1
            elif disc.status == DiscoveryStatus.PROTECTED:
                stats["protected"] += 1
                
        return stats


if __name__ == "__main__":
    # Test the discovery detector
    detector = DiscoveryDetector()
    
    # Test with a potential discovery
    answer = """
    I've been thinking about this problem and I believe I've found a new relationship.
    
    For the sum of squares from 1 to n, we know the formula n(n+1)(2n+1)/6.
    
    But I noticed that if we consider the sum of cubes, there's an interesting connection:
    The sum of cubes equals the square of the sum of integers!
    
    That is: 1³ + 2³ + ... + n³ = (1 + 2 + ... + n)²
    
    This is a beautiful identity that connects two different sums.
    I conjecture this might extend to higher powers in some form.
    """
    
    discovery = detector.detect_discovery(
        student="Stratify",
        answer=answer,
        question="Explore patterns in sums of powers",
        level="9",
        topic="number_theory",
        score=85
    )
    
    if discovery:
        print(f"Discovery detected!")
        print(f"  ID: {discovery.id}")
        print(f"  Type: {discovery.discovery_type.value}")
        print(f"  Title: {discovery.title}")
        print(f"  Status: {discovery.status.value}")
        print(f"  Hash: {discovery.hash}")
    else:
        print("No discovery detected")
        
    print(f"\nStatistics: {detector.get_statistics()}")
