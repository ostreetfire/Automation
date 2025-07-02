import json
import os
import textwrap

def clean_text(text):
    if not isinstance(text, str): return text
    return ''.join(filter(str.isprintable, text))

def generate_slide_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f).get('data', {})

        terms_list = data.get('DIPFacilityTerms', [])
        overview = data.get('DIPFinancingOverview', {})
        
        if not terms_list or not overview:
            print("## DIP Facility Terms\n\n- *Required data not found.*")
            return

        main_terms = terms_list[0] if terms_list else {}
        
        # --- FIX: More reliable title generation ---
        borrower_info = main_terms.get('borrowerGuarantor', 'Company Name')
        company_name = clean_text(borrower_info.split(';')[0].replace('Borrower:', '').strip())
        commitment_info = clean_text(main_terms.get('commitment', 'an amount of new money'))

        print(f"## DIP FACILITY TERMS")
        print(f"### {company_name} secures {commitment_info} in the DIP Facility to navigate Chapter 11, ensuring liquidity for operational continuity.\n")

        print("#### Overview\n")
        # --- FIX: Better formatting for bullet points ---
        commentary = clean_text(main_terms.get('commentary', ''))
        # Split by newline and filter for lines that start with a bullet point character
        points = [line.strip() for line in commentary.split('\n') if line.strip().startswith('*')]
        if points:
            for point in points:
                # Remove the leading '*' and wrap the text
                cleaned_point = point.lstrip('* ').strip()
                print(f"* {textwrap.fill(cleaned_point, width=80, subsequent_indent='  ')}")
        else:
            # Fallback for unformatted text
            print(f"* {textwrap.fill(commentary, width=80, subsequent_indent='  ')}")


        print("\n#### Summary of DIP Facility Terms\n")
        print("| Term | Details |")
        print("|---|---|")
        print(f"| **Commitment** | {clean_text(main_terms.get('commitment', 'N/A')).replace('|', '')} |")
        print(f"| **Borrower/Guarantor** | {clean_text(main_terms.get('borrowerGuarantor', 'N/A')).replace('|', '')} |")
        print(f"| **Lender** | {clean_text(main_terms.get('lender', 'N/A')).replace('|', '')} |")
        print(f"| **Interest Rate** | {clean_text(main_terms.get('interestRate', 'N/A')).replace('|', '')} |")
        print(f"| **Fees** | {clean_text(main_terms.get('fees', 'N/A')).replace('|', '')} |")
        print(f"| **DIP Liens and Collateral** | {textwrap.fill(clean_text(overview.get('liensCollateral', 'N/A')), width=60).replace('|', '')} |")
        print(f"| **Adequate Protection** | {textwrap.fill(clean_text(overview.get('adequateProtection', 'N/A')), width=60).replace('|', '')} |")
        print(f"| **Use of Proceeds** | {textwrap.fill(clean_text(overview.get('useOfProceeds', 'N/A')), width=60).replace('|', '')} |")
        print(f"| **Maturity** | {clean_text(main_terms.get('maturity', 'N/A')).replace('|', '')} |")
        print(f"| **Carve-Out** | {textwrap.fill(clean_text(overview.get('carveOut', 'N/A')), width=60).replace('|', '')} |")

    except Exception as e:
        print(f"An error occurred in generate_terms_slide.py: {e}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dir, 'extraction.json')
    generate_slide_content(json_file)