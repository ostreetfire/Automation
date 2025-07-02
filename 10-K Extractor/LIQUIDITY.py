import json

def display_liquidity(file_path=r'C:\Users\OscarStrieter\OneDrive - Province LLC\Desktop\O. Strieter\15. Code\SEC Filing Extractor\10-K Extractor\extraction.json'):
    """
    Loads and displays the general Liquidity section from the JSON file.
    """
    print("--- Liquidity Information ---")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        liquidity = data.get('data', {}).get('Liquidity', {})
        
        if not liquidity:
            print("No Liquidity information found.")
            return

        print("\n## Management's Liquidity Assessment ##")
        print(liquidity.get('assessmentSummary', 'N/A'))

        print("\n## Key Metrics ##")
        print(f"  - Operating Cash Flow: {liquidity.get('operatingCashFlow', 'N/A')}")
        print(f"  - Working Capital: {liquidity.get('workingCapital', 'N/A')}")
        print(f"  - Current Ratio: {liquidity.get('currentRatio', 'N/A')}")

        print("\n## Credit Facilities ##")
        print(liquidity.get('creditFacilities', 'N/A'))

        # Handle the nested capitalExpenditures object
        capex = liquidity.get('capitalExpenditures', {})
        print("\n## Capital Expenditures ##")
        print(f"  - Amount: {capex.get('amount', 'N/A')}")
        print(f"  - Notes: {capex.get('notes', 'N/A')}")
        print(f"  - Expectations: {capex.get('expectations', 'N/A')}")

    except FileNotFoundError:
        print(f"Error: The file at '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' contains invalid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    display_liquidity()