#!/usr/bin/env python3.11
"""
AETHER Fun Breaks Module

Break times with math games, puzzles, and fun activities
to reduce stress and make learning enjoyable.
"""

import random
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class FunActivity:
    """A fun break activity."""
    name: str
    type: str  # puzzle, game, riddle, trivia
    content: str
    answer: str
    hint: str
    difficulty: int  # 1-3


class MathGames:
    """Collection of fun math games and puzzles."""
    
    def __init__(self):
        self.puzzles = self._create_puzzles()
        self.riddles = self._create_riddles()
        self.trivia = self._create_trivia()
        self.patterns = self._create_patterns()
    
    def _create_puzzles(self) -> List[FunActivity]:
        """Create fun math puzzles."""
        return [
            FunActivity(
                name="Magic Square Mini",
                type="puzzle",
                content="Fill in the missing number so each row, column adds to 15:\n  2 | 7 | ?\n  9 | 5 | 1\n  4 | 3 | 8",
                answer="6",
                hint="What number makes 2 + 7 + ? = 15?",
                difficulty=1
            ),
            FunActivity(
                name="Number Detective",
                type="puzzle",
                content="I'm thinking of a number. Double it, add 10, divide by 2, subtract the original. What do you get?",
                answer="5 (always!)",
                hint="Try it with any number...",
                difficulty=1
            ),
            FunActivity(
                name="Quick Math",
                type="puzzle",
                content="Without calculating each: Which is bigger, 99×101 or 100×100?",
                answer="100×100 = 10000, 99×101 = 9999. They differ by 1!",
                hint="Think about (a-1)(a+1) = a² - 1",
                difficulty=2
            ),
            FunActivity(
                name="The Missing Dollar",
                type="puzzle",
                content="Three friends pay $10 each for a $30 room. The clerk realizes it's $25, gives $5 to the bellboy. Bellboy keeps $2, returns $1 each. Each paid $9 (=$27) + $2 bellboy = $29. Where's the missing $1?",
                answer="There's no missing dollar! $27 = $25 (room) + $2 (bellboy). The $29 is a red herring.",
                hint="Don't add the $2, subtract it from $27",
                difficulty=2
            ),
            FunActivity(
                name="Handshake Problem",
                type="puzzle",
                content="At a party of 6 people, everyone shakes hands with everyone else exactly once. How many handshakes?",
                answer="15 (each of 6 people shakes 5 hands = 30, but each handshake counted twice, so 30/2 = 15)",
                hint="Think about combinations, not permutations",
                difficulty=2
            ),
        ]
    
    def _create_riddles(self) -> List[FunActivity]:
        """Create math riddles."""
        return [
            FunActivity(
                name="Age Riddle",
                type="riddle",
                content="A father is 4 times as old as his son. In 20 years, he'll be twice as old. How old are they now?",
                answer="Son is 10, Father is 40. In 20 years: Son 30, Father 60 (twice as old!)",
                hint="Set up equations: F = 4S and F + 20 = 2(S + 20)",
                difficulty=2
            ),
            FunActivity(
                name="Clock Riddle",
                type="riddle",
                content="How many times do the hour and minute hands overlap in 12 hours?",
                answer="11 times (not 12! They overlap at 12:00, ~1:05, ~2:11... but skip one)",
                hint="The minute hand 'laps' the hour hand 11 times",
                difficulty=2
            ),
            FunActivity(
                name="Lily Pad Riddle",
                type="riddle",
                content="A lily pad doubles in size every day. It covers the whole pond in 48 days. When was it half-covered?",
                answer="Day 47 (if it doubles to full on day 48, it was half on day 47)",
                hint="Work backwards from day 48",
                difficulty=1
            ),
            FunActivity(
                name="Rope Riddle",
                type="riddle",
                content="You have two ropes. Each burns in exactly 1 hour but not uniformly. How do you measure 45 minutes?",
                answer="Light rope 1 from both ends AND rope 2 from one end. When rope 1 burns out (30 min), light other end of rope 2. When rope 2 burns out = 45 min total.",
                hint="Burning from both ends halves the time",
                difficulty=3
            ),
        ]
    
    def _create_trivia(self) -> List[FunActivity]:
        """Create math trivia."""
        return [
            FunActivity(
                name="Pi Day",
                type="trivia",
                content="Why is March 14th called Pi Day?",
                answer="3/14 represents 3.14, the first digits of π!",
                hint="Look at the date format...",
                difficulty=1
            ),
            FunActivity(
                name="Googol",
                type="trivia",
                content="What is a googol?",
                answer="10^100 (1 followed by 100 zeros). Google was named after it (misspelled)!",
                hint="It's a very big number, and inspired a famous company",
                difficulty=1
            ),
            FunActivity(
                name="Perfect Numbers",
                type="trivia",
                content="Why is 6 called a 'perfect number'?",
                answer="Its divisors (1, 2, 3) sum to itself: 1+2+3=6. Next perfect number is 28!",
                hint="Add up all numbers that divide 6 evenly (except 6)",
                difficulty=2
            ),
            FunActivity(
                name="Euler's Identity",
                type="trivia",
                content="What's special about e^(iπ) + 1 = 0?",
                answer="It connects 5 fundamental constants: e, i, π, 1, and 0 in one beautiful equation!",
                hint="Count the special numbers in the equation",
                difficulty=2
            ),
            FunActivity(
                name="Fibonacci in Nature",
                type="trivia",
                content="Where do Fibonacci numbers (1,1,2,3,5,8,13...) appear in nature?",
                answer="Sunflower spirals, pinecone scales, flower petals, nautilus shells!",
                hint="Look at spirals and petals",
                difficulty=1
            ),
        ]
    
    def _create_patterns(self) -> List[FunActivity]:
        """Create pattern recognition games."""
        return [
            FunActivity(
                name="What Comes Next?",
                type="pattern",
                content="1, 1, 2, 3, 5, 8, 13, ?",
                answer="21 (Fibonacci: each number is sum of previous two)",
                hint="Add the last two numbers",
                difficulty=1
            ),
            FunActivity(
                name="Letter Pattern",
                type="pattern",
                content="O, T, T, F, F, S, S, ?",
                answer="E (One, Two, Three, Four, Five, Six, Seven, Eight)",
                hint="Think about counting...",
                difficulty=2
            ),
            FunActivity(
                name="Number Sequence",
                type="pattern",
                content="2, 6, 12, 20, 30, ?",
                answer="42 (differences are 4, 6, 8, 10, 12... or n(n+1))",
                hint="Look at the differences between consecutive numbers",
                difficulty=2
            ),
            FunActivity(
                name="Visual Pattern",
                type="pattern",
                content="1=1, 11=2, 21=3, 1211=4, 111221=5, ?=6",
                answer="312211 (Look-and-say sequence: describe what you see)",
                hint="Read each number aloud describing the digits",
                difficulty=3
            ),
        ]
    
    def get_random_activity(self, difficulty: int = None) -> FunActivity:
        """Get a random fun activity."""
        all_activities = self.puzzles + self.riddles + self.trivia + self.patterns
        
        if difficulty:
            filtered = [a for a in all_activities if a.difficulty == difficulty]
            if filtered:
                return random.choice(filtered)
        
        return random.choice(all_activities)
    
    def get_activity_by_type(self, activity_type: str) -> FunActivity:
        """Get activity by type."""
        type_map = {
            "puzzle": self.puzzles,
            "riddle": self.riddles,
            "trivia": self.trivia,
            "pattern": self.patterns
        }
        activities = type_map.get(activity_type, self.puzzles)
        return random.choice(activities)


