# Test Guide: Gemini ADK vs Native SDK

This guide provides step-by-step instructions to install, configure, and run the performance benchmark comparing the Google Agent Development Kit (ADK) and the raw Google Gen AI Native SDK.

## Prerequisites
*   **Python 3.10 or higher**
*   **`uv`**: A fast Python package manager (recommended).
*   **Google Cloud SDK**: For authentication.

---

## 1. Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/do-priyambodo/do-adk.git
    cd do-adk
    ```
2.  **Create a virtual environment**:
    ```bash
    uv venv .venv
    source .venv/bin/activate
    ```
3.  **Install dependencies**:
    ```bash
    # Install client dependencies
    uv pip install -r perf_test/client/requirements.txt
    
    # Install server dependencies (FastAPI and ADK)
    uv pip install google-adk fastapi uvicorn httpx
    ```

---

## 2. Environment Setup

1.  Create a file named `env.local` in the **project root** directory.
2.  Add your Google Cloud credentials and configuration:
    ```env
    PROJECT_ID=your-gcp-project-id
    GCP_REGION=us-central1
    ```
3.  **CRITICAL PATH FIX**: The script `perf_test/client/benchmark.py` currently uses a hardcoded absolute path for `env.local` on line 8. 
    *   Open `perf_test/client/benchmark.py`.
    *   Change line 8 to use a relative path or point to your actual file:
        ```python
        import os
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "env.local")
        ```

---

## 3. Running the Server

1.  Open a new terminal window.
2.  Navigate to the server folder:
    ```bash
    cd perf_test/server
    ```
3.  Start the local server:
    ```bash
    ./startlocalserver.sh
    ```
    The server will start on `http://127.0.0.1:8001`.

---

## 4. Running the Benchmark

1.  Open another terminal window.
2.  Navigate to the client folder:
    ```bash
    cd perf_test/client
    ```

### Option A: Run a Single Test
To run a single iteration of all scenarios and see the summary in the terminal:
```bash
./startlocalclient.sh
```

### Option B: Run 10x Benchmark (Averages)
To run the automated 10-iteration benchmark and save results to a file:
```bash
python3 benchmark10x.py | tee result10x-lite.txt
```
This will calculate averages and generate a summary table, saved in `result10x-lite.txt`.

---

## 5. Viewing Results
The master report is located in `README.md` at the project root. You can read the raw data of your runs in the text files generated in the `client` folder.
