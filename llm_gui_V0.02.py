# Importiere die benötigten Module für die GUI
# Importiere die Module für die Erstellung der Benutzeroberfläche
import os
import sys
import json
import requests
import winreg
import ctypes
from datetime import datetime
from conversation_manager import ConversationManager

# Importiere die erforderlichen Module für die Erstellung der GUI
try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import scrolledtext
    from tkinter import messagebox
except ModuleNotFoundError as e:
    # Wenn tkinter nicht installiert ist, gebe einen Fehler aus und beende das Programm
    print(f"Fehler: {e}. Bitte stelle sicher, dass alle erforderlichen Module installiert sind.")
    sys.exit(1)

def is_admin():
    """Check if the script is running with admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def set_environment_variable(name, value):
    """Set a permanent environment variable in Windows"""
    try:
        # Open the registry key for environment variables
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS)
        
        # Set the environment variable in the registry
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
        
        # Close the registry key
        winreg.CloseKey(key)
        
        # Update the current process environment
        os.environ[name] = value
        
        # Broadcast WM_SETTINGCHANGE message
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_ABORTIFHUNG = 0x0002
        result = ctypes.c_long()
        ctypes.windll.user32.SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 
            "Environment", SMTO_ABORTIFHUNG, 5000, ctypes.byref(result))
        
        return True
    except Exception as e:
        print(f"Error setting environment variable: {e}")
        return False

# Definiere die Klasse LLMGUI für die Erstellung der GUI
class LLMGUI:
    # Initialisiere die Klasse mit dem Hauptanwendungsfenster
    def __init__(self, root):
        # Initialisiere das Hauptanwendungsfenster
        self.root = root
        root.title("LLM GUI")

        # Initialize conversation manager
        self.conversation_manager = ConversationManager()
        
        # Create menu bar
        self.create_menu()

        # Erstelle ein Eingabefeld für die verschiedenen API-Schlüssel
        self.api_keys = {}
        api_frame = ttk.LabelFrame(root, text="API Keys")
        api_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # OpenRouter API Key
        openrouter_label = ttk.Label(api_frame, text="OpenRouter API Key:")
        openrouter_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.api_keys['openrouter'] = ttk.Entry(api_frame, show="*")
        self.api_keys['openrouter'].grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # OpenAI API Key
        openai_label = ttk.Label(api_frame, text="OpenAI API Key:")
        openai_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.api_keys['openai'] = ttk.Entry(api_frame, show="*")
        self.api_keys['openai'].grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Anthropic API Key
        anthropic_label = ttk.Label(api_frame, text="Anthropic API Key:")
        anthropic_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.api_keys['anthropic'] = ttk.Entry(api_frame, show="*")
        self.api_keys['anthropic'].grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Mistral API Key
        mistral_label = ttk.Label(api_frame, text="Mistral API Key:")
        mistral_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.api_keys['mistral'] = ttk.Entry(api_frame, show="*")
        self.api_keys['mistral'].grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Google API Key
        google_label = ttk.Label(api_frame, text="Google API Key:")
        google_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.api_keys['google'] = ttk.Entry(api_frame, show="*")
        self.api_keys['google'].grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        # Load API keys from environment variables
        self.load_api_keys()

        # Bind events for API key entries
        for provider in self.api_keys:
            self.api_keys[provider].bind('<FocusOut>', lambda e, p=provider: self.save_api_key(p))
            self.api_keys[provider].bind('<Return>', lambda e, p=provider: self.save_api_key(p))

        # Provider selection
        provider_label = ttk.Label(root, text="Select Provider:")
        provider_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.providers = ['openrouter', 'openai', 'anthropic', 'mistral', 'google']
        self.provider_var = tk.StringVar(root)
        self.provider_var.set(self.providers[0])
        self.provider_dropdown = ttk.Combobox(root, textvariable=self.provider_var, values=self.providers)
        self.provider_dropdown.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.provider_dropdown.bind('<<ComboboxSelected>>', self.on_provider_change)

        # Model selection
        model_label = ttk.Label(root, text="Select Model:")
        model_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.model_var = tk.StringVar(root)
        self.model_dropdown = ttk.Combobox(root, textvariable=self.model_var, values=[])
        self.model_dropdown.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Prompt input
        prompt_label = ttk.Label(root, text="Prompt:")
        prompt_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.prompt_text = scrolledtext.ScrolledText(root, height=5, wrap=tk.WORD)
        self.prompt_text.grid(row=4, column=1, padx=5, pady=5, sticky="nsew")

        # Response output
        response_label = ttk.Label(root, text="Response:")
        response_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.response_text = scrolledtext.ScrolledText(root, height=10, wrap=tk.WORD)
        self.response_text.grid(row=5, column=1, padx=5, pady=5, sticky="nsew")

        # Send button
        self.send_button = ttk.Button(root, text="Send", command=self.send_request)
        self.send_button.grid(row=6, column=1, padx=5, pady=5, sticky="e")

        # Configure grid
        root.grid_columnconfigure(1, weight=1)
        api_frame.grid_columnconfigure(1, weight=1)

        # Initialize models for default provider
        self.on_provider_change(None)

    def save_api_key(self, provider):
        """Save API key to system environment variables"""
        api_key = self.api_keys[provider].get().strip()
        if api_key:
            env_var_name = f"{provider.upper()}_API_KEY"
            if set_environment_variable(env_var_name, api_key):
                messagebox.showinfo("Success", f"{provider.title()} API key saved to system environment variables.")
            else:
                messagebox.showerror("Error", f"Failed to save {provider.title()} API key to system environment variables.")

    def load_api_keys(self):
        """Load API keys from environment variables"""
        env_vars = {
            'openrouter': 'OPENROUTER_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'mistral': 'MISTRAL_API_KEY',
            'google': 'GOOGLE_API_KEY'
        }
        for provider, env_var in env_vars.items():
            api_key = os.getenv(env_var)
            if api_key:
                self.api_keys[provider].insert(0, api_key)

    def create_menu(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Conversation", command=self.new_conversation)
        file_menu.add_command(label="Load Conversation", command=self.load_conversation_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

    def new_conversation(self):
        """Start a new conversation"""
        provider = self.provider_var.get()
        model = self.model_var.get()
        self.conversation_manager.start_new_conversation(provider, model)
        self.prompt_text.delete("1.0", tk.END)
        self.response_text.delete("1.0", tk.END)

    def load_conversation_dialog(self):
        """Show dialog to load a previous conversation"""
        conversations = self.conversation_manager.list_conversations()
        if not conversations:
            messagebox.showinfo("Info", "No saved conversations found.")
            return

        # Create a dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Load Conversation")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()

        # Create a listbox with conversations
        listbox = tk.Listbox(dialog, width=70)
        listbox.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Add conversations to listbox
        for conv in conversations:
            timestamp = datetime.fromisoformat(conv["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            listbox.insert(tk.END, f"{timestamp} - {conv['provider']} - {conv['model']}")

        def load_selected():
            selection = listbox.curselection()
            if selection:
                conv = conversations[selection[0]]
                self.load_conversation(conv)
                dialog.destroy()

        # Add load button
        load_button = ttk.Button(dialog, text="Load", command=load_selected)
        load_button.pack(pady=5)

    def load_conversation(self, conversation):
        """Load a conversation into the GUI"""
        # Set provider and model
        self.provider_var.set(conversation["provider"])
        self.on_provider_change(None)  # Update model list
        self.model_var.set(conversation["model"])

        # Display messages
        self.response_text.delete("1.0", tk.END)
        for msg in conversation["messages"]:
            timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            role = msg["role"].title()
            self.response_text.insert(tk.END, f"[{timestamp}] {role}:\n{msg['content']}\n\n")

    def on_provider_change(self, event):
        """Handle provider change and update available models"""
        provider = self.provider_var.get()
        self.load_models_for_provider(provider)

    def load_models_for_provider(self, provider):
        """Load available models for the selected provider"""
        try:
            # Load models regardless of API key
            if provider == 'openrouter':
                api_key = self.api_keys[provider].get()
                if api_key:
                    self.load_openrouter_models(api_key)
                else:
                    # Default OpenRouter models if no API key
                    self.model_dropdown['values'] = [
                        "openai/gpt-3.5-turbo",
                        "openai/gpt-4",
                        "anthropic/claude-2.1",
                        "google/gemini-pro",
                        "meta-llama/llama-2-70b-chat"
                    ]
                    self.model_var.set("openai/gpt-3.5-turbo")
            elif provider == 'openai':
                self.load_openai_models()
            elif provider == 'anthropic':
                self.load_anthropic_models()
            elif provider == 'mistral':
                self.load_mistral_models()
            elif provider == 'google':
                self.load_google_models()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load models: {str(e)}")

    def load_openrouter_models(self, api_key):
        """Load models from OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repository",
            "X-Title": "LLM GUI"
        }
        response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
        if response.status_code == 200:
            models = response.json()
            model_names = [model["id"] for model in models["data"]]
            self.model_dropdown['values'] = model_names
            if model_names:
                self.model_var.set(model_names[0])

    def load_openai_models(self):
        """Load models from OpenAI"""
        models = [
            "gpt-4-1106-preview",
            "gpt-4-vision-preview",
            "gpt-4",
            "gpt-4-32k",
            "gpt-3.5-turbo-1106",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ]
        self.model_dropdown['values'] = models
        self.model_var.set("gpt-3.5-turbo")

    def load_anthropic_models(self):
        """Load Anthropic models"""
        models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2"
        ]
        self.model_dropdown['values'] = models
        self.model_var.set("claude-2.1")

    def load_mistral_models(self):
        """Load Mistral models"""
        models = [
            "mistral-tiny",
            "mistral-small",
            "mistral-medium",
            "mistral-large-latest",
            "mistral-embed"
        ]
        self.model_dropdown['values'] = models
        self.model_var.set("mistral-small")

    def load_google_models(self):
        """Load Google models"""
        models = [
            "gemini-pro",
            "gemini-pro-vision",
            "text-bison-001",
            "chat-bison-001"
        ]
        self.model_dropdown['values'] = models
        self.model_var.set("gemini-pro")

    def send_request(self):
        """Send request to the selected provider"""
        try:
            provider = self.provider_var.get()
            api_key = self.api_keys[provider].get()
            if not api_key:
                messagebox.showerror("Error", f"Please enter your {provider.title()} API key.")
                return

            model = self.model_var.get()
            if not model:
                messagebox.showerror("Error", "Please select a model.")
                return

            prompt = self.prompt_text.get("1.0", tk.END).strip()
            if not prompt:
                messagebox.showerror("Error", "Please enter a prompt.")
                return

            # Start new conversation if none exists
            if not self.conversation_manager.current_conversation:
                self.conversation_manager.start_new_conversation(provider, model)

            # Add user message to conversation
            self.conversation_manager.add_message("user", prompt)

            # Send request based on provider
            if provider == 'openrouter':
                self.send_openrouter_request(api_key, model, prompt)
            elif provider == 'openai':
                self.send_openai_request(api_key, model, prompt)
            elif provider == 'anthropic':
                self.send_anthropic_request(api_key, model, prompt)
            elif provider == 'mistral':
                self.send_mistral_request(api_key, model, prompt)
            elif provider == 'google':
                self.send_google_request(api_key, model, prompt)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send request: {str(e)}")

    def send_openrouter_request(self, api_key, model, prompt):
        """Send request to OpenRouter API"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repository",
            "X-Title": "LLM GUI"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        self.handle_response(response)

    def send_openai_request(self, api_key, model, prompt):
        """Send request to OpenAI API"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        self.handle_response(response)

    def send_anthropic_request(self, api_key, model, prompt):
        """Send request to Anthropic API"""
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data
        )
        self.handle_response(response)

    def send_mistral_request(self, api_key, model, prompt):
        """Send request to Mistral API"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers=headers,
            json=data
        )
        self.handle_response(response)

    def send_google_request(self, api_key, model, prompt):
        """Send request to Google API"""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "contents": [{"role": "user", "parts": [{"text": prompt}]}]
        }
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent",
            headers=headers,
            json=data
        )
        self.handle_response(response)

    def handle_response(self, response):
        """Handle API response and update UI"""
        if response.status_code == 200:
            result = response.json()
            provider = self.provider_var.get()
            
            # Extract response text based on provider
            if provider == 'openrouter' or provider == 'openai' or provider == 'mistral':
                response_text = result["choices"][0]["message"]["content"]
            elif provider == 'anthropic':
                response_text = result["content"][0]["text"]
            elif provider == 'google':
                response_text = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # Add assistant message to conversation
            self.conversation_manager.add_message("assistant", response_text)
            
            # Save conversation after each response
            self.conversation_manager.save_conversation()
            
            # Update UI with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.response_text.insert(tk.END, f"\n[{timestamp}] Assistant:\n{response_text}\n")
        else:
            messagebox.showerror("Error", f"API request failed: {response.text}")

# Hauptprogramm
if __name__ == "__main__":
    root = tk.Tk()
    app = LLMGUI(root)
    root.mainloop()
