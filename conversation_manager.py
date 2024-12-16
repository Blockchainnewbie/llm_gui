import json
import os
from datetime import datetime as dt
from typing import List, Dict
from fpdf import FPDF

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

class ConversationExporter:
    @staticmethod
    def export_to_txt(conversation: Dict, filepath: str):
        """Export conversation to a text file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Conversation with {conversation['provider']} - {conversation['model']}\n")
            f.write(f"Started: {conversation['timestamp']}\n")
            f.write("-" * 80 + "\n\n")
            
            for msg in conversation['messages']:
                timestamp = dt.fromisoformat(msg['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {msg['role'].title()}:\n")
                f.write(f"{msg['content']}\n\n")

    @staticmethod
    def export_to_pdf(conversation: Dict, filepath: str):
        """Export conversation to a PDF file"""
        pdf = FPDF()
        pdf.add_page()
        
        # Set up fonts
        pdf.add_font('DejaVu', '', 'C:\\Windows\\Fonts\\DejaVuSansCondensed.ttf', uni=True)
        pdf.set_font('DejaVu', size=12)
        
        # Header
        pdf.set_font('DejaVu', size=16)
        pdf.cell(0, 10, f"Conversation with {conversation['provider']} - {conversation['model']}", ln=True)
        pdf.set_font('DejaVu', size=12)
        pdf.cell(0, 10, f"Started: {conversation['timestamp']}", ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)
        
        # Messages
        for msg in conversation['messages']:
            timestamp = dt.fromisoformat(msg['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            pdf.set_font('DejaVu', size=10)
            pdf.cell(0, 10, f"[{timestamp}] {msg['role'].title()}:", ln=True)
            
            pdf.set_font('DejaVu', size=12)
            # Split long messages into multiple lines
            text = msg['content']
            lines = text.split('\n')
            for line in lines:
                # Handle long lines by wrapping them
                while len(line) > 0:
                    chunk = line[:80]  # Take first 80 characters
                    line = line[80:]   # Remove them from the line
                    pdf.multi_cell(0, 10, chunk)
            pdf.ln(5)
        
        pdf.output(filepath)

class ConversationManager:
    def __init__(self, save_dir: str = "conversations"):
        self.save_dir = save_dir
        self.current_conversation = None
        self.ensure_save_directory()
        self.exporter = ConversationExporter()

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

    def export_conversation(self, conversation_id: str, format: str = 'txt'):
        """Export a conversation to the specified format"""
        conversation = self.load_conversation(conversation_id)
        
        # Create exports directory if it doesn't exist
        export_dir = os.path.join(self.save_dir, "exports")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        # Generate export filename
        timestamp = dt.fromisoformat(conversation["timestamp"]).strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}"
        
        if format.lower() == 'pdf':
            filepath = os.path.join(export_dir, f"{filename}.pdf")
            self.exporter.export_to_pdf(conversation, filepath)
        else:  # default to txt
            filepath = os.path.join(export_dir, f"{filename}.txt")
            self.exporter.export_to_txt(conversation, filepath)
        
        return filepath