class BreakManager:
    """Manage break times and fun activities."""
    
    def __init__(self):
        self.games = MathGames()
        self.breaks_taken = 0
        self.activities_completed = []
    
    def should_take_break(self, questions_answered: int, last_scores: List[float]) -> bool:
        """Determine if it's time for a break."""
        # Break every 10 questions
        if questions_answered > 0 and questions_answered % 10 == 0:
            return True
        
        # Break if struggling (3 low scores in a row)
        if len(last_scores) >= 3 and all(s < 50 for s in last_scores[-3:]):
            return True
        
        return False
    
    def take_break(self, framework: str, stress_level: str = "normal") -> Dict:
        """Take a fun break!"""
        self.breaks_taken += 1
        
        # Select difficulty based on stress level
        difficulty = {"low": 2, "normal": 1, "high": 1}.get(stress_level, 1)
        
        # Get a fun activity
        activity = self.games.get_random_activity(difficulty)
        
        result = {
            "break_number": self.breaks_taken,
            "framework": framework,
            "activity": {
                "name": activity.name,
                "type": activity.type,
                "content": activity.content,
                "hint": activity.hint,
                "difficulty": activity.difficulty
            },
            "message": self._get_break_message()
        }
        
        self.activities_completed.append({
            "framework": framework,
            "activity": activity.name,
            "type": activity.type
        })
        
        return result
    
    def _get_break_message(self) -> str:
        """Get an encouraging break message."""
        messages = [
            "🎮 Time for a fun break! Let's play a quick game.",
            "☕ Take a breather! Here's something fun.",
            "🧩 Brain refresh time! Try this puzzle.",
            "🌟 You've been working hard! Enjoy this break.",
            "🎯 Quick fun challenge before we continue!",
            "🧠 Let's exercise a different part of the brain!",
            "🎪 Intermission! Here's something entertaining.",
            "💫 Recharge time! Here's a fun activity."
        ]
        return random.choice(messages)
    
    def evaluate_break_activity(self, activity: Dict, response: str) -> Dict:
        """Evaluate response to break activity (always encouraging)."""
        # Breaks are always positive - no pressure!
        return {
            "enjoyed": True,
            "message": random.choice([
                "Great thinking! 🌟",
                "Nice work on that! 🎉",
                "You're a natural! 💪",
                "That was fun, wasn't it? 😊",
                "Well done! Ready to continue? 🚀"
            ]),
            "bonus_confidence": 5  # Small confidence boost from breaks
        }
    
    def get_stats(self) -> Dict:
        """Get break statistics."""
        return {
            "total_breaks": self.breaks_taken,
            "activities_by_type": self._count_by_type(),
            "activities_completed": len(self.activities_completed)
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count activities by type."""
        counts = {}
        for activity in self.activities_completed:
            t = activity["type"]
            counts[t] = counts.get(t, 0) + 1
        return counts


# Quick motivational quotes for momentum
MOTIVATION_QUOTES = [
    "Every expert was once a beginner. Keep going! 🌱",
    "Progress, not perfection. You're doing great! 📈",
    "The only way to learn math is to do math. 💪",
    "Mistakes are proof that you're trying. 🌟",
    "Small steps lead to big achievements. 🚀",
    "Your brain is growing stronger with each problem! 🧠",
    "Curiosity is the engine of achievement. 🔥",
    "You're building something amazing, one concept at a time. 🏗️"
]


def get_motivation() -> str:
    """Get a random motivational quote."""
    return random.choice(MOTIVATION_QUOTES)


# Singleton
_break_manager = None

def get_break_manager() -> BreakManager:
    """Get the singleton break manager."""
    global _break_manager
    if _break_manager is None:
        _break_manager = BreakManager()
    return _break_manager
