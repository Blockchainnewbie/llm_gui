import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch
import sys
import os
import tempfile
from pathlib import Path

# Add the parent directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from llm_gui import LLMGUI, set_environment_variable

class TestLLMGUI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create a temporary directory for home
        self.temp_home = Path(tempfile.mkdtemp())
        self.home_patcher = patch('pathlib.Path.home', return_value=self.temp_home)
        self.home_patcher.start()
        
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', {
            'ANTHROPIC_API_KEY': 'test-key',
        }, clear=True)
        self.env_patcher.start()
        
        # Initialize Tkinter root window
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the window
        self.root.title("Test Window")
        self.root.grid_columnconfigure(0, weight=1)
        
        # Mock Aider manager
        self.mock_aider = MagicMock()
        self.aider_patcher = patch('llm_gui.AiderManager', return_value=self.mock_aider)
        self.aider_patcher.start()
        
        # Set up mock model
        self.mock_aider.get_available_models.return_value = ['claude-3-opus-20240229']
        self.mock_aider.main_model = 'claude-3-opus-20240229'
        self.mock_aider.process_code_edit = MagicMock()
        
        # Create GUI instance
        self.gui = LLMGUI(self.root)
    
    def tearDown(self):
        """Clean up after each test method"""
        self.env_patcher.stop()
        self.aider_patcher.stop()
        self.home_patcher.stop()
        if os.path.exists(self.temp_home):
            os.rmdir(self.temp_home)
        self.root.destroy()
    
    def test_load_api_keys(self):
        """Test loading API keys from environment"""
        self.gui.load_api_keys()
        self.assertEqual(self.gui.api_keys['anthropic'].get(), 'test-key')
    
    def test_save_api_key(self):
        """Test saving API key"""
        with patch('llm_gui.set_environment_variable') as mock_set_env:
            mock_set_env.return_value = True
            self.gui.api_keys['anthropic'].set('new-test-key')
            self.gui.save_api_key('anthropic')
            mock_set_env.assert_called_once_with('ANTHROPIC_API_KEY', 'new-test-key')
    
    def test_show_aider_dialog(self):
        """Test Aider dialog creation"""
        self.gui.show_aider_dialog()
        
        # Verify dialog widgets exist
        dialog = self.root.winfo_children()[-1]
        self.assertIsInstance(dialog, tk.Toplevel)
        
        # Check main components
        self.assertTrue(hasattr(self.gui, 'main_model_var'))
        self.assertTrue(hasattr(self.gui, 'weak_model_var'))
        self.assertTrue(hasattr(self.gui, 'file_listbox'))
        self.assertTrue(hasattr(self.gui, 'aider_prompt'))
        self.assertTrue(hasattr(self.gui, 'aider_response'))
    
    def test_process_aider_edit(self):
        """Test Aider edit processing"""
        # Mock the aider manager's process_code_edit method
        self.mock_aider.process_code_edit.return_value = {
            'success': True,
            'message': 'Test response',
            'files_changed': ['test.py']
        }

        # Show dialog and set up test data
        self.gui.show_aider_dialog()
        self.gui.aider_prompt.insert('1.0', 'Test edit request')
        
        # Add a test file to edit
        self.gui.file_listbox.insert(tk.END, "test.py")

        # Trigger process edit
        self.gui.process_aider_edit()

        # Give the thread time to run and process events
        import time
        time.sleep(0.1)  # Wait for thread to start
        
        # Process all pending events
        while self.root.dooneevent(tk._tkinter.ALL_EVENTS | tk._tkinter.DONT_WAIT):
            pass

        # Verify aider manager was called with correct arguments
        self.mock_aider.process_code_edit.assert_called_once_with('Test edit request')
    
    def test_handle_aider_response(self):
        """Test handling Aider responses"""
        # Show dialog first
        self.gui.show_aider_dialog()
        
        # Test successful response
        success_response = {
            'success': True,
            'message': 'Test message',
            'files_changed': ['test.py']
        }
        self.gui._handle_aider_response(success_response)
        self.assertEqual(self.gui.edit_status.cget('text'), 'Changes applied successfully!')
        
        # Test response with no changes
        no_change_response = {
            'success': True,
            'message': 'No changes needed',
            'files_changed': []
        }
        self.gui._handle_aider_response(no_change_response)
        self.assertEqual(self.gui.edit_status.cget('text'), 'No changes were needed.')
        
        # Test error response
        error_response = {
            'success': False,
            'error': 'Test error',
            'details': 'Error details'
        }
        self.gui._handle_aider_response(error_response)
        self.assertEqual(self.gui.edit_status.cget('text'), 'Edit failed!')
    
    def test_add_files_to_edit(self):
        """Test adding files to edit list"""
        # Show dialog first
        self.gui.show_aider_dialog()
        
        # Mock filedialog.askopenfilenames
        with patch('tkinter.filedialog.askopenfilenames') as mock_dialog:
            mock_dialog.return_value = ['test1.py', 'test2.py']
            self.gui.add_files_to_edit()
            
            # Verify files were added to listbox
            files = list(self.gui.file_listbox.get(0, tk.END))
            self.assertEqual(files, ['test1.py', 'test2.py'])

if __name__ == '__main__':
    unittest.main()
