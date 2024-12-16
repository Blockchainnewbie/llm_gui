# LLM GUI Developer Instructions

This document contains all necessary information to rebuild and maintain the LLM GUI application, a Python-based GUI tool that integrates with various LLM APIs and the Aider code editing framework.

## Project Structure

```
llm_gui/
├── llm_gui.py          # Main GUI application
├── aider_manager.py    # Aider integration and management
├── test_llm_gui.py     # GUI tests
├── test_aider_init.py  # Aider initialization tests
├── requirements.txt    # Python dependencies
└── README.md          # User documentation
```

## Core Components

### 1. GUI Application (`llm_gui.py`)

The main GUI application built with tkinter, featuring:
- File selection and management
- Request input area
- Response display
- Console output display
- Error handling and status updates

Key classes:
- `LLMGUI`: Main application window
- `FileTreeview`: Custom treeview for file selection
- `ScrollableFrame`: Reusable scrollable frame component

### 2. Aider Manager (`aider_manager.py`)

Handles integration with the Aider framework, including:
- Code editing requests
- Console output capture
- Git operations
- Error handling
- CMD.exe process management

Key classes:
- `AiderManager`: Main integration class
- `CaptureConsole`: Console output capture utility

## Dependencies

Required Python packages:
```
tkinter
aider-chat
anthropic
python-dotenv
subprocess
```

## Environment Setup

1. Required Environment Variables:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

2. System Requirements:
   - Windows OS (for cmd.exe integration)
   - Git installed and configured
   - Python 3.8 or higher

3. Git Repository Setup:
   - Initialize git repository
   - Set up .gitignore for Python
   - Configure git user and email

## Implementation Details

### GUI Implementation

1. Main Window Layout:
   - Left side: File selection and input
   - Right side: Response and console output
   - Status bar at bottom

2. File Management:
   - Tree-based file selection
   - File type filtering
   - Git integration

3. Request Processing:
   - Input validation
   - Async processing
   - Progress indication

### Aider Integration

1. Console Management:
   - Start cmd.exe in new window
   - Capture all Aider output
   - Store in memory
   - Display in GUI
   - Cleanup on exit

2. Code Editing:
   - File validation
   - Git status checking
   - Edit processing
   - Response formatting

3. Error Handling:
   - API errors
   - Git errors
   - File system errors

## Testing

1. GUI Tests (`test_llm_gui.py`):
   - Window creation
   - Component interaction
   - Event handling

2. Aider Tests (`test_aider_init.py`):
   - Initialization
   - API integration
   - Console capture
   - Error cases

## Common Issues and Solutions

1. Console Issues:
   ```python
   # Start cmd.exe in a new window
   self.cmd_process = subprocess.Popen(
       ['cmd.exe'],
       creationflags=subprocess.CREATE_NEW_CONSOLE
   )

   # Handle cleanup
   def __del__(self):
       if hasattr(self, 'cmd_process') and self.cmd_process:
           self.cmd_process.terminate()
   ```

2. Git Integration:
   ```python
   # Skip problematic files
   if any(skip in abs_path.lower() for skip in ['.git', '.env', 'venv', '__pycache__']):
       continue
   ```

3. API Key Handling:
   ```python
   if not os.environ.get('ANTHROPIC_API_KEY'):
       raise RuntimeError("ANTHROPIC_API_KEY not found in environment variables")
   ```

## Development Workflow

1. Feature Addition:
   - Add tests first
   - Implement feature
   - Update documentation
   - Run test suite
   - Commit with descriptive message

2. Bug Fixes:
   - Create reproduction test
   - Fix issue
   - Verify fix with test
   - Update documentation if needed

3. Code Style:
   - Follow PEP 8
   - Use type hints
   - Add docstrings
   - Keep methods focused and small

## Deployment

1. Build Process:
   ```bash
   # Install dependencies
   pip install -r requirements.txt

   # Run tests
   python -m unittest discover

   # Start application
   python llm_gui.py
   ```

2. Distribution:
   - Package with PyInstaller if needed
   - Include all necessary files
   - Test on target platforms

## Maintenance

1. Regular Tasks:
   - Update dependencies
   - Check for API changes
   - Run test suite
   - Review error logs

2. Code Updates:
   - Keep API keys secure
   - Monitor console output
   - Check git integration
   - Update documentation

## Future Improvements

1. Planned Features:
   - Multiple LLM support
   - Custom prompt templates
   - Enhanced file diff view
   - Automated testing

2. Technical Debt:
   - Refactor console capture
   - Improve error handling
   - Add more unit tests
   - Enhance documentation

## Support

For issues and questions:
1. Check existing documentation
2. Run test suite
3. Check console output
4. Review git history
5. Contact maintainers

## Version History

- v0.1.0: Initial release
  - Basic GUI implementation
  - Aider integration
  - File management
  - Console capture

## License

This project is licensed under the MIT License - see the LICENSE file for details.
