import json
import os
import textwrap

def clean_text(text):
    if not isinstance(text, str): return text
    return ''.join(filter(str.isprintable, text))

def generate_slide_content(file_path):
    """Generates the Markdown content for the DIP Drawdown slide."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f).get('data', {})

        drawdown = data.get('DIPFacilityDrawdown', {})
        budget = data.get('DIPBudget', {})
        
        if not drawdown or not budget:
            print("## DIP Facility Drawdown\n\n- *Required data not found.*")
            return
            
        # --- Title & Subtitle ---
        print("## DIP FACILITY DRAWDOWN\n")
        print(f"_{clean_text(drawdown.get('commentary', ''))}_\n")

        # --- Left Side Commentary ---
        print("#### Overview\n")
        print(f"**A) Initial Draw**\n* {clean_text(drawdown.get('initialDraw', 'N/A'))}\n")
        print(f"**B) Final Draw**\n* {clean_text(drawdown.get('finalDraw', 'N/A'))}\n")
        print(f"**C) DIP Related Fees**\n* {clean_text(drawdown.get('dipRelatedFees', 'N/A'))}\n")

        # --- Right Side Chart Data ---
        print("#### DIP Budget Bridge ($MM)\n")
        print("> **Note:** Use the following data points to create the waterfall chart in your presentation software.\n")
        
        budget_items = {item['lineItemName']: item['total'] for item in budget.get('budgetLineItems', [])}
        
        print("| Category | Amount ($MM) |")
        print("|---|---|")
        print(f"| Beginning Cash Balance | {budget_items.get('Beginning Cash Balance', 0):.2f} |")
        print(f"| Operating Receipts | {budget_items.get('Total Receipts', 0):.2f} |")
        print(f"| Sale of Assets | {budget_items.get('Asset Sales', 0):.2f} |")
        print(f"| DIP Facility Draws | {budget_items.get('(+) DIP Draw', 0):.2f} |")
        print(f"| Operating Disbursements | {budget_items.get('Total Operating Disbursements', 0):.2f} |")
        print(f"| Restructuring Items | {budget_items.get('Total Non-Operating Disbursements', 0):.2f} |")
        print(f"| FILO / Revolver (Paydown) | {budget_items.get('FILO Paydown', 0):.2f} |")
        print(f"| DIP Facility (Paydown) | {budget_items.get('(-) DIP Paydown', 0):.2f} |")
        print(f"| **Ending Cash Balance** | **{budget_items.get('Ending Cash Balance', 0):.2f}** |")

        # --- Bottom Commentary ---
        print(f"\n**DIP funds are needed to bridge the budget until the receipt of the $50 million on account of the sale of assets as they are not forecasted to be received until the week ending 7/5/2024.**")

    except Exception as e:
        print(f"An error occurred in generate_drawdown_slide.py: {e}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dir, 'extraction.json')
    generate_slide_content(json_file)