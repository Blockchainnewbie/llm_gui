import json
import os
from datetime import datetime as dt
from typing import List, Dict

class Conversation:
    def __init__(self, provider: str, model: str):
        self.provider = provider
        self.model = model
        self.messages: List[Dict] = []
        self.timestamp = dt.now()
        self.id = self.timestamp.strftime("%Y%m%d_%H%M%S")

    def add_message(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": dt.now().isoformat()
        })

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "provider": self.provider,
            "model": self.model,
            "timestamp": self.timestamp.isoformat(),
            "messages": self.messages
        }

class ConversationManager:
    def __init__(self, save_dir: str = "conversations"):
        self.save_dir = save_dir
        self.current_conversation = None
        self.ensure_save_directory()

    def ensure_save_directory(self):
        """Create the save directory if it doesn't exist"""
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def start_new_conversation(self, provider: str, model: str) -> Conversation:
        """Start a new conversation and save the previous one if it exists"""
        if self.current_conversation:
            self.save_conversation(self.current_conversation)
        self.current_conversation = Conversation(provider, model)
        return self.current_conversation

    def add_message(self, role: str, content: str):
        """Add a message to the current conversation"""
        if not self.current_conversation:
            raise ValueError("No active conversation. Call start_new_conversation first.")
        self.current_conversation.add_message(role, content)

    def save_conversation(self, conversation: Conversation = None):
        """Save the conversation to a JSON file"""
        if conversation is None:
            conversation = self.current_conversation
        if conversation is None:
            return

        filename = f"conversation_{conversation.id}.json"
        filepath = os.path.join(self.save_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation.to_dict(), f, indent=2, ensure_ascii=False)

    def load_conversation(self, conversation_id: str) -> Dict:
        """Load a conversation from a JSON file"""
        filename = f"conversation_{conversation_id}.json"
        filepath = os.path.join(self.save_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Conversation {conversation_id} not found")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_conversations(self) -> List[Dict]:
        """List all saved conversations"""
        conversations = []
        for filename in os.listdir(self.save_dir):
            if filename.startswith("conversation_") and filename.endswith(".json"):
                filepath = os.path.join(self.save_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    conversations.append(json.load(f))
        return sorted(conversations, key=lambda x: x["timestamp"], reverse=True)
