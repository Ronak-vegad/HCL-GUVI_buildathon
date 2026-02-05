from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")
expected = "alterEgo12345hCiGUvi_Buildathon"

print(f"Loaded: {repr(api_key)}")
print(f"Expected: {repr(expected)}")
print(f"Match: {api_key == expected}")
print(f"Loaded length: {len(api_key) if api_key else 0}")
print(f"Expected length: {len(expected)}")

if api_key != expected:
    print("\nDifference found:")
    for i, (c1, c2) in enumerate(zip(api_key or "", expected)):
        if c1 != c2:
            print(f"  Position {i}: got {repr(c1)} expected {repr(c2)}")
