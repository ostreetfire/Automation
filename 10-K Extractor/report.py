import subprocess
import os
import json

def generate_consolidated_report():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    output_filename = "consolidated_report.md" # Default filename
    try:
        json_path = os.path.join(script_dir, 'extraction.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        company_name = data.get('data', {}).get('companyProfile', {}).get('name')

        if company_name:
            sanitized_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '.', '_')).rstrip()
            # 1. CHANGE: Use .md extension
            output_filename = f"{sanitized_name}.md"

    except (FileNotFoundError, json.JSONDecodeError):
        print("Warning: Could not read company name. Using default report name.")
    
    scripts_to_run = [
        "COMPANY.py", "RISKS.py", "LIQUIDITY.py", "DEBT.py",
        "CAST.py", "RELATED_PARTY.py", "AUDIT_MATTERS.py"
    ]
    
    print(f"--- Starting Full Report Generation ---")
    print(f"Report will be saved as: {output_filename}")
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    with open(os.path.join(script_dir, output_filename), 'w', encoding='utf-8') as report_file:
        for script_name in scripts_to_run:
            script_path = os.path.join(script_dir, script_name)
            
            if not os.path.exists(script_path):
                # ... (error handling is the same)
                continue

            try:
                print(f"Running {script_name}...")
                
                result = subprocess.run(
                    ["python", script_path],
                    capture_output=True, text=True, check=True, env=env
                )
                
                report_file.write(result.stdout)
                # 2. CHANGE: Use Markdown horizontal rule as a separator
                report_file.write("\n\n---\n\n")

            except subprocess.CalledProcessError as e:
                # ... (error handling is the same)
                pass
            except Exception as e:
                # ... (error handling is the same)
                pass

    print(f"\n--- Report Generation Complete ---")
    print(f"Full report saved to: {output_filename}")

if __name__ == "__main__":
    generate_consolidated_report()