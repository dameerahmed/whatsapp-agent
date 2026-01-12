# What Agent - WhatsApp Bot Assistant

An intelligent WhatsApp bot powered by AI agents that can send messages, interact with users, and execute commands through Groq's LLM API.

## 📋 Project Overview

**What Agent** is a FastAPI-based WhatsApp chatbot system that integrates with:
- **Groq API** for fast LLM processing (OpenAI-compatible endpoints)
- **WhatsApp Business API** for message delivery
- **AI Agents Framework** for intelligent task execution
- **Function Tools** for mass messaging and automation

### Key Features
- ✅ Send WhatsApp messages to multiple recipients
- ✅ AI-powered message generation and responses
- ✅ Webhook integration for incoming messages
- ✅ Personalized message templates
- ✅ Boss confirmation workflow for security
- ✅ Real-time message timestamps and formatting

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend Framework** | FastAPI |
| **LLM Provider** | Groq API (GPT-OSS-120B) |
| **Web Server** | Uvicorn |
| **Agent Framework** | OpenAI Agents |
| **Client Library** | httpx, OpenAI Python SDK |
| **Configuration** | python-dotenv |
| **Python Version** | 3.11+ |

---

## 📦 Dependencies

Core dependencies listed in `pyproject.toml`:
- `fastapi>=0.125.0` - Web framework
- `uvicorn>=0.38.0` - ASGI server
- `openai>=2.14.0` - OpenAI API client
- `openai-agents>=0.6.4` - Agent framework
- `python-dotenv>=1.2.1` - Environment variables
- `requests>=2.32.5` - HTTP requests
- `gradio>=6.1.0` - UI interface
- `pydantic-ai>=1.39.0` - AI data validation

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Groq API Key
- WhatsApp Business API credentials
- WhatsApp Business Account

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd what_agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   Or with Poetry:
   ```bash
   poetry install
   ```

3. **Setup environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
   WHATSAPP_VERIFY_TOKEN=your_verify_token
   BOSS_PHONE=your_boss_phone_number
   PHONE_NUMBER_ID=your_phone_number_id
   ```

4. **Run the application**
   ```bash
   python main.py
   ```
   Or with Uvicorn directly:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

---

## 📡 API Endpoints

### Webhook Verification
- **GET** `/webhook`
  - Verifies WhatsApp webhook subscription
  - Parameters: `hub.verify_token`, `hub.challenge`
  - Returns: Challenge token or 403 Forbidden

### Message Handling
- **POST** `/webhook` (expected)
  - Receives incoming WhatsApp messages
  - Processes with AI agents
  - Sends intelligent responses

---

## 🛠️ Main Components

### `main.py`
The main application file containing:

#### Groq LLM Setup
```python
client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)
model = OpenAIChatCompletionsModel(
    model="openai/gpt-oss-120b",
    openai_client=client,
)
```

#### `send_mass_messages()` Function Tool
Sends WhatsApp messages to multiple recipients with:
- **Inputs**: Phone numbers, message text, recipient names
- **Features**: 
  - Supports multiple recipients (comma-separated)
  - Personalized message formatting
  - Timestamp and date inclusion
  - Boss-level formatted templates
- **Safety**: Only sends to explicitly specified contacts (never to BOSS_PHONE)

---

## 🔐 Security & Configuration

### Environment Variables
- `GROQ_API_KEY` - API key for Groq LLM service
- `ACCESS_TOKEN` - WhatsApp Business API access token
- `PHONE_NUMBER_ID` - WhatsApp Business phone number ID
- `VERIFY_TOKEN` - Webhook verification token
- `BOSS_PHONE` - Administrator phone number (protected from mass messages)

### Rules
- Boss confirmation required before sending messages
- Messages never sent to BOSS_PHONE without explicit permission
- Webhook token verification for security
- Tracing disabled in production (`AGENTS_TRACING_ENABLED=false`)

---

## 📝 Usage Examples

### Sending Mass Messages
The bot can be instructed to send messages like:
```
Send "Hello, this is a promotional message!" to +92XXXXXXXXXX, +92XXXXXXXXXX
```

### Message Format
Messages are automatically formatted with:
- Sender identification ("MESSAGE FROM BOSS")
- Recipient name (personalized)
- Message content
- Timestamp (DD-MM-YYYY, HH:MM AM/PM format)
- Professional separator lines

---

## 🔄 Workflow

1. **Message Received** → WhatsApp API sends webhook
2. **Verification** → Token validation via GET /webhook
3. **Processing** → AI agent processes the request
4. **Execution** → Function tools execute actions (send messages)
5. **Response** → Bot sends confirmation/result to Boss

---

## ⚙️ Configuration Files

### `pyproject.toml`
- Project metadata (name, version, description)
- Python version requirement (>=3.11)
- All package dependencies listed
- Compatible with Poetry or pip

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `GROQ_API_KEY not found` | Ensure `.env` file exists with valid key |
| `Connection refused on localhost` | Check if Uvicorn server is running |
| `Webhook verification fails` | Verify VERIFY_TOKEN matches WhatsApp settings |
| `Messages not sending` | Confirm ACCESS_TOKEN and PHONE_NUMBER_ID are valid |

---

## 📚 Additional Resources

- [Groq API Documentation](https://groq.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started)
- [OpenAI Agents Framework](https://github.com/openai/swarm)

---

## 📄 License

[Add your license here]

---

## 👤 Author

**Boss's Elite Assistant** - WhatsApp Bot Management System

---

## 📞 Support

For issues or questions, contact the development team through WhatsApp or create an issue in the repository.

---

**Last Updated:** January 2026