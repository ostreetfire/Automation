import json

def display_related_party_transactions(file_path=r'C:\Users\OscarStrieter\OneDrive - Province LLC\Desktop\O. Strieter\15. Code\SEC Filing Extractor\10-K Extractor\extraction.json'):
    """
    Loads and displays Related Party Transactions from the JSON file.
    """
    print("--- Related Party Transactions ---")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        transactions = data.get('data', {}).get('RelatedPartyTransactions', [])
        
        if not transactions:
            print("No Related Party Transactions found.")
            return
            
        for i, tx in enumerate(transactions, 1):
            name = tx.get("relatedPartyName", "N/A")
            relationship = tx.get("relationship", "N/A")
            description = tx.get("transactionDescription", "N/A")
            amounts = tx.get("transactionAmounts", "N/A")

            print(f"\n--- Transaction {i} ---")
            print(f"  - Related Party: {name}")
            print(f"  - Relationship: {relationship}")
            print(f"  - Description: {description}")
            print(f"  - Amounts: {amounts}")

    except FileNotFoundError:
        print(f"Error: The file at '{file_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' contains invalid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    display_related_party_transactions()