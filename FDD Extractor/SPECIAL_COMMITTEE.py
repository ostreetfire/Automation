import json
import textwrap
import string

def clean_text(text):
    if not isinstance(text, str): return text
    return ''.join(filter(lambda x: x in string.printable, text))

def display_special_committee(file_path):
    print("## Special Committee Information ##")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f).get('data', {})

        committee = data.get('SpecialCommittee', {})
        if not committee:
            print("No Special Committee data found.")
            return

        print(f"\n**Formation Date:** {clean_text(committee.get('formationDate', 'N/A'))}")
        
        print("\n**Mandate:**")
        print(textwrap.fill(clean_text(committee.get('mandate', 'N/A')), width=88))
        
        members = committee.get('members', [])
        print("\n**Members:**")
        if members:
            for member in members:
                print(f"- {clean_text(member)}")
        else:
            print("No members listed.")

        print(f"\n**Advisors:** {clean_text(committee.get('advisors', 'N/A'))}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    json_file = r'C:\Users\OscarStrieter\OneDrive - Province LLC\Desktop\O. Strieter\15. Code\SEC Filing Extractor\FDD Extractor\extraction.json'
    display_special_committee(json_file)