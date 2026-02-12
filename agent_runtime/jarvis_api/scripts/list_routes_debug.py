import sys
import os
sys.path.append("/app")
from main import app

print("Registered Routes:")
for route in app.routes:
    print(f"{route.path} [{route.methods}]")
