import subprocess
import os
import json

def generate_dip_slides_report():
    """
    Runs all DIP slide generator scripts and consolidates their
    output into a single Markdown file.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # --- Dynamic Filename Logic ---
    output_filename = "DIP_Slides_Content.md"
    try:
        json_path = os.path.join(script_dir, 'extraction.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get company name from Borrower field
        terms = data.get('data', {}).get('DIPFacilityTerms', [{}])[0]
        borrower = terms.get('borrowerGuarantor', 'Company')
        if borrower:
            company_name = borrower.split(';')[0].replace('Borrower:','').strip()
            sanitized_name = "".join(c for c in company_name if c.isalnum() or c in (' ')).rstrip()
            if sanitized_name:
                output_filename = f"{sanitized_name} DIP Summary.md"

    except Exception:
        print("Warning: Could not read company name. Using default report name.")
    
    # --- Script Execution ---
    scripts_to_run = [
        "generate_terms_slide.py",
        "generate_drawdown_slide.py",
        "generate_budget_slide.py"
    ]
    
    print(f"--- Starting DIP Slide Content Generation ---")
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    with open(os.path.join(script_dir, output_filename), 'w', encoding='utf-8') as report_file:
        for script_name in scripts_to_run:
            script_path = os.path.join(script_dir, script_name)
            
            if not os.path.exists(script_path):
                print(f"WARNING: Script not found, skipping: {script_name}")
                continue

            try:
                print(f"Running {script_name}...")
                result = subprocess.run(
                    ["python", script_path],
                    capture_output=True, text=True, check=True, env=env
                )
                report_file.write(result.stdout)
                report_file.write("\n\n---\n\n")

            except subprocess.CalledProcessError as e:
                print(f"ERROR running {script_name}:\n{e.stderr}")
            except Exception as e:
                print(f"An unexpected error occurred with {script_name}: {e}")

    print(f"\n--- Report Generation Complete ---")
    print(f"Full report saved to: {output_filename}")

if __name__ == "__main__":
    generate_dip_slides_report()