import json
import textwrap
import string

def clean_text(text):
    if not isinstance(text, str): return text
    return ''.join(filter(lambda x: x in string.printable, text))

def display_prepetition_transactions(file_path):
    print("## Prepetition Transactions & Events ##")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f).get('data', {})

        trans = data.get('PrepetitionTransactions', {})
        if not trans:
            print("No Prepetition Transactions data found.")
            return

        print("\n**Cost Rationalization Measures:**")
        print(textwrap.fill(clean_text(trans.get('costRationalizationMeasures', 'N/A')), width=88))
        
        print("\n**Liquidity Management:**")
        print(textwrap.fill(clean_text(trans.get('liquidityManagement', 'N/A')), width=88))

        bridge = trans.get('bridgeFinancing', {})
        print("\n**Bridge Financing:**")
        print(f"**Details:** {textwrap.fill(clean_text(bridge.get('facilityDetails', 'N/A')), width=88)}")
        print(f"**Purpose:** {textwrap.fill(clean_text(bridge.get('purpose', 'N/A')), width=88)}")
        
        print("\n**Forbearance Agreements:**")
        print(textwrap.fill(clean_text(trans.get('forbearanceAgreements', 'N/A')), width=88))

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    json_file = r'C:\Users\OscarStrieter\OneDrive - Province LLC\Desktop\O. Strieter\15. Code\SEC Filing Extractor\FDD Extractor\extraction.json'
    display_prepetition_transactions(json_file)