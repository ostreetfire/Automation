import json

def display_company_overview(file_path=r'C:\Users\OscarStrieter\OneDrive - Province LLC\Desktop\O. Strieter\15. Code\SEC Filing Extractor\10-K Extractor\extraction.json'):
    """
    Loads and displays the Company Profile and key filing info from the JSON file.
    """
    print("--- Company Overview ---")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Get the relevant data objects, defaulting to an empty dict if not found
        profile = data.get('data', {}).get('companyProfile', {})
        filing = data.get('data', {}).get('filingInfo', {})
        
        if not profile:
            print("No Company Profile information found.")
            return
        
        # --- Print the Overview ---
        print(f"\n## {profile.get('name', 'N/A')} ({profile.get('ticker', 'N/A')}) ##")
        print(f"Reporting Period End: {filing.get('reportingPeriodEnd', 'N/A')}")
        print("-" * 30)
        
        print("\n**Business Description:**")
        print(profile.get('businessDescription', 'N/A'))
        
        print("\n**Key Information:**")
        print(f"  - Industry / Sector: {profile.get('industry', 'N/A')} / {profile.get('sector', 'N/A')}")
        print(f"  - Location: {profile.get('location', 'N/A')}")
        print(f"  - Employees: {profile.get('employeeCount', 'N/A')}")
        print(f"  - Auditor: {profile.get('auditor', 'N/A')}")

    except FileNotFoundError:
        print(f"Error: The file at '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' contains invalid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Run the function
if __name__ == "__main__":
    display_company_overview()