#!/usr/bin/env python3
"""
AETHER Data Integrity System
Detects and repairs data corruption in progress files
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, List, Tuple

class DataIntegrityChecker:
    """Checks and repairs data corruption in AETHER system files."""
    
    def __init__(self, memory_dir: str = "/home/ubuntu/aether/memory"):
        self.memory_dir = memory_dir
        self.backup_dir = os.path.join(memory_dir, "backups")
        self.log_file = os.path.join(memory_dir, "integrity_log.jsonl")
        
        # Ensure directories exist
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Define valid ranges and types for each field
        self.schema = {
            "name": {"type": str, "required": True},
            "role": {"type": str, "required": False},
            "total_questions": {"type": int, "min": 0, "max": 100000, "required": True},
            "total_passed": {"type": int, "min": 0, "max": 100000, "required": True},
            "average_score": {"type": (int, float), "min": 0, "max": 100, "required": True},
            "current_level": {"type": int, "min": 1, "max": 20, "required": True},
            "sessions": {"type": list, "required": True},
            "character_traits": {"type": dict, "required": False},
            "grade_history": {"type": list, "required": False}
        }
        
        # Valid character trait ranges
        self.trait_range = {"min": 0, "max": 100}
    
    def log_event(self, event_type: str, details: Dict[str, Any]):
        """Log integrity events."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")
    
    def backup_file(self, filepath: str) -> str:
        """Create a backup of a file before modification."""
        if not os.path.exists(filepath):
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(filepath)
        backup_path = os.path.join(self.backup_dir, f"{filename}.{timestamp}.bak")
        shutil.copy2(filepath, backup_path)
        return backup_path
    
    def check_file_corruption(self, filepath: str) -> Tuple[bool, List[str]]:
        """Check a file for corruption. Returns (is_valid, list_of_issues)."""
        issues = []
        
        # Check if file exists
        if not os.path.exists(filepath):
            return False, ["File does not exist"]
        
        # Try to load JSON
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"JSON parse error: {e}"]
        except Exception as e:
            return False, [f"File read error: {e}"]
        
        # Validate schema
        for field, rules in self.schema.items():
            if rules.get("required", False) and field not in data:
                issues.append(f"Missing required field: {field}")
                continue
            
            if field in data:
                value = data[field]
                expected_type = rules["type"]
                
                # Type check
                if not isinstance(value, expected_type):
                    issues.append(f"Invalid type for {field}: expected {expected_type}, got {type(value)}")
                    continue
                
                # Range check for numbers
                if isinstance(value, (int, float)):
                    if "min" in rules and value < rules["min"]:
                        issues.append(f"Value too low for {field}: {value} < {rules['min']}")
                    if "max" in rules and value > rules["max"]:
                        issues.append(f"Value too high for {field}: {value} > {rules['max']}")
        
        # Validate character traits if present
        if "character_traits" in data and isinstance(data["character_traits"], dict):
            for trait, value in data["character_traits"].items():
                if not isinstance(value, (int, float)):
                    issues.append(f"Invalid trait type for {trait}: {type(value)}")
                elif value < self.trait_range["min"] or value > self.trait_range["max"]:
                    issues.append(f"Trait out of range: {trait}={value}")
        
        # Cross-validation checks
        if "total_questions" in data and "total_passed" in data:
            if data["total_passed"] > data["total_questions"]:
                issues.append(f"total_passed ({data['total_passed']}) > total_questions ({data['total_questions']})")
        
        if "average_score" in data and "total_questions" in data:
            # Check for obviously wrong averages
            if data["total_questions"] > 10 and data["average_score"] < 5:
                issues.append(f"Suspiciously low average_score: {data['average_score']}% with {data['total_questions']} questions")
        
        return len(issues) == 0, issues
    
    def repair_file(self, filepath: str, issues: List[str]) -> Dict[str, Any]:
        """Attempt to repair a corrupted file."""
        repairs_made = []
        
        # Backup first
        backup_path = self.backup_file(filepath)
        if backup_path:
            repairs_made.append(f"Backup created: {backup_path}")
        
        # Try to load existing data
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except:
            # If can't load, start fresh
            data = {}
            repairs_made.append("Started with empty data due to parse error")
        
        # Get student name from filename
        filename = os.path.basename(filepath)
        student_name = filename.replace("_full_record.json", "").capitalize()
        
        # Apply repairs based on issues
        for issue in issues:
            if "Missing required field" in issue:
                field = issue.split(": ")[1]
                default_values = {
                    "name": student_name,
                    "total_questions": 0,
                    "total_passed": 0,
                    "average_score": 50.0,
                    "current_level": 1,
                    "sessions": []
                }
                if field in default_values:
                    data[field] = default_values[field]
                    repairs_made.append(f"Added missing field {field} with default value")
            
            elif "Invalid type" in issue:
                field = issue.split(" for ")[1].split(":")[0]
                if field == "current_level":
                    try:
                        data[field] = int(data[field])
                    except:
                        data[field] = 1
                    repairs_made.append(f"Fixed type for {field}")
                elif field == "average_score":
                    try:
                        data[field] = float(data[field])
                    except:
                        data[field] = 50.0
                    repairs_made.append(f"Fixed type for {field}")
            
            elif "Suspiciously low average_score" in issue:
                # Recalculate from sessions if possible
                if "sessions" in data and data["sessions"]:
                    scores = [s.get("average_score", 50) for s in data["sessions"] if "average_score" in s]
                    if scores:
                        data["average_score"] = sum(scores) / len(scores)
                        repairs_made.append(f"Recalculated average_score from sessions: {data['average_score']:.1f}%")
                else:
                    # Default to reasonable value
                    data["average_score"] = 75.0
                    repairs_made.append("Reset average_score to default 75.0%")
            
            elif "total_passed" in issue and "total_questions" in issue:
                # Fix passed count
                data["total_passed"] = min(data["total_passed"], data["total_questions"])
                repairs_made.append("Fixed total_passed to not exceed total_questions")
            
            elif "Value too" in issue:
                field = issue.split(" for ")[1].split(":")[0]
                if "too low" in issue:
                    data[field] = self.schema[field].get("min", 0)
                else:
                    data[field] = self.schema[field].get("max", 100)
                repairs_made.append(f"Clamped {field} to valid range")
            
            elif "Trait out of range" in issue:
                trait = issue.split(": ")[1].split("=")[0]
                if "character_traits" in data:
                    data["character_traits"][trait] = max(0, min(100, data["character_traits"].get(trait, 50)))
                    repairs_made.append(f"Clamped trait {trait} to valid range")
        
        # Ensure grade matches proficiency
        if "average_score" in data and "current_level" in data:
            avg = data["average_score"]
            expected_level = self._calculate_grade_from_score(avg)
            if data["current_level"] > expected_level + 2:  # Allow some buffer
                data["current_level"] = expected_level
                repairs_made.append(f"Adjusted current_level to match proficiency: {expected_level}")
        
        # Save repaired data
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Log the repair
        self.log_event("repair", {
            "file": filepath,
            "issues_found": issues,
            "repairs_made": repairs_made
        })
        
        return {
            "file": filepath,
            "issues_found": len(issues),
            "repairs_made": repairs_made,
            "data": data
        }
    
    def _calculate_grade_from_score(self, avg_score: float) -> int:
        """Calculate appropriate grade level from average score."""
        if avg_score >= 95:
            return 12  # Can be at highest level
        elif avg_score >= 90:
            return 10
        elif avg_score >= 85:
            return 8
        elif avg_score >= 80:
            return 6
        elif avg_score >= 75:
            return 4
        elif avg_score >= 70:
            return 3
        elif avg_score >= 65:
            return 2
        else:
            return 1
    
    def check_all_files(self) -> Dict[str, Any]:
        """Check all progress files for corruption."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "files_checked": 0,
            "files_valid": 0,
            "files_corrupted": 0,
            "files_repaired": 0,
            "details": []
        }
        
        # Find all progress files
        for filename in os.listdir(self.memory_dir):
            if filename.endswith("_full_record.json"):
                filepath = os.path.join(self.memory_dir, filename)
                results["files_checked"] += 1
                
                is_valid, issues = self.check_file_corruption(filepath)
                
                if is_valid:
                    results["files_valid"] += 1
                    results["details"].append({
                        "file": filename,
                        "status": "valid"
                    })
                else:
                    results["files_corrupted"] += 1
                    
                    # Attempt repair
                    repair_result = self.repair_file(filepath, issues)
                    results["files_repaired"] += 1
                    
                    results["details"].append({
                        "file": filename,
                        "status": "repaired",
                        "issues": issues,
                        "repairs": repair_result["repairs_made"]
                    })
        
        # Log the check
        self.log_event("integrity_check", results)
        
        return results
    
    def validate_before_save(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate data before saving. Returns (is_valid, cleaned_data)."""
        cleaned = data.copy()
        
        # Ensure required fields
        if "name" not in cleaned:
            cleaned["name"] = "Unknown"
        
        if "total_questions" not in cleaned:
            cleaned["total_questions"] = 0
        else:
            cleaned["total_questions"] = max(0, int(cleaned["total_questions"]))
        
        if "total_passed" not in cleaned:
            cleaned["total_passed"] = 0
        else:
            cleaned["total_passed"] = max(0, min(int(cleaned["total_passed"]), cleaned["total_questions"]))
        
        if "average_score" not in cleaned:
            cleaned["average_score"] = 50.0
        else:
            cleaned["average_score"] = max(0.0, min(100.0, float(cleaned["average_score"])))
        
        if "current_level" not in cleaned:
            cleaned["current_level"] = 1
        else:
            cleaned["current_level"] = max(1, min(20, int(cleaned["current_level"])))
        
        if "sessions" not in cleaned:
            cleaned["sessions"] = []
        
        # Validate character traits
        if "character_traits" in cleaned:
            for trait in cleaned["character_traits"]:
                cleaned["character_traits"][trait] = max(0, min(100, float(cleaned["character_traits"][trait])))
        
        return True, cleaned


def run_integrity_check():
    """Run a full integrity check on all AETHER data files."""
    checker = DataIntegrityChecker()
    results = checker.check_all_files()
    
    print("\n" + "="*60)
    print("🔍 AETHER DATA INTEGRITY CHECK")
    print("="*60)
    print(f"\nTimestamp: {results['timestamp']}")
    print(f"Files Checked: {results['files_checked']}")
    print(f"Files Valid: {results['files_valid']}")
    print(f"Files Corrupted: {results['files_corrupted']}")
    print(f"Files Repaired: {results['files_repaired']}")
    
    print("\n--- Details ---")
    for detail in results["details"]:
        status_icon = "✅" if detail["status"] == "valid" else "🔧"
        print(f"\n{status_icon} {detail['file']}: {detail['status']}")
        if "issues" in detail:
            for issue in detail["issues"]:
                print(f"   ⚠️  {issue}")
        if "repairs" in detail:
            for repair in detail["repairs"]:
                print(f"   ✓  {repair}")
    
    return results


if __name__ == "__main__":
    run_integrity_check()
