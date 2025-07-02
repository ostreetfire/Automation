import json
import textwrap
import string

def clean_text(text):
    if not isinstance(text, str): return text
    return ''.join(filter(lambda x: x in string.printable, text))

def display_financial_condition(file_path):
    print("## Financial Condition ##")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f).get('data', {})

        financials = data.get('FinancialCondition', {})
        if not financials:
            print("No Financial Condition data found.")
            return

        # Assets
        assets = financials.get('assets', {})
        print("\n**Assets:**")
        print(f"- **Cash and Equivalents:** {clean_text(assets.get('cashAndEquivalents', 'N/A'))}")
        print(f"- **Accounts Receivable:** {clean_text(assets.get('accountsReceivable', 'N/A'))}")
        print(f"- **Inventory:** {clean_text(assets.get('inventory', 'N/A'))}")

        # Liabilities
        liabilities = financials.get('liabilities', {})
        print("\n**Liabilities:**")
        print(f"- **Trade Payables:** {clean_text(liabilities.get('tradePayables', 'N/A'))}")
        
        funded_debt = liabilities.get('fundedDebt', [])
        print("\n**Funded Debt Structure:**")
        if funded_debt:
            print("| Facility Name | Principal | Total Outstanding |")
            print("|---|---|---|")
            for debt in funded_debt:
                name = clean_text(debt.get('facilityName','N/A'))
                principal = clean_text(debt.get('principal','N/A'))
                outstanding = clean_text(debt.get('totalOutstanding','N/A'))
                print(f"| {name} | {principal} | {outstanding} |")
        else:
            print("No funded debt details found.")

        # Historical Performance
        performance = financials.get('historicalPerformance', {})
        print("\n**Historical Performance:**")
        print(f"**Summary:** {textwrap.fill(clean_text(performance.get('performanceSummary', 'N/A')), width=88)}")
        print(f"**Impact of Specific Events:** {textwrap.fill(clean_text(performance.get('specificEventsImpact', 'N/A')), width=88)}")
        
        # Projections
        print("\n**Financial Projections:**")
        print(textwrap.fill(clean_text(financials.get('financialProjections', 'N/A')), width=88))

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    json_file = r'C:\Users\OscarStrieter\OneDrive - Province LLC\Desktop\O. Strieter\15. Code\SEC Filing Extractor\FDD Extractor\extraction.json'
    display_financial_condition(json_file)