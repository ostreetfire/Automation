import subprocess
import os
import json

def generate_bankruptcy_report():
    """
    Runs all bankruptcy analysis scripts and consolidates their
    output into a single, dynamically named Markdown report.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # --- Dynamic Filename Logic ---
    output_filename = "bankruptcy_report.md"
    company_name_str = "Report"
    try:
        json_path = os.path.join(script_dir, 'extraction.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get the first word from the company description for the filename
        desc = data.get('data',{}).get('CaseOverview',{}).get('companyDescription','')
        if desc:
            company_name = desc.split(' ')[0]
            sanitized_name = "".join(c for c in company_name if c.isalnum()).rstrip()
            if sanitized_name:
                output_filename = f"{sanitized_name} Case Summary.md"
                company_name_str = sanitized_name

    except (FileNotFoundError, json.JSONDecodeError):
        print("Warning: Could not read company name. Using default report name.")
    
    # --- Script Execution ---
    scripts_to_run = [
        "CASE_OVERVIEW.py",
        "FINANCIALS.py",
        "PREPETITION.py",
        "SPECIAL_COMMITTEE.py"
    ]
    
    print(f"--- Starting Report Generation for {company_name_str} ---")
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    with open(os.path.join(script_dir, output_filename), 'w', encoding='utf-8') as report_file:
        for script_name in scripts_to_run:
            script_path = os.path.join(script_dir, script_name)
            
            if not os.path.exists(script_path):
                print(f"WARNING: Script not found, skipping: {script_name}")
                report_file.write(f"\n--- SKIPPED: {script_name} (File not found) ---\n")
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
                error_message = f"ERROR running {script_name}:\n{e.stderr}"
                print(error_message)
                report_file.write(f"\n--- FAILED: {script_name} ---\n{e.stderr}\n")
            except Exception as e:
                general_error = f"An unexpected error occurred with {script_name}: {e}"
                print(general_error)
                report_file.write(f"\n--- FAILED with unexpected error: {script_name} ---\n{general_error}\n")

    print(f"\n--- Report Generation Complete ---")
    print(f"Full report saved to: {output_filename}")

if __name__ == "__main__":
    generate_bankruptcy_report()