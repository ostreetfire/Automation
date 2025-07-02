import json
import textwrap
import string

def clean_text(text):
    if not isinstance(text, str): return text
    return ''.join(filter(lambda x: x in string.printable, text))

def display_case_overview(file_path):
    print("## Case Overview ##")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f).get('data', {})

        overview = data.get('CaseOverview', {})
        if not overview:
            print("No Case Overview data found.")
            return

        print("\n**Company Description:**")
        print(textwrap.fill(clean_text(overview.get('companyDescription', 'N/A')), width=88))
        
        print("\n**Case Summary:**")
        print(textwrap.fill(clean_text(overview.get('caseSummary', 'N/A')), width=88))

        print("\n**Reasons for Filing:**")
        print(textwrap.fill(clean_text(overview.get('reasonsForFiling', 'N/A')), width=88))
        
        print("\n**Restructuring Purpose & Go-Forward Plan:**")
        print(textwrap.fill(clean_text(overview.get('restructuringPurpose', 'N/A')), width=88))

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    json_file = r'C:\Users\OscarStrieter\OneDrive - Province LLC\Desktop\O. Strieter\15. Code\SEC Filing Extractor\FDD Extractor\extraction.json'
    display_case_overview(json_file)