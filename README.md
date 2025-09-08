# PostgreSQL NLP CLI

A powerful command-line interface that combines PostgreSQL database interaction with Natural Language Processing, allowing users to query databases using natural language. The CLI translates English queries into SQL using configurable LLM providers (local LLMs through Ollama or cloud APIs via OpenRouter), with support for example-based learning.

## Features

- 🤖 Natural Language to SQL translation using configurable LLM providers
- 🌐 Support for multiple LLM providers (Ollama, OpenRouter)
- 📚 Example-based learning from `.gist` files
- 🔍 Interactive CLI with command history
- 💾 Persistent query history
- 🎨 Beautiful console output with syntax highlighting
- 🔒 Secure credential management through environment variables
- 📊 Formatted query results in tables
- ⚡ Support for both SQL and natural language queries

## Technology Stack

- **Python 3.8+**
- **PostgreSQL** - Database
- **LLM Providers**:
  - **Ollama** - Local LLM service
  - **OpenRouter** - Cloud-based LLM API service
- **Key Libraries**:
  - `psycopg2-binary` - PostgreSQL adapter
  - `python-dotenv` - Environment management
  - `rich` - Terminal formatting
  - `prompt-toolkit` - Interactive CLI
  - `typer` - CLI framework
  - `requests` - HTTP client for API calls
  - `sqlparse` - SQL formatting

## Prerequisites

1. **Python 3.8 or higher**
2. **PostgreSQL** installed and running
3. **LLM Provider** (choose one):
   - **Ollama** (for local processing): Install and run with Gemma 2B model
     ```bash
     ollama run gemma:2b
     ```
   - **OpenRouter** (for cloud-based processing): Get API key from [OpenRouter](https://openrouter.ai/)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/sina-mobarez/query-assistant.git
   cd query-assistant
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file (see Configuration section below)

## Configuration

Create a `.env` file in the project root with the following variables:

### Basic Database Configuration
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

### LLM Provider Configuration

#### Option 1: Using Ollama (Local LLM)
```env
LLM_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=gemma:2b
```

#### Option 2: Using OpenRouter (Cloud API)
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
```

### Supported OpenRouter Models
- `meta-llama/llama-3.1-8b-instruct:free` (Free)
- `openai/gpt-4o-mini` (Paid)
- `anthropic/claude-3-haiku` (Paid)
- `google/gemini-pro` (Paid)
- And many more available on [OpenRouter](https://openrouter.ai/models)

## Query Examples

Create an `examples.gist` file in the project root to help the model generate better SQL queries:

(there is a examples file that use for DVDRental database.)

```sql
-- Show me actor's first_name, last_name that have Nick, Ed and Jennifer as their firstnames.
SELECT first_name, 
       last_name
FROM actor
WHERE first_name IN ('Nick','Ed', 'Jennifer');

-- List all actors sorted by last name
SELECT first_name, last_name
FROM actor
ORDER BY last_name ASC;
```

## Usage

1. Start the CLI:
   ```bash
   python -m src.main
   ```

2. Use natural language queries by prefixing with `?`:
   ```sql
    > ?show me the top 10 customers by total purchase amount
   ```

3. Or use direct SQL:
   ```sql
    > SELECT * FROM customers LIMIT 10;
   ```

4. Special Commands:
   - `\q` - Quit
   - `\h` - Show query history
   - `\c` - Clear screen

## LLM Provider Comparison

| Feature | Ollama | OpenRouter |
|---------|--------|------------|
| **Cost** | Free (local compute) | Pay-per-use |
| **Privacy** | Complete privacy | Data sent to third parties |
| **Speed** | Depends on local hardware | Generally faster |
| **Model Selection** | Limited to locally installed | 100+ models available |
| **Internet Required** | No | Yes |
| **Setup Complexity** | Requires local installation | Simple API key setup |

## Project Structure

```
.
├── .env
├── .env.example
├── .gitignore
├── examples.gist
├── requirements.txt
├── README.md
└── src/
    ├── __init__.py
    ├── config.py     # Configuration management
    ├── database.py   # Database operations
    ├── history.py    # Query history handling
    ├── nlp.py        # NLP processing with multiple providers
    ├── cli.py        # CLI interface
    └── main.py       # Entry point
```

## Contributing

Contributions are welcome! Here are some ways you can contribute:

1. Report bugs and issues
2. Improve documentation
3. Add new features
4. Enhance NLP capabilities
5. Add more LLM provider integrations
6. Add more example queries
7. Optimize SQL generation

### Areas for Improvement

- Additional LLM provider support (Azure OpenAI, AWS Bedrock, etc.)
- Query optimization suggestions
- Schema relationship detection
- Enhanced example matching
- Support for more complex queries
- Query caching
- Additional database support
- Streaming responses for better UX

## Troubleshooting

### Common Issues

1. **OpenRouter API Key Issues**
   - Ensure your API key is correctly set in the `.env` file
   - Check your OpenRouter account has sufficient credits
   - Verify the model name is correct

2. **Ollama Connection Issues**
   - Make sure Ollama is running: `ollama serve`
   - Verify the model is installed: `ollama list`
   - Check the OLLAMA_URL in your `.env` file

3. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check database credentials in `.env` file
   - Ensure the database exists and is accessible

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Ollama team for the local LLM capability
- OpenRouter for providing access to multiple LLM APIs
- PostgreSQL community
- All contributors and users

---

For questions and support, please open an issue in the GitHub repository.