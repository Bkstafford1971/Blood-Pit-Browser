import requests
import re
import webbrowser
import sys

# Config
MANAGER_ID = "93"
ROSTER_URL = "https://bloodpit.net/reports/roster.php"
NEWS_URL = "https://bloodpit.net/reports/news.php"

def get_data():
    print(f"--- Gathering intel for Manager {MANAGER_ID} ---")
    try:
        roster_response = requests.get(ROSTER_URL)
        news_response = requests.get(NEWS_URL)
        roster_text = roster_response.text
        news_text = news_response.text
    except Exception as e:
        print(f"Error connecting to Blood Pit: {e}")
        return []

    # 1. Find the Roster Section for Manager 93
    # Using 'fr' (Raw-Formatted) to fix syntax warnings
    # Using a more flexible regex to find the manager block
    pattern = fr"MANAGER:.*?\(({MANAGER_ID})\)"
    sections = re.split(r"MANAGER:", roster_text)
    
    manager_block = ""
    for sec in sections:
        if f"({MANAGER_ID})" in sec:
            manager_block = sec
            break

    if not manager_block:
        print(f"CRITICAL ERROR: Could not find Manager {MANAGER_ID} on the roster page.")
        print("The page format may have changed or the ID is missing.")
        return []

    # Extract warrior names: Looking for names followed by (ID)
    # Most Blood Pit names are uppercase
    warriors = re.findall(r"([A-Z\s]{3,})\s+\(\d+\)", manager_block)
    # Remove duplicates and clean whitespace
    warriors = list(set([w.strip() for w in warriors if w.strip()]))
    
    print(f"Found {len(warriors)} warriors in your warband.")
    
    results_list = []

    # 2. Match Warriors to Newsletter Fights
    for name in warriors:
        # Search for name in the newsletter
        # Regex looks for the name followed by their ID and record
        fight_pattern = fr"{re.escape(name)}.*"
        match = re.search(fight_pattern, news_text, re.IGNORECASE)
        
        if match:
            line = match.group(0)
            # Standard fight line detection
            # If 'SLAIN' or 'KILLED' appears in the line, mark it
            result = "WIN" # Default
            if "SLAIN" in line.upper(): result = "SLAIN"
            elif "LOSS" in line.upper(): result = "LOSS"
            
            results_list.append({
                "name": name, 
                "result": result, 
                "line": line[:80] + "..." # Snippet of the fight
            })
        else:
            results_list.append({"name": name, "result": "NO FIGHT", "line": "Resting in the barracks"})

    return results_list

def create_report(results):
    if not results:
        print("No results to display.")
        return

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ilneval Arena Report</title>
        <style>
            body {{ background: #1a1a1a; color: #f4e4c1; font-family: 'Segoe UI', serif; padding: 40px; }}
            .card {{ background: #2a2a2a; border-left: 5px solid #8B0000; padding: 15px; margin-bottom: 10px; border-radius: 4px; }}
            .WIN {{ color: #44ff44; font-weight: bold; }}
            .LOSS {{ color: #ff4444; font-weight: bold; }}
            .SLAIN {{ background: #8B0000; color: white; padding: 2px 5px; }}
            .warrior-name {{ font-size: 1.2em; color: #FFD700; }}
        </style>
    </head>
    <body>
        <h1>Warriors of Ilneval - Turn Report</h1>
        <div id="results">
            {"".join([f'<div class="card"><span class="warrior-name">{r["name"]}</span> - <span class="{r["result"]}">{r["result"]}</span><br><small>{r["line"]}</small></div>' for r in results])}
        </div>
    </body>
    </html>
    """
    
    with open("Bloodpit_Auto.html", "w", encoding="utf-8") as f:
        f.write(html_template)
    
    print("Report generated! Opening now...")
    webbrowser.open("Bloodpit_Auto.html")

if __name__ == "__main__":
    data = get_data()
    create_report(data)