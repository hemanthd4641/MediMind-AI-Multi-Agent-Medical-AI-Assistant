import subprocess
import sys
import os
import signal
import time

def main():
    print("Starting MediMind AI...")

    # Define the backend command
    # Assuming we're in the root directory and 'backend' is a python module
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    
    # Define the frontend command
    # We use shell=True on Windows for npm
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    frontend_cmd = "npm run dev"

    print("Starting Backend (FastAPI)...")
    backend_process = subprocess.Popen(backend_cmd)

    print("Starting Frontend (Vite)...")
    frontend_process = subprocess.Popen(
        frontend_cmd,
        cwd=frontend_dir,
        shell=True
    )

    def signal_handler(sig, frame):
        print("\nShutting down MediMind AI...")
        # Kill backend
        if backend_process.poll() is None:
            backend_process.terminate()
        # Kill frontend (Since shell=True is used, this might only kill the shell, but it's a best effort)
        if frontend_process.poll() is None:
            frontend_process.terminate()
        
        sys.exit(0)

    # Register the signal handler for graceful shutdown on Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("\n=======================================================")
    print("MediMind AI is running!")
    print("Backend API: http://localhost:8000")
    print("Frontend UI: http://localhost:5173 (default Vite port)")
    print("Press Ctrl+C to stop all services.")
    print("=======================================================\n")

    try:
        # Wait for both processes to complete (they usually run indefinitely)
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()
