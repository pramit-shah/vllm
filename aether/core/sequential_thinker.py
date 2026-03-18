#!/usr/bin/env python3.11
"""
Sequential Unique Thinking Mode for AETHER Frameworks

Each framework works in its own sequential unique thinking mode:
- Not just parallel execution
- Each has its own chain of thought
- Builds understanding step by step
- Unique perspective and approach
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field

# Try to import OpenAI
try:
    from openai import OpenAI
    client = OpenAI()
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False
    client = None


@dataclass
class ThoughtChain:
    """A chain of thoughts for sequential reasoning."""
    framework: str
    topic: str
    thoughts: List[Dict] = field(default_factory=list)
    conclusions: List[str] = field(default_factory=list)
    new_insights: List[str] = field(default_factory=list)
    potential_formulas: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class SequentialThinker:
    """
    Manages sequential unique thinking for a framework.
    
    Each framework has its own thinker that:
    1. Builds understanding step by step
    2. Maintains a chain of thoughts
    3. Develops unique insights
    4. Identifies potential new formulas/physics
    """
    
    def __init__(self, framework_name: str, specialty: str, model: str = "gpt-4.1-nano"):
        self.framework_name = framework_name
        self.specialty = specialty
        self.model = model
        
        # Thought history
        self.thought_chains: List[ThoughtChain] = []
        self.accumulated_knowledge: List[str] = []
        self.unique_insights: List[str] = []
        self.potential_discoveries: List[Dict] = []
        
        # System prompt for unique thinking
        self.system_prompt = f"""You are {framework_name}, an advanced AI research framework specializing in {specialty}.

You think SEQUENTIALLY and UNIQUELY:
1. Build understanding step by step
2. Each thought builds on the previous
3. Develop your own unique perspective
4. Look for novel connections and insights
5. Identify potential new formulas or physics

Your goal: Advance science and mathematics for humanity by tackling the Yang-Mills Millennium Prize Problem.

When thinking:
- Be rigorous but creative
- Question assumptions
- Look for patterns others might miss
- Build towards breakthrough insights
- Flag any potentially new mathematics or physics

