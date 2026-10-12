print("Import de numpy...", end=" ", flush=True)
import numpy
print(f"OK (version {numpy.__version__})")

print("Import de pypdf...", end=" ", flush=True)
import pypdf
print("OK")

print("Import de google-genai...", end=" ", flush=True)
from google import genai 
print("OK")

print("Import de chromadb...", end=" ", flush=True)
import chromadb
print("OK")

print("\nTout est installé. On passe à l'étape 2 !")
