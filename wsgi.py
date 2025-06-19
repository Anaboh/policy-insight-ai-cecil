import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Debug: Print Python version and paths
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

try:
    from src.backend.app import app
    print("Successfully imported app from src.backend.app")
except ImportError as e:
    print(f"Import error: {str(e)}")
    raise

if __name__ == "__main__":
    app.run()
