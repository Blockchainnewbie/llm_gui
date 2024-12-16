import os
import unittest
from aider_manager import AiderManager

class TestAiderInitialization(unittest.TestCase):
    def setUp(self):
        # Ensure we have the API key for testing
        if not os.environ.get('ANTHROPIC_API_KEY'):
            self.skipTest("ANTHROPIC_API_KEY not found in environment variables")
    
    def test_basic_initialization(self):
        """Test that AiderManager initializes with minimal settings"""
        manager = AiderManager()
        self.assertIsNotNone(manager.io)
        self.assertIsNotNone(manager.coder)
        self.assertIsNotNone(manager.main_model)
    
    def test_model_initialization(self):
        """Test initialization with specific model"""
        manager = AiderManager()
        manager.initialize_aider(main_model='claude-3-opus-20240229')
        self.assertEqual(manager.main_model, 'claude-3-opus-20240229')
    
    def test_file_handling(self):
        """Test file handling in process_code_edit"""
        manager = AiderManager()
        # Test with non-existent file
        result = manager.process_code_edit("test", ["nonexistent.py"])
        self.assertFalse(result['success'])
        self.assertIn('File not found', result['error'])

if __name__ == '__main__':
    unittest.main()
