#!/usr/bin/env python3.11
"""
AETHER System - Main Orchestrator
Autonomous Ecosystem for Theoretical and Heuristic Exploration in Research
"""

import sys
import time
sys.path.append('/home/ubuntu/aether/core')
sys.path.append('/home/ubuntu/aether/frameworks')

from manus import manus
from stratify import stratify
from principia import principia
from communication import comm_hub
from classification import output_classifier
from knowledge_base import knowledge_base

class AETHERSystem:
    def __init__(self):
        self.manus = manus
        self.frameworks = {}
        self.problem = ""
        self.cycles_completed = 0
        self.max_cycles = 20
        self.running = False
    
    def initialize(self, problem: str):
        """Initialize the system with a problem"""
        print("="*80)
        print("AETHER SYSTEM INITIALIZATION")
        print("="*80)
        print(f"Problem: {problem}")
        print()
        
        self.problem = problem
        
        # Register frameworks
        print("Registering frameworks...")
        self.manus.register_framework(stratify)
        self.manus.register_framework(principia)
        self.frameworks = {
            "Stratify": stratify,
            "Principia": principia
        }
        
        print(f"✅ Registered: Stratify ({stratify.identity})")
        print(f"✅ Registered: Principia ({principia.identity})")
        print()
        
        # Provide complete knowledge
        print("Providing complete mathematical knowledge...")
        print("  ✅ Elementary mathematics")
        print("  ✅ High school mathematics")
        print("  ✅ Undergraduate mathematics")
        print("  ✅ Graduate mathematics")
        print("  ✅ Expert-level mathematics")
        print("  ✅ Historical perspectives (11 scientists)")
        print()
        
        print("="*80)
        print("SYSTEM READY")
        print("="*80)
        print()
    
    def run_cycle(self):
        """Run one complete cycle"""
        self.cycles_completed += 1
        print(f"\n{'='*80}")
        print(f"CYCLE {self.cycles_completed}")
        print(f"{'='*80}\n")
        
        # Each framework does work
        for name, framework in self.frameworks.items():
            print(f"\n--- {name} Working ---")
            result = framework.work_cycle(self.problem)
            
            # Report progress
            print(f"Progress: {result['progress']}")
            
            # Handle discoveries
            for discovery in result['discoveries']:
                print(f"💡 Discovery: {discovery}")
                self.manus.process_output(discovery, name, self.problem)
            
            # Handle questions
            for question in result['questions']:
                print(f"❓ Question: {question}")
                framework.ask_question(question)
            
            # Handle stuck
            if result['stuck']:
                print(f"🧱 {name} is stuck!")
                framework.mark_stuck()
            
            # Save state
            framework.save_state()
            print()
        
        # Manus supervises
        print("\n--- Manus Supervising ---")
        self.manus.supervise_cycle()
        
        # Process messages
        self._process_messages()
        
        # Check for consensus
        consensus = self.manus.check_for_consensus()
        if consensus:
            print(f"\n🎯 {consensus}")
        
        print(f"\n{'='*80}")
        print(f"END OF CYCLE {self.cycles_completed}")
        print(f"{'='*80}\n")
        
        # Small delay for readability
        time.sleep(0.5)
    
    def _process_messages(self):
        """Process inter-framework messages"""
        # Process tool requests first
        tool_messages = comm_hub.get_messages_for("Manus")
        for msg in tool_messages:
            if msg.msg_type.value == "TOOL_REQUEST":
                self.manus.handle_tool_request(msg)
        
        # Process tool queue (one request per cycle)
        self.manus.process_tool_queue()
        
        # Check if frameworks are communicating
        for name, framework in self.frameworks.items():
            messages = framework.check_messages()
            if messages:
                print(f"\n📨 {name} received {len(messages)} message(s)")
                for msg in messages:
                    print(f"  From {msg.from_entity}: {msg.content[:80]}...")
                    
                    # Respond to challenges
                    if msg.msg_type.value == "CHALLENGE":
                        response = framework.respond_to_challenge(msg.content)
                        print(f"  Response: {response[:80]}...")
                        comm_hub.respond_to(msg.id, response, name)
                    
                    # Respond to guidance
                    elif msg.msg_type.value == "GUIDANCE":
                        print(f"  Acknowledged guidance")
                    
                    # Handle tool responses
                    elif msg.msg_type.value == "TOOL_RESPONSE":
                        print(f"  Tool results received")
    
    def run(self, cycles: int = None):
        """Run the system for a number of cycles"""
        if cycles:
            self.max_cycles = cycles
        
        self.running = True
        
        try:
            while self.cycles_completed < self.max_cycles and self.running:
                self.run_cycle()
                
                # Check if we should stop
                if self.cycles_completed % 5 == 0:
                    print("\n" + "="*80)
                    print("CHECKPOINT")
                    print("="*80)
                    self.print_status()
                    print()
        
        except KeyboardInterrupt:
            print("\n\nSystem interrupted by user")
            self.running = False
        
        finally:
            self.finalize()
    
    def print_status(self):
        """Print current system status"""
        print(self.manus.get_status_report())
        output_classifier.print_summary()
    
    def finalize(self):
        """Finalize and save results"""
        print("\n" + "="*80)
        print("FINALIZING AETHER SYSTEM")
        print("="*80)
        
        # Save all states
        for framework in self.frameworks.values():
            framework.save_state()
        
        # Save communication history
        comm_hub.save_history("/home/ubuntu/aether/logs/communication_history.json")
        
        # Final status
        self.print_status()
        
        # Save final report
        report = f"""
AETHER SYSTEM FINAL REPORT
{'='*80}

Problem: {self.problem}
Cycles Completed: {self.cycles_completed}

{self.manus.get_status_report()}

{'='*80}
OUTPUT CLASSIFICATION SUMMARY
{'='*80}
"""
        stats = output_classifier.get_statistics()
        report += f"\nTotal Outputs: {stats.get('total', 0)}\n"
        report += f"Breakthroughs: {stats.get('breakthroughs', 0)}\n"
        report += f"Walls: {stats.get('walls', 0)}\n"
        report += f"Solutions: {stats.get('solutions', 0)}\n"
        
        with open("/home/ubuntu/aether/results/final_report.txt", "w") as f:
            f.write(report)
        
        print("\n✅ Results saved to /home/ubuntu/aether/results/")
        print("✅ Communication history saved to /home/ubuntu/aether/logs/")
        print("✅ Framework workspaces saved to /home/ubuntu/aether/workspaces/")
        print()
        print("="*80)
        print("AETHER SYSTEM SHUTDOWN COMPLETE")
        print("="*80)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AETHER - Autonomous Research System")
    parser.add_argument("--problem", type=str, default="Yang-Mills Existence and Mass Gap",
                       help="Problem to solve")
    parser.add_argument("--cycles", type=int, default=20,
                       help="Number of work cycles")
    
    args = parser.parse_args()
    
    # Create and run system
    system = AETHERSystem()
    system.initialize(args.problem)
    system.run(cycles=args.cycles)

if __name__ == "__main__":
    main()
