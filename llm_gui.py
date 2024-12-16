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
from aider_manager import AiderManager
from tkinter import filedialog
import threading
from queue import Queue

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
        self.aider_manager = AiderManager()
        self.event_queue = Queue()
        
        # Start event processing thread
        self.event_thread = threading.Thread(target=self.process_events, daemon=True)
        self.event_thread.start()
        
        # Create menu bar
        self.create_menu()

        # Initialize variables
        self.api_keys = {
            'anthropic': tk.StringVar(),
            'openai': tk.StringVar(),
            'google': tk.StringVar(),
            'mistral': tk.StringVar(),
            'openrouter': tk.StringVar()
        }
        
        # Load API keys from environment
        self.load_api_keys()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create API key entries
        self.create_api_key_entries()
        
        # Create provider and model selection
        self.create_provider_model_selection()
        
        # Create prompt and response areas
        self.create_prompt_response_areas()

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
        env_mapping = {
            'anthropic': 'ANTHROPIC_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'google': 'GOOGLE_API_KEY',
            'mistral': 'MISTRAL_API_KEY',
            'openrouter': 'OPENROUTER_API_KEY'
        }
        for provider, env_var in env_mapping.items():
            key = os.environ.get(env_var, '')
            self.api_keys[provider].set(key)

    def create_menu(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Conversation", command=self.new_conversation)
        file_menu.add_command(label="Load Conversation", command=self.load_conversation_dialog)
        
        # Export submenu
        export_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Export Conversation", menu=export_menu)
        export_menu.add_command(label="Export as TXT", command=lambda: self.export_conversation('txt'))
        export_menu.add_command(label="Export as PDF", command=lambda: self.export_conversation('pdf'))
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Code Edit with Aider", command=self.show_aider_dialog)
        
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
        self.update_models()
        self.model_var.set(conversation["model"])

        # Display messages
        self.response_text.delete("1.0", tk.END)
        for msg in conversation["messages"]:
            timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            role = msg["role"].title()
            self.response_text.insert(tk.END, f"[{timestamp}] {role}:\n{msg['content']}\n\n")

    def create_api_key_entries(self):
        """Create API key entries"""
        api_frame = ttk.LabelFrame(self.main_frame, text="API Keys")
        api_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Anthropic API Key
        anthropic_label = ttk.Label(api_frame, text="Anthropic API Key:")
        anthropic_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.anthropic_entry = ttk.Entry(api_frame, textvariable=self.api_keys['anthropic'], show="*")
        self.anthropic_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # OpenAI API Key
        openai_label = ttk.Label(api_frame, text="OpenAI API Key:")
        openai_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.openai_entry = ttk.Entry(api_frame, textvariable=self.api_keys['openai'], show="*")
        self.openai_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Google API Key
        google_label = ttk.Label(api_frame, text="Google API Key:")
        google_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.google_entry = ttk.Entry(api_frame, textvariable=self.api_keys['google'], show="*")
        self.google_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Mistral API Key
        mistral_label = ttk.Label(api_frame, text="Mistral API Key:")
        mistral_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.mistral_entry = ttk.Entry(api_frame, textvariable=self.api_keys['mistral'], show="*")
        self.mistral_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # OpenRouter API Key
        openrouter_label = ttk.Label(api_frame, text="OpenRouter API Key:")
        openrouter_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.openrouter_entry = ttk.Entry(api_frame, textvariable=self.api_keys['openrouter'], show="*")
        self.openrouter_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        # Bind events for API key entries
        for provider in self.api_keys:
            entry = getattr(self, f"{provider}_entry")
            entry.bind('<FocusOut>', lambda e, p=provider: self.save_api_key(p))
            entry.bind('<Return>', lambda e, p=provider: self.save_api_key(p))

    def create_provider_model_selection(self):
        """Create provider and model selection dropdowns"""
        # Provider selection
        ttk.Label(self.main_frame, text="Select Provider:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.provider_var = tk.StringVar(value='anthropic')  # Set Anthropic as default
        self.provider_dropdown = ttk.Combobox(self.main_frame, textvariable=self.provider_var)
        self.provider_dropdown['values'] = ['anthropic', 'openai', 'google', 'mistral', 'openrouter']
        self.provider_dropdown.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)
        self.provider_dropdown.bind('<<ComboboxSelected>>', self.update_models)
        
        # Model selection
        ttk.Label(self.main_frame, text="Select Model:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar()
        self.model_dropdown = ttk.Combobox(self.main_frame, textvariable=self.model_var)
        self.model_dropdown.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Initialize models for default provider
        self.update_models()

    def create_prompt_response_areas(self):
        """Create prompt and response areas"""
        # Prompt input
        prompt_label = ttk.Label(self.main_frame, text="Prompt:")
        prompt_label.grid(row=8, column=0, padx=5, pady=5, sticky="w")
        self.prompt_text = scrolledtext.ScrolledText(self.main_frame, height=5, wrap=tk.WORD)
        self.prompt_text.grid(row=8, column=1, padx=5, pady=5, sticky="nsew")

        # Response output
        response_label = ttk.Label(self.main_frame, text="Response:")
        response_label.grid(row=9, column=0, padx=5, pady=5, sticky="w")
        self.response_text = scrolledtext.ScrolledText(self.main_frame, height=10, wrap=tk.WORD)
        self.response_text.grid(row=9, column=1, padx=5, pady=5, sticky="nsew")

        # Send button
        self.send_button = ttk.Button(self.main_frame, text="Send", command=self.send_request)
        self.send_button.grid(row=10, column=1, padx=5, pady=5, sticky="e")

        # Configure grid
        self.main_frame.grid_columnconfigure(1, weight=1)

    def update_models(self, event=None):
        """Update available models based on selected provider"""
        provider = self.provider_var.get()
        
        # Set available models based on provider
        if provider == 'anthropic':
            models = ['claude-3-opus-20240229', 'claude-3-sonnet-20240229']
        elif provider == 'openai':
            models = ['gpt-4', 'gpt-3.5-turbo']
        elif provider == 'google':
            models = ['gemini-pro']
        elif provider == 'mistral':
            models = ['mistral-tiny', 'mistral-small', 'mistral-medium']
        else:  # openrouter
            models = ['openrouter/auto']
            
        self.model_dropdown['values'] = models
        self.model_var.set(models[0])  # Set first model as default

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
            if provider == 'anthropic':
                self.send_anthropic_request(api_key, model, prompt)
            elif provider == 'openai':
                self.send_openai_request(api_key, model, prompt)
            elif provider == 'google':
                self.send_google_request(api_key, model, prompt)
            elif provider == 'mistral':
                self.send_mistral_request(api_key, model, prompt)
            elif provider == 'openrouter':
                self.send_openrouter_request(api_key, model, prompt)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send request: {str(e)}")

    def send_anthropic_request(self, api_key, model, prompt):
        """Send request to Anthropic API"""
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096
        }
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
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

    def handle_response(self, response):
        """Handle API response and update UI"""
        if response.status_code == 200:
            result = response.json()
            provider = self.provider_var.get()
            
            # Extract response text based on provider
            if provider == 'anthropic':
                response_text = result["content"][0]["text"]
            elif provider == 'openai' or provider == 'mistral':
                response_text = result["choices"][0]["message"]["content"]
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

    def export_conversation(self, format_type: str):
        """Export the current conversation"""
        if not self.conversation_manager.current_conversation:
            messagebox.showinfo("Info", "No active conversation to export.")
            return
        
        try:
            filepath = self.conversation_manager.export_conversation(
                self.conversation_manager.current_conversation.id,
                format_type
            )
            
            # Show success message with file location
            messagebox.showinfo(
                "Export Successful",
                f"Conversation exported successfully!\nLocation: {filepath}"
            )
            
            # Open the exports folder
            os.startfile(os.path.dirname(filepath))
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export conversation: {str(e)}")

    def show_aider_dialog(self):
        """Show dialog for Aider code editing"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Aider Code Editor")
        dialog.geometry("1200x800")
        
        # Set up font
        text_font = ("Consolas", 10)
        
        # Configure dialog grid
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(0, weight=0)  # Model selection row
        dialog.grid_rowconfigure(1, weight=1)  # Main content row
        
        # Model selection frame at top
        model_frame = ttk.LabelFrame(dialog, text="Model Selection")
        model_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Main model selection
        main_model_label = ttk.Label(model_frame, text="Main Model:")
        main_model_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.main_model_var = tk.StringVar(value="gpt-4")
        self.main_model_dropdown = ttk.Combobox(model_frame, textvariable=self.main_model_var,
                                              values=self.aider_manager.get_available_models())
        self.main_model_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Weak model selection
        weak_model_label = ttk.Label(model_frame, text="Helper Model:")
        weak_model_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.weak_model_var = tk.StringVar(value="gpt-3.5-turbo")
        self.weak_model_dropdown = ttk.Combobox(model_frame, textvariable=self.weak_model_var,
                                              values=self.aider_manager.get_available_models())
        self.weak_model_dropdown.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Configure model frame grid
        model_frame.grid_columnconfigure(1, weight=1)
        model_frame.grid_columnconfigure(3, weight=1)
        
        # Split frame for files and edit
        split_frame = ttk.PanedWindow(dialog, orient=tk.HORIZONTAL)
        split_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # Left panel - File list
        left_frame = ttk.Frame(split_frame)
        split_frame.add(left_frame, weight=1)
        
        # File list with scrollbar
        file_scroll = ttk.Scrollbar(left_frame)
        file_scroll.pack(side="right", fill="y")
        
        self.file_listbox = tk.Listbox(left_frame, selectmode="extended",
                                      yscrollcommand=file_scroll.set,
                                      font=text_font)
        self.file_listbox.pack(side="left", fill="both", expand=True)
        file_scroll.config(command=self.file_listbox.yview)
        
        # Buttons for file management
        file_btn_frame = ttk.Frame(left_frame)
        file_btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(file_btn_frame, text="Add Files",
                  command=self.add_files_to_edit).pack(side="left", padx=2)
        ttk.Button(file_btn_frame, text="Remove Selected",
                  command=lambda: [self.file_listbox.delete(i) for i in self.file_listbox.curselection()[::-1]]
                  ).pack(side="left", padx=2)
        
        # Right panel - Edit instructions
        right_frame = ttk.Frame(split_frame)
        split_frame.add(right_frame, weight=2)
        
        # Prompt input
        prompt_frame = ttk.LabelFrame(right_frame, text="Edit Instructions")
        prompt_frame.pack(fill="both", expand=True)
        
        prompt_scroll = ttk.Scrollbar(prompt_frame)
        prompt_scroll.pack(side="right", fill="y")
        
        self.aider_prompt = tk.Text(prompt_frame, height=5, wrap=tk.WORD,
                                  yscrollcommand=prompt_scroll.set,
                                  font=text_font)
        self.aider_prompt.pack(fill="both", expand=True, padx=5, pady=5)
        prompt_scroll.config(command=self.aider_prompt.yview)
        
        # Send button frame
        send_frame = ttk.Frame(right_frame)
        send_frame.pack(fill="x", pady=5)
        
        self.edit_status = ttk.Label(send_frame, text="")
        self.edit_status.pack(side="left")
        
        ttk.Button(send_frame, text="Send to Aider",
                  command=self.process_aider_edit).pack(side="right")
        
        # Response display
        response_frame = ttk.LabelFrame(right_frame, text="Aider Response")
        response_frame.pack(fill="both", expand=True)
        
        response_scroll = ttk.Scrollbar(response_frame)
        response_scroll.pack(side="right", fill="y")
        
        self.aider_response = tk.Text(response_frame, height=10, wrap=tk.WORD,
                                    yscrollcommand=response_scroll.set,
                                    font=text_font)
        self.aider_response.pack(fill="both", expand=True, padx=5, pady=5)
        response_scroll.config(command=self.aider_response.yview)
        
        # Console output display
        console_frame = ttk.LabelFrame(right_frame, text="Console Output")
        console_frame.pack(fill="both", expand=True)
        
        console_scroll = ttk.Scrollbar(console_frame)
        console_scroll.pack(side="right", fill="y")
        
        self.console_text = tk.Text(console_frame, height=5, wrap=tk.WORD,
                                  yscrollcommand=console_scroll.set,
                                  font=text_font)
        self.console_text.pack(fill="both", expand=True, padx=5, pady=5)
        console_scroll.config(command=self.console_text.yview)

    def add_files_to_edit(self):
        """Add files to the edit list"""
        files = filedialog.askopenfilenames(
            title="Select Files to Edit",
            filetypes=[("Python files", "*.py"), 
                      ("All files", "*.*")]
        )
        for file in files:
            self.file_listbox.insert(tk.END, file)

    def process_aider_edit(self):
        """Process the code edit request with Aider"""
        files = list(self.file_listbox.get(0, tk.END))
        prompt = self.aider_prompt.get("1.0", tk.END).strip()
        main_model = self.main_model_var.get()
        weak_model = self.weak_model_var.get()
        
        if not files:
            messagebox.showwarning("Warning", "Please select at least one file to edit")
            return
            
        if not prompt:
            messagebox.showwarning("Warning", "Please provide edit instructions")
            return
        
        # Update status
        self.edit_status.config(text="Processing edit request...")
        
        # Process in background thread to keep UI responsive
        def process_edit():
            try:
                response = self.aider_manager.process_code_edit(prompt, files)  
                # Schedule response handling in main thread
                self.root.after(0, lambda: self._handle_aider_response(response))
            except Exception as e:
                error_response = {'success': False, 'error': str(e)}
                self.root.after(0, lambda: self._handle_aider_response(error_response))
        
        # Start processing thread
        threading.Thread(target=process_edit, daemon=True).start()

    def _handle_aider_response(self, response):
        """Handle the response from Aider"""
        # Clear previous status and response
        self.edit_status.config(text="")
        self.aider_response.delete("1.0", tk.END)
        self.console_text.delete("1.0", tk.END)
        
        if response.get('success'):
            # Show the main response message
            message = response.get('message', '')
            if message:
                try:
                    # Try to insert the message directly
                    self.aider_response.insert(tk.END, message + "\n")
                except tk.TclError:
                    # If there's an encoding error, try to clean the text
                    clean_message = ''.join(char for char in message if ord(char) < 128)
                    self.aider_response.insert(tk.END, clean_message + "\n")
            
            # Show console output if available
            if 'console_output' in response:
                self.console_text.insert(tk.END, response['console_output'])
                self.console_text.see(tk.END)
            
            # Show changed files if any
            changed_files = response.get('files_changed', [])
            if changed_files:
                self.aider_response.insert(tk.END, "\nFiles changed:\n")
                for file in changed_files:
                    self.aider_response.insert(tk.END, f"- {file}\n")
                
            # Update status based on changes
            if changed_files:
                self.edit_status.config(text="Changes applied successfully!")
            else:
                self.edit_status.config(text="No changes were needed.")
        else:
            # Show error message
            self.edit_status.config(text="Edit failed!")
            error_msg = response.get('error', 'Unknown error occurred')
            details = response.get('details', '')
            
            try:
                # Try to insert the error message directly
                self.aider_response.insert(tk.END, f"Error: {error_msg}\n")
                if details:
                    self.aider_response.insert(tk.END, f"\nDetails: {details}")
            except tk.TclError:
                # If there's an encoding error, try to clean the text
                clean_error = ''.join(char for char in error_msg if ord(char) < 128)
                clean_details = ''.join(char for char in details if ord(char) < 128) if details else ''
                self.aider_response.insert(tk.END, f"Error: {clean_error}\n")
                if clean_details:
                    self.aider_response.insert(tk.END, f"\nDetails: {clean_details}")

    def process_events(self):
        """Process async events in a separate thread"""
        while True:
            try:
                coro, callback = self.event_queue.get()
                # Removed asyncio.run
                callback(coro)
            except Exception as e:
                print(f"Error processing event: {e}")

# Hauptprogramm
if __name__ == "__main__":
    root = tk.Tk()
    app = LLMGUI(root)
    root.mainloop()
