# Docker SDG - Synthetic Data Generator

Web application for generating synthetic data using AI (Google Gemini) based on DDL schemas. Includes two main features:

- **Data Generation**: Creates synthetic data from DDL schemas
- **Chat with your Data**: Interact with generated data using natural language

## 🚀 Local Execution (Development and Debug)

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Steps to run locally

1. **Clone or navigate to the project directory**
   ```bash
   cd docker-SDG
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root (same level as `app.py`):
   
   ```bash
   # Copy the example file
   copy .env.example .env
   
   # Or manually create the .env file with:
   ```
   
   Then edit the `.env` file and configure at least the `GOOGLE_API_KEY`:
   ```env
   GOOGLE_API_KEY=your-api-key-here
   ```
   
   **Note:** 
   - The `.env.example` file contains all available variables with documentation
   - If you don't configure the `.env` file, the application will use default values (except the Gemini API key, which is mandatory)

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

   The application will automatically open in your browser at `http://localhost:8501`

### Run with debug options

To run with more debug information:

```bash
# Verbose mode
streamlit run app.py --logger.level=debug

# Or with custom configuration
streamlit run app.py --server.headless=true
```

### Streamlit configuration (optional)

You can create a `.streamlit/config.toml` file to configure Streamlit:

```toml
[server]
port = 8501
address = "localhost"

[browser]
gatherUsageStats = false
```

## 🐳 Docker Execution

If you prefer to use Docker, the project includes `docker-compose.yml` which configures:

- **Streamlit Application**: Main application service
- **PostgreSQL**: Database for storing synthetic data

### Steps to run with Docker:

```bash
# Build and run (includes the database)
docker-compose up --build

# Or just run (if already built)
docker-compose up

# Run in background
docker-compose up -d
```

### Environment variables in Docker:

The `docker-compose.yml` uses environment variables to configure PostgreSQL and the application. The easiest way is to use a `.env` file:

1. **Copy the example file:**
   ```bash
   # Windows
   copy .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   ```

2. **Edit `.env` and configure your values:**
   - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: To configure PostgreSQL
   - `GOOGLE_API_KEY`: Required for the application to work
   - Other optional variables as needed

3. **Run Docker Compose:**
   ```bash
   docker-compose up --build
   ```

**Important notes:**
- Docker Compose automatically reads the `.env` file in the project root
- If you don't define variables in `.env`, default values from `docker-compose.yml` will be used
- The `DATABASE_URL` is automatically built using the `POSTGRES_*` variables
- The application automatically connects to the PostgreSQL database when running with Docker

## 🐛 Debugging

### Using a debugger (VS Code)

1. **Create `.vscode/launch.json` file**:
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Python: Streamlit",
               "type": "python",
               "request": "launch",
               "module": "streamlit",
               "args": [
                   "run",
                   "app.py",
                   "--server.headless=true"
               ],
               "console": "integratedTerminal",
               "justMyCode": false
           }
       ]
   }
   ```

2. **Set breakpoints** in the code where you need to debug

3. **Press F5** to start the debugger

### Debugging with print statements

You can use `st.write()` or `print()` to debug:

```python
# Anywhere in the code
st.write("Debug info:", variable)
print("Debug:", variable)  # Appears in the console
```

### View Streamlit logs

Logs appear in the terminal where you ran `streamlit run app.py`

## 🔧 Troubleshooting

### Error: "ModuleNotFoundError"
- Make sure you have activated the virtual environment
- Verify that all dependencies are installed: `pip install -r requirements.txt`

### Error: "GOOGLE_API_KEY is not configured"
- Configure the `GOOGLE_API_KEY` environment variable in your `.env` file
- Or verify that the `.streamlit/secrets.toml` file has the key configured
- You can use the `.env.example` file as a reference to see all available variables

### Application doesn't open in browser
- Verify that port 8501 is not in use
- Manually access `http://localhost:8501`

### Code changes are not reflected
- Streamlit reloads automatically, but if it doesn't work:
  - Press `R` in the Streamlit interface to reload
  - Or restart the server with `Ctrl+C` and run again

## 📝 Notes

- The application uses hot-reload, so code changes are automatically reflected
- For development, running locally is faster than using Docker
- Generated data is maintained in `st.session_state` during the session
- You can use example DDL files in the `examples/` folder to test the application
- The `.env.example` file contains all available environment variables with complete documentation
- For Docker, PostgreSQL variables can be configured in the `.env` file (see `.env.example`)

## 🎯 Features

- ✅ Synthetic data generation based on DDL schemas
- ✅ Conversational interface to interact with generated data
- ✅ PostgreSQL support as storage
- ✅ Google Gemini AI integration
- ✅ Layered architecture for easy maintenance
- ✅ Data visualization support
- ✅ Observability with Langfuse Cloud (optional) - tracks all AI operations

## 📊 Observability with Langfuse

The application includes optional integration with [Langfuse Cloud](https://cloud.langfuse.com) for complete observability of all AI operations. Langfuse allows:

- Track synthetic data generation (tables, rows, execution time)
- Monitor generated SQL queries and their results
- Analyze chat conversations with data
- Detect jailbreak attempts and security issues
- Optimize prompts and parameters based on real metrics

**Configuration**: See [SETUP_ENV.md](SETUP_ENV.md) for detailed instructions on how to configure Langfuse Cloud. It's completely optional - the application works perfectly without it.
