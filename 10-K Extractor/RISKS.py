import json
from collections import defaultdict

def display_grouped_risks(file_path=r'C:\Users\OscarStrieter\OneDrive - Province LLC\Desktop\O. Strieter\15. Code\SEC Filing Extractor\10-K Extractor\extraction.json'):
    """
    Loads key risks from a JSON file, groups them by category,
    and prints them in an organized format.
    """
    print("--- Key Risks ---")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        key_risks = data.get('data', {}).get('keyRisks', [])
        
        if not key_risks:
            print("No Key Risks information found.")
            return
            
        # Use defaultdict to easily group risks by category
        grouped_risks = defaultdict(list)
        for risk in key_risks:
            category = risk.get("category", "Uncategorized")
            grouped_risks[category].append(risk)
            
        # Iterate through the grouped dictionary and print the risks
        for category, risks in grouped_risks.items():
            print(f"\n\n## {category} ##")
            print("-" * (len(category) + 14)) # Decorative separator
            
            for risk in risks:
                title = risk.get("title", "N/A")
                description = risk.get("description", "No description available.")
                impact = risk.get("potentialImpact", "No potential impact specified.")
                
                print(f"\n- {title}")
                print(f"  Description: {description}")
                print(f"  Potential Impact: {impact}")

    except FileNotFoundError:
        print(f"Error: The file at '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' contains invalid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Run the function
if __name__ == "__main__":
    display_grouped_risks()