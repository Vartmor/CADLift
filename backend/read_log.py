
try:
    with open('uvicorn-log.txt', 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    found = False
    for i, line in enumerate(lines):
        if "GEO_STEP_GENERATION_FAILED" in line or "SolidPythonError" in line:
            print(f"--- MATCH at line {i} ---")
            # Print 5 lines before and 20 after
            start = max(0, i - 5)
            end = min(len(lines), i + 20)
            print("".join(lines[start:end]))
            found = True
            
    if not found:
        print("Error string not found in log.")
            
except Exception as e:
    print(f"Error reading log: {e}")
