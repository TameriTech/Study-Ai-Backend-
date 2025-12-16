# debug_imports.py
import sys
import os

print("=== DEBUG INFO ===")
print(f"Python executable: {sys.executable}")
print(f"VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV')}")
print(f"PATH: {os.environ.get('PATH')[:200]}...")
print(f"sys.path (first 5):")
for p in sys.path[:5]:
    print(f"  {p}")

print("\n=== Testing imports ===")
try:
    import pydantic
    print(f"pydantic location: {pydantic.__file__}")
    print(f"pydantic version: {pydantic.__version__}")
except ImportError as e:
    print(f"Error importing pydantic: {e}")
except AttributeError:
    print("pydantic imported, but no __version__ attribute")

try:
    from pydantic_settings import BaseSettings
    print("✓ pydantic_settings import successful")
except ImportError as e:
    print(f"✗ pydantic_settings import failed: {e}")