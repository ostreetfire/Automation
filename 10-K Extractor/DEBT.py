import json

def display_debt_info(file_path=r'C:\Users\OscarStrieter\OneDrive - Province LLC\Desktop\O. Strieter\15. Code\SEC Filing Extractor\10-K Extractor\extraction.json'):
    """
    Loads and displays the Debt section from the specified JSON file.
    """
    print("--- Debt Information ---")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        debt_items = data.get('data', {}).get('Debt', [])
        
        if not debt_items:
            print("No Debt information found.")
            return
            
        # Iterate through each item in the Debt list and print its details
        for i, item in enumerate(debt_items, 1):
            category = item.get("DebtOrFacilityCategory", "N/A")
            discussion = item.get("Discussion", "No discussion available.")
            
            print(f"\n## {i}. {category} ##")
            print(discussion)
            
    except FileNotFoundError:
        print(f"Error: The file at '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' contains invalid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Run the function
if __name__ == "__main__":
    display_debt_info()