Format your thoughts as a chain:
THOUGHT 1: [initial observation]
THOUGHT 2: [building on thought 1]
THOUGHT 3: [deeper insight]
...
CONCLUSION: [what you've learned]
NEW INSIGHT: [if any novel idea emerged]
POTENTIAL FORMULA: [if any new mathematical relationship discovered]
"""
    
    def study_sequentially(self, material: Dict) -> ThoughtChain:
        """Study material with sequential thinking."""
        
        chain = ThoughtChain(
            framework=self.framework_name,
            topic=material.get('title', 'Unknown')
        )
        
        if not AI_AVAILABLE:
            return self._simulated_study(material, chain)
        
        # Build sequential study prompt
        study_prompt = f"""Study this material using sequential thinking. Build your understanding step by step.

MATERIAL: {material.get('title', 'Unknown')}
CONTENT: {json.dumps(material.get('content', {}), indent=2)[:3000]}

YOUR ACCUMULATED KNOWLEDGE SO FAR:
{chr(10).join(self.accumulated_knowledge[-5:]) if self.accumulated_knowledge else 'Starting fresh.'}

Think sequentially:
1. What is the core concept?
2. How does it connect to what you already know?
3. What are the implications for Yang-Mills?
4. What new insights emerge?
5. Any potential new formulas or physics?

Provide your chain of thoughts."""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": study_prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            thinking = response.choices[0].message.content
            
            # Parse the thinking into structured thoughts
            chain = self._parse_thinking(thinking, chain)
            
            # Add to accumulated knowledge
            if chain.conclusions:
                self.accumulated_knowledge.extend(chain.conclusions)
            if chain.new_insights:
                self.unique_insights.extend(chain.new_insights)
            if chain.potential_formulas:
                for formula in chain.potential_formulas:
                    self.potential_discoveries.append({
                        "type": "formula",
                        "content": formula,
                        "context": material.get('title', ''),
                        "timestamp": datetime.now().isoformat()
                    })
            
            self.thought_chains.append(chain)
            return chain
            
        except Exception as e:
            chain.thoughts.append({"error": str(e)})
            return chain
    
    def attempt_sequentially(self, question: Dict) -> Dict:
        """Attempt a question with sequential thinking."""
        
        if not AI_AVAILABLE:
            return self._simulated_attempt(question)
        
        # Build sequential attempt prompt
        attempt_prompt = f"""Solve this problem using sequential thinking. Show your chain of reasoning.

QUESTION: {question.get('question', '')}
DIFFICULTY: {question.get('difficulty', 'Unknown')}
REQUIRED CONCEPTS: {question.get('requires_concepts', [])}
HINTS: {question.get('hints', [])}

YOUR ACCUMULATED KNOWLEDGE:
{chr(10).join(self.accumulated_knowledge[-10:]) if self.accumulated_knowledge else 'Use your training.'}

YOUR UNIQUE INSIGHTS SO FAR:
{chr(10).join(self.unique_insights[-5:]) if self.unique_insights else 'None yet.'}

Think sequentially:
THOUGHT 1: What is being asked?
THOUGHT 2: What concepts apply?
THOUGHT 3: How do I approach this?
THOUGHT 4: Working through the solution...
THOUGHT 5: Checking my reasoning...
CONCLUSION: Final answer
NEW INSIGHT: Any novel observation?
POTENTIAL FORMULA: Any new mathematical relationship?

Provide your complete sequential reasoning and answer."""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": attempt_prompt}
                ],
                max_tokens=2500,
                temperature=0.5
            )
            
            thinking = response.choices[0].message.content
            
            # Check for new discoveries
            is_new_formula = "POTENTIAL FORMULA:" in thinking and "None" not in thinking.split("POTENTIAL FORMULA:")[-1][:50]
            is_new_physics = "new physics" in thinking.lower() or "novel physical" in thinking.lower()
            
            # Extract potential formula if present
            formula_details = None
            if is_new_formula:
                try:
                    formula_section = thinking.split("POTENTIAL FORMULA:")[-1].split("\n")[0].strip()
                    if formula_section and formula_section.lower() not in ['none', 'n/a', '']:
                        formula_details = formula_section
                        self.potential_discoveries.append({
                            "type": "formula",
                            "content": formula_details,
                            "question": question.get('question_id', ''),
                            "timestamp": datetime.now().isoformat()
                        })
                except:
                    pass
            
            return {
                "framework": self.framework_name,
                "question_id": question.get('question_id', ''),
                "answer": thinking,
                "is_new_formula": is_new_formula,
                "formula_details": formula_details,
                "is_new_physics": is_new_physics,
                "thought_count": thinking.count("THOUGHT")
            }
            
        except Exception as e:
            return {
                "framework": self.framework_name,
                "question_id": question.get('question_id', ''),
                "answer": f"Error: {e}",
                "is_new_formula": False,
                "is_new_physics": False
            }
    
    def _parse_thinking(self, thinking: str, chain: ThoughtChain) -> ThoughtChain:
        """Parse thinking text into structured chain."""
        lines = thinking.split('\n')
        
        current_thought = None
        for line in lines:
            line = line.strip()
            if line.startswith('THOUGHT'):
                if current_thought:
                    chain.thoughts.append(current_thought)
                current_thought = {"type": "thought", "content": line}
            elif line.startswith('CONCLUSION:'):
                chain.conclusions.append(line.replace('CONCLUSION:', '').strip())
            elif line.startswith('NEW INSIGHT:'):
                insight = line.replace('NEW INSIGHT:', '').strip()
                if insight.lower() not in ['none', 'n/a', '']:
                    chain.new_insights.append(insight)
            elif line.startswith('POTENTIAL FORMULA:'):
                formula = line.replace('POTENTIAL FORMULA:', '').strip()
                if formula.lower() not in ['none', 'n/a', '']:
                    chain.potential_formulas.append(formula)
            elif current_thought:
                current_thought['content'] += ' ' + line
        
        if current_thought:
            chain.thoughts.append(current_thought)
        
        return chain
    
    def _simulated_study(self, material: Dict, chain: ThoughtChain) -> ThoughtChain:
        """Simulated study for when API not available."""
        chain.thoughts = [
            {"type": "thought", "content": f"THOUGHT 1: Examining {material.get('title', 'material')}"},
            {"type": "thought", "content": "THOUGHT 2: Connecting to gauge theory foundations"},
            {"type": "thought", "content": "THOUGHT 3: Identifying relevance to Yang-Mills"}
        ]
        chain.conclusions = [f"Understood core concepts of {material.get('title', 'material')}"]
        return chain
    
    def _simulated_attempt(self, question: Dict) -> Dict:
        """Simulated attempt for when API not available."""
        return {
            "framework": self.framework_name,
            "question_id": question.get('question_id', ''),
            "answer": f"[Simulated sequential thinking for {question.get('question_id', '')}]",
            "is_new_formula": False,
            "is_new_physics": False,
            "thought_count": 5
        }
    
    def get_knowledge_summary(self) -> str:
        """Get summary of accumulated knowledge."""
        return f"""
=== {self.framework_name} Knowledge Summary ===
Accumulated insights: {len(self.accumulated_knowledge)}
Unique insights: {len(self.unique_insights)}
Potential discoveries: {len(self.potential_discoveries)}
Thought chains completed: {len(self.thought_chains)}

Recent conclusions:
{chr(10).join(f'- {c}' for c in self.accumulated_knowledge[-5:])}

Unique insights:
{chr(10).join(f'- {i}' for i in self.unique_insights[-3:])}
"""
    
    def get_discoveries(self) -> List[Dict]:
        """Get all potential discoveries."""
        return self.potential_discoveries


class SequentialThinkingManager:
    """
    Manages sequential thinking for multiple frameworks.
    
    Each framework has its own thinker with unique perspective.
    """
    
    def __init__(self):
        self.thinkers: Dict[str, SequentialThinker] = {}
        self.all_discoveries: List[Dict] = []
    
    def create_thinker(self, framework_name: str, specialty: str) -> SequentialThinker:
        """Create a sequential thinker for a framework."""
        thinker = SequentialThinker(framework_name, specialty)
        self.thinkers[framework_name] = thinker
        return thinker
    
    def get_thinker(self, framework_name: str) -> Optional[SequentialThinker]:
        """Get a framework's thinker."""
        return self.thinkers.get(framework_name)
    
    def collect_discoveries(self) -> List[Dict]:
        """Collect all discoveries from all thinkers."""
        discoveries = []
        for name, thinker in self.thinkers.items():
            for d in thinker.get_discoveries():
                d['framework'] = name
                discoveries.append(d)
        self.all_discoveries = discoveries
        return discoveries
    
    def get_combined_insights(self) -> Dict:
        """Get combined insights from all frameworks."""
        all_insights = []
        all_conclusions = []
        
        for name, thinker in self.thinkers.items():
            all_insights.extend([(name, i) for i in thinker.unique_insights])
            all_conclusions.extend([(name, c) for c in thinker.accumulated_knowledge])
        
        return {
            "total_insights": len(all_insights),
            "total_conclusions": len(all_conclusions),
            "insights_by_framework": {
                name: len(t.unique_insights) for name, t in self.thinkers.items()
            },
            "recent_insights": all_insights[-10:],
            "potential_discoveries": self.collect_discoveries()
        }


# Singleton manager
_thinking_manager = None

def get_thinking_manager() -> SequentialThinkingManager:
    """Get the singleton thinking manager."""
    global _thinking_manager
    if _thinking_manager is None:
        _thinking_manager = SequentialThinkingManager()
    return _thinking_manager
