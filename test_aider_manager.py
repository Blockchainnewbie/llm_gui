import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from aider_manager import AiderManager

class TestAiderManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.py")
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("def test_function():\n    pass\n")
            
        # Create a temporary directory for home
        self.temp_home = Path(tempfile.mkdtemp())
        self.home_patcher = patch('pathlib.Path.home', return_value=self.temp_home)
        self.home_patcher.start()
            
        # Mock environment variables and console check
        self.mock_io = MagicMock()
        self.mock_io.pretty = True
        
        self.patches = [
            patch.dict('os.environ', {
                'ANTHROPIC_API_KEY': 'test-key',
            }, clear=True),
            patch('aider_manager.AiderManager._has_console', return_value=True),
            patch('aider.io.InputOutput', return_value=self.mock_io)
        ]
        
        for p in self.patches:
            p.start()
        
        # Create AiderManager instance with Anthropic model
        self.manager = AiderManager()
        self.manager.set_model('claude-3-opus-20240229')
    
    def tearDown(self):
        """Clean up after each test method"""
        # Remove test files
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)
        if os.path.exists(self.temp_home):
            # Remove all files in temp_home
            for root, dirs, files in os.walk(self.temp_home, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.temp_home)
            
        # Stop all patches
        for p in self.patches:
            p.stop()
        self.home_patcher.stop()
    
    def test_clean_text(self):
        """Test the clean_text method"""
        # Test with various special characters
        test_cases = [
            ('\u22ee', '...'),  # Vertical ellipsis
            ('\u2026', '...'),  # Horizontal ellipsis
            ('\u2013', '-'),    # En dash
            ('\u2014', '--'),   # Em dash
            ('\u201c\u201d', '""'),  # Quotation marks
            ('\u2018\u2019', "''"),  # Single quotes
            ('Hello\rWorld', 'Hello\nWorld'),  # Carriage return
            ('Hello\r\nWorld', 'Hello\nWorld'),  # Windows line ending
            ('Hello\x00World', 'HelloWorld'),  # Null character
            ('', ''),  # Empty string
            (None, ''),  # None value
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.manager.clean_text(input_text)
                self.assertEqual(result, expected)
    
    def test_initialize_aider(self):
        """Test Aider initialization"""
        # Test successful initialization
        self.assertIsNotNone(self.manager.coder)
        
        # Test initialization with missing API key
        with patch.dict('os.environ', {}, clear=True):  # Clear all environment variables
            with self.assertRaises(RuntimeError):
                self.manager.initialize_aider()
    
    def test_process_code_edit(self):
        """Test code editing process"""
        # Test with non-existent file
        response = self.manager.process_code_edit(
            "Fix the code",
            ["nonexistent.py"]
        )
        self.assertFalse(response['success'])
        self.assertIn('File not found', response['error'])
        
        # Test with existing file
        response = self.manager.process_code_edit(
            "Add a docstring",
            [self.test_file]
        )
        self.assertTrue(isinstance(response, dict))
        self.assertIn('success', response)
        
        # Test with empty prompt
        response = self.manager.process_code_edit(
            "",
            [self.test_file]
        )
        self.assertTrue(isinstance(response, dict))
        self.assertIn('success', response)
    
    def test_get_available_models(self):
        """Test getting available models"""
        models = self.manager.get_available_models()
        self.assertIsInstance(models, list)
        self.assertGreater(len(models), 0)
        self.assertIn('claude-3-opus-20240229', models)
    
    def test_set_model(self):
        """Test model setting"""
        # Test with valid models
        self.manager.set_model("claude-3-opus-20240229")
        self.assertEqual(self.manager.main_model, "claude-3-opus-20240229")
        
        # Test with invalid model
        with self.assertRaises(ValueError):
            self.manager.set_model("invalid-model")

if __name__ == '__main__':
    unittest.main()
