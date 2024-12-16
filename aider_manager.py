"""
Aider integration manager for the LLM GUI application.
Handles communication with the Aider AI assistant.
"""

import os
import sys
import subprocess
from typing import List, Dict, Optional
from pathlib import Path
from aider.coders import EditBlockCoder
from aider.io import InputOutput
from aider.models import Model
from aider import models
import winreg

class AiderManager:
    # List of API keys to try in order of preference
    API_KEYS = [
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GOOGLE_API_KEY",
        "MISTRAL_API_KEY",
        "OPENROUTER_API_KEY"
    ]
    
    def __init__(self):
        """Initialize the Aider manager"""
        self.coder = None
        self.main_model = None
        self.weak_model = None
        self.active_provider = None
        
        # Try to set an API key from available providers
        self.set_api_key_from_registry()
            
        self.initialize_aider()
    
    def _has_console(self) -> bool:
        """Check if we have a valid console"""
        try:
            # Try to get console window info
            from ctypes import windll
            return bool(windll.kernel32.GetConsoleWindow())
        except:
            return False
            
    def _initialize_console(self):
        """Initialize a new console window for interactive features"""
        try:
            # Skip console initialization in GUI mode
            return
        except Exception as e:
            print(f"Warning: Could not initialize console: {e}")
    
    def set_api_key_from_registry(self):
        """Get API key from Windows Registry and set it in environment"""
        found_key = False
        error_messages = []
        
        # Try each API key in order
        for api_key_name in self.API_KEYS:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ)
                api_key = winreg.QueryValueEx(key, api_key_name)[0]
                winreg.CloseKey(key)
                
                if api_key:
                    # Set the provider's key in environment
                    os.environ[api_key_name] = api_key
                    
                    # Set the active provider
                    self.active_provider = api_key_name.split('_')[0].lower()
                    
                    # Set model based on provider
                    self._set_model_for_provider()
                    
                    print(f"Using {api_key_name} for Aider integration")
                    found_key = True
                    break
                    
            except Exception as e:
                error_messages.append(f"{api_key_name}: {str(e)}")
                continue
        
        if not found_key:
            error_list = "\n".join(error_messages)
            raise RuntimeError(f"No valid API keys found. Tried:\n{error_list}")
    
    def _set_model_for_provider(self):
        """Set appropriate model based on active provider"""
        if self.active_provider == 'anthropic':
            self.main_model = 'claude-3-opus-20240229'
        elif self.active_provider == 'google':
            self.main_model = 'gemini-pro'
        elif self.active_provider == 'mistral':
            self.main_model = 'mistral-large'
        elif self.active_provider == 'openrouter':
            self.main_model = 'openrouter/auto'  # Let OpenRouter choose best model
        # OpenAI models remain as set in __init__
    
    def initialize_aider(self, main_model=None, weak_model=None):
        """Initialize Aider with the specified models"""
        try:
            # Check for required API keys
            if not os.environ.get('ANTHROPIC_API_KEY'):
                raise RuntimeError("ANTHROPIC_API_KEY not found in environment variables")

            # Create a console that captures output
            class CaptureConsole:
                def __init__(self):
                    self.output = []
                    self.last_output = ""

                def print(self, *args, sep=' ', end='\n', **kwargs):
                    # Combine the arguments into a single string
                    output_text = sep.join(str(arg) for arg in args) + end
                    # Store in both the full history and last output
                    self.output.append(output_text)
                    self.last_output = output_text
                
                def input(self, *args, **kwargs):
                    if args:  # If there's a prompt, capture it too
                        self.print(args[0], end='')
                    return ""  # Return empty string for any input requests
                
                def get_output(self):
                    """Get all captured output"""
                    return ''.join(self.output)
                
                def get_last_output(self):
                    """Get the last captured output"""
                    return self.last_output
                
                def clear(self):
                    """Clear the captured output"""
                    self.output = []
                    self.last_output = ""

            # Create InputOutput instance with minimal parameters
            self.io = InputOutput(
                yes=True,  # Auto-confirm prompts
                pretty=True,  # Enable pretty formatting
                chat_history_file=None  # Disable chat history file
            )
            
            # Replace the console with our capturing version
            self.io.console = CaptureConsole()
            
            # Initialize coder with Anthropic model
            model_instance = Model(main_model or 'claude-3-opus-20240229')
            
            self.coder = EditBlockCoder(
                fnames=[],
                io=self.io,
                main_model=model_instance,
                stream=False  # Disable streaming to avoid console issues
            )
            
            # Set the models
            self.main_model = model_instance.name
            self.weak_model = weak_model
            
            return True
        
        except Exception as e:
            # Re-raise RuntimeError for missing API key
            if "ANTHROPIC_API_KEY not found" in str(e):
                raise
            raise RuntimeError(f"Failed to initialize Aider: {str(e)}")
    
    def get_console_output(self):
        """Get all captured console output"""
        if hasattr(self.io, 'console') and hasattr(self.io.console, 'get_output'):
            return self.io.console.get_output()
        return ""
    
    def get_last_output(self):
        """Get the last console output"""
        if hasattr(self.io, 'console') and hasattr(self.io.console, 'get_last_output'):
            return self.io.console.get_last_output()
        return ""
    
    def clear_console(self):
        """Clear the captured console output"""
        if hasattr(self.io, 'console') and hasattr(self.io.console, 'clear'):
            self.io.console.clear()
    
    def process_code_edit(self, prompt: str, files: List[str], main_model: str = None, weak_model: str = None) -> Dict:
        """
        Process a code editing request using Aider.
        
        Args:
            prompt (str): The user's editing request
            files (List[str]): List of files to be considered for editing
            main_model (str, optional): Main model to use for editing
            weak_model (str, optional): Helper model to use for summaries
            
        Returns:
            Dict: Response containing edits, status, and console output
        """
        try:
            # Clear previous console output
            self.clear_console()
            
            # Initialize or reinitialize Aider with the specified models if needed
            if not self.coder or main_model != self.main_model or weak_model != self.weak_model:
                self.initialize_aider(main_model, weak_model)
            
            # Reset files for this request
            self.coder.abs_fnames = set()
            
            # Add files to Aider's tracking
            valid_files = []
            for file in files:
                if os.path.exists(file):
                    abs_path = str(Path(file).resolve())
                    # Skip files that might cause git issues
                    if any(skip in abs_path.lower() for skip in ['.git', '.env', 'venv', '__pycache__']):
                        continue
                    valid_files.append(abs_path)
                else:
                    raise FileNotFoundError(f"File not found: {file}")
            
            if not valid_files:
                return {
                    'success': False,
                    'error': 'No valid files to edit',
                    'details': 'All selected files were skipped or invalid',
                    'console_output': self.get_console_output()
                }
            
            # Set the files to be edited
            self.coder.abs_fnames = set(valid_files)
            
            # Clean the prompt text and add context
            clean_prompt = self.clean_text(prompt)
            full_prompt = f"""Please help me modify the code according to these instructions:

{clean_prompt}

The files available for editing are:
{chr(10).join('- ' + os.path.basename(f) for f in valid_files)}

Please make the changes needed while following these guidelines:
1. Show the changes in diff format
2. Only modify the specified files
3. Keep the changes minimal and focused
4. Preserve existing code style
5. Add comments for complex changes
"""
            
            try:
                # Process the edit request using run_one which handles the chat and edits
                self.coder.run_one(full_prompt, preproc=True)
            except Exception as edit_error:
                if "git" in str(edit_error).lower():
                    return {
                        'success': False,
                        'error': 'Git operation failed',
                        'details': 'Make sure the files are in a valid git repository and you have the necessary permissions.',
                        'console_output': self.get_console_output()
                    }
                raise  # Re-raise if it's not a git error
            
            # Get the edits and response
            edits = self.coder.get_edits()
            
            # Clean and format the response text
            response_text = self.clean_text(self.coder.partial_response_content or "No changes were needed.")
            
            # Get and clean any tool output
            tool_output = ""
            if hasattr(self.coder.io, 'get_tool_output'):
                tool_output = self.coder.io.get_tool_output()
                if tool_output:
                    tool_output = self.clean_text(tool_output)
                    response_text = tool_output + "\n\n" + response_text
            
            return {
                'success': True,
                'edits': edits,
                'message': response_text,
                'files_changed': list(set(edit.fname for edit in edits)) if edits else [],
                'console_output': self.get_console_output()
            }
            
        except Exception as e:
            error_msg = self.clean_text(str(e))
            return {
                'success': False,
                'error': error_msg,
                'details': str(e),  # Include original error for debugging
                'console_output': self.get_console_output()
            }
        finally:
            # Clear files for next request
            if self.coder:
                self.coder.abs_fnames = set()
    
    def clean_text(self, text: str) -> str:
        """Clean text by removing problematic characters and normalizing line endings"""
        if not text:
            return ""
        # Replace problematic characters with safe alternatives
        replacements = {
            '\u22ee': '...',  # Vertical ellipsis
            '\u2026': '...',  # Horizontal ellipsis
            '\u2013': '-',    # En dash
            '\u2014': '--',   # Em dash
            '\u201c': '"',    # Left double quotation mark
            '\u201d': '"',    # Right double quotation mark
            '\u2018': "'",    # Left single quotation mark
            '\u2019': "'",    # Right single quotation mark
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove any remaining non-printable characters
        return ''.join(char for char in text if char.isprintable() or char in '\n\t')
    
    def set_model(self, main_model: str, weak_model: str = None):
        """
        Change the model used by Aider.
        
        Args:
            main_model (str): New main model to use
            weak_model (str): New weak model to use
        """
        if main_model not in self.get_available_models():
            raise ValueError(f"Unsupported model: {main_model}")
        
        self.initialize_aider(main_model, weak_model)
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available models for Aider.
        
        Returns:
            List[str]: List of model names
        """
        # Return models based on active provider
        if self.active_provider == 'anthropic':
            return ['claude-3-opus-20240229', 'claude-3-sonnet-20240229']
        elif self.active_provider == 'openai':
            return models.OPENAI_MODELS
        elif self.active_provider == 'google':
            return ['gemini-pro']
        elif self.active_provider == 'mistral':
            return ['mistral-large']
        elif self.active_provider == 'openrouter':
            return ['openrouter/auto']
        else:
            return []
