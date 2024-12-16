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

## Planned Features and Improvements

### Conversation Management
✅ Save chat history with timestamps (Implemented!)
✅ Load previous conversations (Implemented!)
- Export conversations to PDF/TXT
- Search through past conversations

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
