**Getting Started**
====================

### Create Conda Environment

Create a new Conda environment for your project:
```bash
conda create --name mgraph python=3.12 pip
```

### Activate Environment

Activate the newly created environment:
```bash
conda activate mgraph
```

### Install Requirements

Install the required dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Additional Steps

1. Add a `.env` file with the following keys:

    ```plaintext
    API_URL=http://localhost:11434/v1/chat/completions
    API_KEY=your_api_key
    MODEL=llama3.1:70b
    VISUAL_CROSSING_API_KEY=your_key
    ```

   - For the weather tool, add a key from visualcrossing.com.

2. Install Ollama and/or set the correct API URL for any OpenAI-compatible LLM server.

   In `main.py`, ensure the `api_url` is set correctly. For example, if your Ollama server is locally installed, the line should look like this:

    ```python
    api_url = "http://localhost:11434/v1/chat/completions"
    ```

### Run the Application

Start the Uvicorn server with the following command:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
This will start the development server, listening on all available network interfaces (`0.0.0.0`) on port `8000`, and automatically reload when changes are detected.

---

**Running the Application with Docker**
=======================================

### Docker Instructions

If you prefer to run the application inside a Docker container, follow these steps:

1. **Create a `.env` file**:
    - Create a `.env` file in the root directory of your project with the following content:

    ```plaintext
    API_URL=http://localhost:11434/v1/chat/completions
    API_KEY=your_api_key
    MODEL=llama3.1:70b
    VISUAL_CROSSING_API_KEY=your_key
    ```

    - Update the values according to your environment.

2. **Build the Docker Image**:
    - Run the following command to build the Docker image:

    ```bash
    docker build -t basic-agent-chat .
    ```

3. **Run the Docker Container**:
    - Run the Docker container using the following command:

    ```bash
    docker run --env-file .env -p 8000:8000 basic-agent-chat --name basic-agent-chat
    ```

    - This command will start the application inside a Docker container, exposing it on port `8000`.

    - If you want to restart always
    ```bash
    docker run --env-file .env -p 8000:8000 --name basic-agent-chat --restart always basic-agent-chat

    ```

### Access the Application

Once the container is running, you can access the application by navigating to `http://localhost:8000` in your web browser.
