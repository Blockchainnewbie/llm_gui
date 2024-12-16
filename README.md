# LLM GUI
A Universal GUI for Multiple AI Provider SDKs

## Current Features
- Multi-provider support (OpenAI, Anthropic, Mistral, Google, OpenRouter)
- Dynamic model selection for each provider
- Secure API key management with system environment variables
- User-friendly interface with input/output text areas
- Automatic model list updates
- Error handling and user feedback
- Environment variable persistence
- Conversation History Management:
  - Automatic saving of conversations with timestamps
  - Load and review previous conversations
  - Messages displayed with timestamps
  - JSON-based storage for easy backup
  - File menu for conversation management
- Export Functionality:
  - Export conversations to TXT and PDF formats
  - Professional PDF formatting with proper fonts
  - Timestamps and role labels in exports
  - Automatic file naming and organization
  - Dedicated exports directory
- Aider AI Integration:
  - Direct integration with Aider for code editing
  - Multi-file selection support
  - Custom edit instructions
  - Real-time feedback on changes
  - Support for multiple AI models
  - Accessible via Tools menu

## Planned Features and Improvements

### Conversation Management
✅ Save chat history with timestamps (Implemented!)
✅ Load previous conversations (Implemented!)
✅ Export conversations to PDF/TXT (Implemented!)
✅ Aider AI Integration (Implemented!)
- Search through past conversations

### Aider Integration Improvements
- Git commit history viewer
- Custom model configuration
- Edit preview before applying
- Syntax highlighting in edit dialog
- Undo/Redo support for edits

### UI Enhancements
- Dark/Light theme toggle
- Resizable/Detachable windows
- Syntax highlighting for code responses
- Markdown rendering for formatted responses
- Progress bar during API calls
- Character/token counter for prompts

### Advanced Features
- Temperature/Top-P parameter controls
- System prompt templates
- Batch processing of prompts
- File upload support for context
- Code execution sandbox for Python responses
- Split screen for multiple conversations

### Productivity Tools
- Prompt templates library
- Quick-access favorite prompts
- Keyboard shortcuts for common actions
- Auto-complete for prompts
- Custom model parameter presets

### Integration Features
- Image generation support (DALL-E, Stable Diffusion)
- Text-to-Speech for responses
- Speech-to-Text for input
- Direct code snippet copying
- Export to various formats (Markdown, JSON)

### Advanced Settings
- Proxy configuration
- API usage tracking/limits
- Cost estimation before requests
- Response streaming option
- Auto-retry on failure

### Collaboration Features
- Share conversations via link
- Export/Import conversation settings
- Team shared prompt templates
- Multi-user support

### Development Tools
- API response debugging view
- Request/Response logging
- Performance metrics
- Token usage analytics
- API error explanations

### Content Management
- Conversation folders/categories
- Tags for conversations
- Favorites system
- Bulk export/import
- Auto-backup feature

### Smart Features
- Context memory across conversations
- Auto-suggest better prompts
- Similar conversation finder
- Response quality scoring
- Automatic language detection

### Security Features
- API key encryption
- Secure storage for sensitive prompts
- Session timeout options
- Access logging
- Data export controls

### Customization
- Custom API endpoints
- User-defined model lists
- Interface layout customization
- Custom response parsing
- Personalized shortcuts

## Aider Integration Guide

### Overview
The Aider integration allows you to edit code directly using AI assistance. It supports:
- Multiple file editing in a single session
- Various AI models (GPT-4, Claude, etc.)
- Automatic API key management
- Git integration for version control
- Real-time code updates

### Setup
1. API Key Configuration:
   - The system automatically checks for API keys in the following order:
     1. OPENAI_API_KEY
     2. ANTHROPIC_API_KEY
     3. GOOGLE_API_KEY
     4. MISTRAL_API_KEY
     5. OPENROUTER_API_KEY
   - Keys are securely stored in Windows Registry
   - First available key will be used for Aider integration

### Using Aider for Code Editing

#### Basic Usage
1. Access Aider:
   - Click Tools -> Code Edit with Aider
   - Or use shortcut (if configured)

2. Select Files:
   - Click "Add Files" button
   - Select one or multiple Python files
   - Files appear in the selection list
   - Click "Remove" to unselect files

3. Edit Instructions:
   - Enter clear, specific instructions
   - Examples:
     - "Add error handling to the process_data function"
     - "Implement a new method for user authentication"
     - "Fix the bug in the file parsing logic"

4. Process Edits:
   - Click "Process Edit"
   - Aider will analyze files and make changes
   - Changes are applied automatically
   - Review success/error messages

#### Advanced Features

1. Multi-File Edits:
   - Select multiple related files
   - Aider understands cross-file dependencies
   - Makes consistent changes across files

2. Code Analysis:
   - Aider analyzes code context
   - Understands project structure
   - Maintains code style consistency

3. Error Handling:
   - Validates changes before applying
   - Provides detailed error messages
   - Suggests fixes for common issues

4. Best Practices:
   - Be specific in edit instructions
   - Review changes in related files
   - Test code after significant changes
   - Use version control for safety

### Tips for Effective Use

1. Writing Good Instructions:
   ```
   DO:
   - "Add input validation to the user_input function"
   - "Implement error handling for database connections"
   - "Refactor the authentication logic to use JWT"

   DON'T:
   - "Fix the code"
   - "Make it better"
   - "Add some features"
   ```

2. Code Context:
   - Include relevant files in selection
   - Mention specific functions/classes
   - Provide example inputs/outputs

3. Troubleshooting:
   - Check API key configuration
   - Verify file permissions
   - Review error messages
   - Ensure files are saved

### Supported Models

1. Primary Models:
   - GPT-4 (Recommended)
   - GPT-3.5-Turbo
   - Claude-2
   - Google PaLM
   - Mistral Large

2. Model Selection:
   - Automatically uses best available model
   - Falls back to alternative if primary unavailable
   - Configurable through API keys

### Security Considerations

1. API Key Management:
   - Keys stored in Windows Registry
   - Never exposed in code or logs
   - Automatic key rotation support

2. Code Safety:
   - Changes validated before applying
   - No execution of unknown code
   - Local file system access only

### Limitations

1. Current Limitations:
   - Windows-only registry support
   - Python files primarily supported
   - Single edit session at a time

2. Known Issues:
   - Prompt toolkit warning in GUI (non-critical)
   - May require cmd.exe for some features

### Future Improvements

1. Planned Features:
   - Git integration improvements
   - Multi-language support
   - Custom model configurations
   - Edit preview functionality
   - Syntax highlighting
   - Undo/Redo support

## Usage

### Using Aider Integration
1. Access via Tools -> Code Edit with Aider
2. Select files to edit:
   - Click "Add Files" button
   - Choose one or multiple Python files
   - Selected files appear in the list
3. Enter edit instructions:
   - Provide clear instructions in the text area
   - Be specific about desired changes
4. Process the edit:
   - Click "Process Edit"
   - Review success/error messages
   - Changes are applied automatically

### Models
The following models are supported for code editing:
- GPT-4 (recommended)
- GPT-3.5-Turbo
- GPT-4-32k

## Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/llm_gui.git

# Navigate to the directory
cd llm_gui

# Install required packages
pip install -r requirements.txt
```

## Usage
1. Run the application:
```bash
python llm_gui_V0.02.py
```

2. Enter your API keys for the providers you want to use
3. Select a provider from the dropdown
4. Choose a model
5. Enter your prompt and click "Send"

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
