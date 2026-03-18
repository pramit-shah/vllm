#!/usr/bin/env python3.11
"""
AETHER Communication System
Handles message passing between Manus, frameworks, and the user
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class MessageType(Enum):
    REPORT = "REPORT"
    CHALLENGE = "CHALLENGE"
    QUESTION = "QUESTION"
    GUIDANCE = "GUIDANCE"
    PEER_MESSAGE = "PEER_MESSAGE"
    USER_CHALLENGE = "USER_CHALLENGE"
    MANUS_CHALLENGE = "MANUS_CHALLENGE"
    CREATION = "CREATION"
    EVOLUTION = "EVOLUTION"
    TOOL_REQUEST = "TOOL_REQUEST"
    TOOL_RESPONSE = "TOOL_RESPONSE"

class Message:
    def __init__(self, from_entity: str, to_entity: str, msg_type: MessageType,
                 content: str, requires_response: bool = False, priority: str = "normal"):
        self.from_entity = from_entity
        self.to_entity = to_entity
        self.msg_type = msg_type
        self.content = content
        self.requires_response = requires_response
        self.priority = priority
        self.timestamp = datetime.now().isoformat()
        self.id = f"{self.from_entity}_{int(time.time()*1000)}"
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "from": self.from_entity,
            "to": self.to_entity,
            "type": self.msg_type.value,
            "content": self.content,
            "requires_response": self.requires_response,
            "priority": self.priority,
            "timestamp": self.timestamp
        }
    
    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.from_entity} → {self.to_entity} ({self.msg_type.value}): {self.content}"

class CommunicationHub:
    def __init__(self, log_file: str = "/home/ubuntu/aether/logs/communication.log"):
        self.log_file = log_file
        self.message_queue: List[Message] = []
        self.message_history: List[Message] = []
        self.pending_responses: Dict[str, Message] = {}
    
    def send_message(self, message: Message):
        """Send a message through the hub"""
        self.message_queue.append(message)
        self.message_history.append(message)
        self._log_message(message)
        
        if message.requires_response:
            self.pending_responses[message.id] = message
    
    def get_messages_for(self, entity: str) -> List[Message]:
        """Get all messages addressed to an entity"""
        messages = [msg for msg in self.message_queue if msg.to_entity == entity]
        # Remove from queue
        self.message_queue = [msg for msg in self.message_queue if msg.to_entity != entity]
        return messages
    
    def respond_to(self, original_message_id: str, response_content: str, from_entity: str):
        """Respond to a message that required a response"""
        if original_message_id in self.pending_responses:
            original = self.pending_responses[original_message_id]
            response = Message(
                from_entity=from_entity,
                to_entity=original.from_entity,
                msg_type=MessageType.GUIDANCE if from_entity == "Manus" else MessageType.REPORT,
                content=f"Re: {original.content[:50]}... → {response_content}",
                requires_response=False
            )
            self.send_message(response)
            del self.pending_responses[original_message_id]
    
    def broadcast(self, from_entity: str, content: str, msg_type: MessageType = MessageType.REPORT):
        """Broadcast a message to all entities"""
        message = Message(
            from_entity=from_entity,
            to_entity="ALL",
            msg_type=msg_type,
            content=content,
            requires_response=False
        )
        self.send_message(message)
    
    def _log_message(self, message: Message):
        """Log message to file"""
        with open(self.log_file, "a") as f:
            f.write(str(message) + "\n")
    
    def get_conversation(self, entity1: str, entity2: str) -> List[Message]:
        """Get all messages between two entities"""
        return [msg for msg in self.message_history 
                if (msg.from_entity == entity1 and msg.to_entity == entity2) or
                   (msg.from_entity == entity2 and msg.to_entity == entity1)]
    
    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """Get the most recent messages"""
        return self.message_history[-count:]
    
    def clear_queue(self):
        """Clear the message queue"""
        self.message_queue = []
    
    def save_history(self, filepath: str):
        """Save message history to JSON"""
        with open(filepath, "w") as f:
            json.dump([msg.to_dict() for msg in self.message_history], f, indent=2)
    
    def print_recent(self, count: int = 5):
        """Print recent messages"""
        print("\n" + "="*80)
        print(f"RECENT MESSAGES (last {count}):")
        print("="*80)
        for msg in self.get_recent_messages(count):
            print(msg)
        print("="*80 + "\n")

# Global communication hub
comm_hub = CommunicationHub()
