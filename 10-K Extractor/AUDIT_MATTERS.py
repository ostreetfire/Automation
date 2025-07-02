import json

def display_critical_audit_matters(file_path=r'C:\Users\OscarStrieter\OneDrive - Province LLC\Desktop\O. Strieter\15. Code\SEC Filing Extractor\10-K Extractor\extraction.json'):
    """
    Loads and displays the Critical Audit Matters section from the specified JSON file.
    """
    print("--- Critical Audit Matters ---")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        audit_matters = data.get('data', {}).get('CriticalAuditMatters', [])
        
        if not audit_matters:
            print("No Critical Audit Matters found.")
            return
            
        # Iterate through each item and print its details
        for i, matter in enumerate(audit_matters, 1):
            title = matter.get("MatterTtile", "N/A") # Note: "MatterTtile" may be a typo in the source JSON
            description = matter.get("MatterDescription", "No description available.")
            
            print(f"\n## {i}. {title} ##")
            print(description)

    except FileNotFoundError:
        print(f"Error: The file at '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' contains invalid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Run the function
if __name__ == "__main__":
    display_critical_audit_matters()