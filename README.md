# PostgreSQL NLP CLI

A powerful command-line interface that combines PostgreSQL database interaction with Natural Language Processing, allowing users to query databases using natural language. The CLI translates English queries into SQL using local LLMs through Ollama, with support for example-based learning.

## Features

- 🤖 Natural Language to SQL translation using local LLMs (Ollama)
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
- **Ollama** - Local LLM service
- **Key Libraries**:
  - `psycopg2-binary` - PostgreSQL adapter
  - `python-dotenv` - Environment management
  - `rich` - Terminal formatting
  - `prompt-toolkit` - Interactive CLI
  - `typer` - CLI framework
  - `requests` - HTTP client for Ollama API
  - `sqlparse` - SQL formatting

## Prerequisites

1. **Python 3.8 or higher**
2. **PostgreSQL** installed and running
3. **Ollama** installed with Gemma 2B model
   ```bash
   ollama run gemma:2b
   ```

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

4. Create a `.env` file:
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_database
   DB_USER=your_username
   DB_PASSWORD=your_password
   OLLAMA_URL=http://localhost:11434
   ```

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

## Project Structure

```
.
├── .env
├── .gitignore
├── examples.gist
├── requirements.txt
├── README.md
└── src/
    ├── __init__.py
    ├── config.py     # Configuration management
    ├── database.py   # Database operations
    ├── history.py    # Query history handling
    ├── nlp.py        # NLP processing
    ├── cli.py        # CLI interface
    └── main.py       # Entry point
```

## Contributing

Contributions are welcome! Here are some ways you can contribute:

1. Report bugs and issues
2. Improve documentation
3. Add new features
4. Enhance NLP capabilities
5. Add more example queries
6. Optimize SQL generation


### Areas for Improvement

- Additional LLM model support
- Query optimization suggestions
- Schema relationship detection
- Enhanced example matching
- Support for more complex queries
- Query caching
- Additional database support

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Ollama team for the local LLM capability
- PostgreSQL community
- All contributors and users

---

For questions and support, please open an issue in the GitHub repository.