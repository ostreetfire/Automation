import json

def display_capital_structure_table(file_path=r'C:\Users\OscarStrieter\OneDrive - Province LLC\Desktop\O. Strieter\15. Code\SEC Filing Extractor\10-K Extractor\extraction.json'):
    """
    Loads capital structure data and prints it as a Markdown table.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        capital_structure = data.get('data', {}).get('CapitalStructure', [])
        if not capital_structure:
            print("No capital structure data found.")
            return

        headers = {
            "FacilityOrSecurityName": "Facility/Security Name",
            "AmountOutstanding": "Amount Outstanding",
            "Maturity": "Maturity",
            "InterestRate": "Interest Rate"
        }
        
        # 1. Print Markdown table header
        header_keys = list(headers.keys())
        header_titles = list(headers.values())
        print(f"| {' | '.join(header_titles)} |")
        
        # 2. Print Markdown separator
        print(f"| {' | '.join(['---'] * len(header_titles))} |")

        # 3. Print each row in Markdown format
        for item in capital_structure:
            row_values = [str(item.get(key, '')).replace('|', '\|') for key in header_keys]
            print(f"| {' | '.join(row_values)} |")

    except Exception as e:
        print(f"An unexpected error occurred in CAST.py: {e}")

if __name__ == "__main__":
    display_capital_structure_table()