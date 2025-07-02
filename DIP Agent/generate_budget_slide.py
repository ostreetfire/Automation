import json
import os

def generate_slide_content(file_path):
    """Generates the Markdown content for the DIP Budget slide."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f).get('data', {})

        budget = data.get('DIPBudget', {})
        if not budget:
            print("## DIP Budget as Filed\n\n- *Budget data not found.*")
            return

        print("## DIP Budget as Filed\n")
        print("#### DIP Budget ($000's)\n")

        dates = budget.get('weekEndingDates', [])
        line_items = budget.get('budgetLineItems', [])
        
        # --- Header ---
        header = "| Week Ending | " + " | ".join(dates) + " | Total |"
        print(header)
        
        # --- Separator ---
        separator = "|---|" + "---|"*len(dates) + "---|"
        print(separator)

        # --- Rows ---
        for item in line_items:
            name = item.get('lineItemName', 'N/A')
            values = item.get('weeklyValues', [0]*len(dates))
            total = item.get('total', 0)
            
            # Format values with commas and parentheses for negatives
            formatted_values = [f"{val:,.0f}" if val >= 0 else f"({abs(val):,.0f})" for val in values]
            formatted_total = f"{total:,.0f}" if total >= 0 else f"({abs(total):,.0f})"
            
            row_str = f"| **{name}** | " + " | ".join(formatted_values) + f" | **{formatted_total}** |"
            print(row_str)

    except Exception as e:
        print(f"An error occurred in generate_budget_slide.py: {e}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dir, 'extraction.json')
    generate_slide_content(json_file)