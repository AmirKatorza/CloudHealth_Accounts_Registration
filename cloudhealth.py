import requests
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# Get the directory containing the script
script_dir = Path(__file__).resolve().parent
env_path = script_dir / '.env'

print(f"\n=== Environment File Debug ===")
print(f"Looking for .env file at: {env_path}")
print(f"File exists: {env_path.exists()}")

# Load environment variables from .env file
load_dotenv(env_path, override=True)  # Added override=True to ensure values are loaded

print("\n=== Raw Environment Variables ===")
print(f"BEARER_TOKEN: {os.getenv('BEARER_TOKEN')}")
print(f"CLIENT_API_ID: {os.getenv('CLIENT_API_ID')}")
print(f"EXTERNAL_ID: {os.getenv('EXTERNAL_ID')}")
print(f"PAYER_ACCOUNTS: {os.getenv('PAYER_ACCOUNTS')}")
print(f"ROLE_TEMPLATE: {os.getenv('ROLE_TEMPLATE')}")
print(f"ROLE_NAME: {os.getenv('ROLE_NAME')}")

# Load sensitive information from environment variables
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")
CLIENT_API_ID = os.getenv("CLIENT_API_ID", "")
EXTERNAL_ID = os.getenv("EXTERNAL_ID", "")
PAYER_ACCOUNTS = os.getenv("PAYER_ACCOUNTS", "").split(",") if os.getenv("PAYER_ACCOUNTS") else []
ROLE_TEMPLATE = os.getenv("ROLE_TEMPLATE", "arn:aws:iam::{owner_id}:role/{role_name}")
ROLE_NAME = os.getenv("ROLE_NAME", "CLDZE-CloudHealth_Role")
DEREGISTER_ROLE_NAME = "CLDZE-CloudHealth_Role_XXX"  # Hardcoded role name for de-registration

print("\n=== Loaded Variables ===")
print(f"BEARER_TOKEN: {BEARER_TOKEN}")
print(f"CLIENT_API_ID: {CLIENT_API_ID}")
print(f"EXTERNAL_ID: {EXTERNAL_ID}")
print(f"PAYER_ACCOUNTS: {PAYER_ACCOUNTS}")
print(f"ROLE_TEMPLATE: {ROLE_TEMPLATE}")
print(f"ROLE_NAME: {ROLE_NAME}")

def get_all_accounts(bearer_token, client_api_id, filter_status=False, include_all=False):
    """Retrieves AWS accounts for the given client API ID, handling pagination.
    
    Args:
        bearer_token (str): CloudHealth API bearer token
        client_api_id (str): Client API ID
        filter_status (bool): If True, only return accounts with 'unknown' or 'red' status
        include_all (bool): If True, include all accounts without any filtering
    """
    url = f'https://chapi.cloudhealthtech.com/v1/aws_accounts?client_api_id={client_api_id}'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {bearer_token}'
    }
    
    all_accounts = []
    page = 1
    
    while True:
        try:
            response = requests.get(f"{url}&page={page}", headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching accounts: {e}")
            return []
        
        data = response.json()
        accounts = data.get('aws_accounts', [])

        if not accounts:
            break
        
        all_accounts.extend(accounts)
        page += 1
    
    # Filter accounts based on criteria
    filtered_accounts = []
    for account in all_accounts:
        if include_all:
            # Include all accounts for de-registration
            filtered_accounts.append((
                account.get('owner_id'),
                account.get('id'),
                account.get('name')
            ))
        else:
            # Skip consolidated billing accounts for normal operations
            if account.get('billing', {}).get('is_consolidated', False):
                continue
                
            status = account.get('status', {}).get('level', '').lower()
            
            # Apply status filter if requested
            if filter_status:
                if status in ['unknown', 'red']:
                    filtered_accounts.append((
                        account.get('owner_id'),
                        account.get('id'),
                        account.get('name')
                    ))
            else:
                filtered_accounts.append((
                    account.get('owner_id'),
                    account.get('id'),
                    account.get('name')
                ))
    
    print(f"\nFound {len(filtered_accounts)} accounts matching criteria")
    print("Account IDs:", [acc[0] for acc in filtered_accounts])
    return filtered_accounts

def put_arn(bearer_token, client_api_id, external_id, accounts, is_deregister=False):
    """Updates AWS accounts with an IAM role ARN, skipping payer accounts unless deregistering."""
    for owner_id, id, name in accounts:
        if not is_deregister and owner_id in PAYER_ACCOUNTS:
            print(f"Skipping payer account: {owner_id}")
            continue
        
        print('-' * 100)
        print('CONFIGURING ACCOUNT')
        print(f"Owner ID: {owner_id}")
        print('-' * 100)
        
        url = f'https://chapi.cloudhealthtech.com/v1/aws_accounts/{id}?client_api_id={client_api_id}'
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        role_name = DEREGISTER_ROLE_NAME if is_deregister else ROLE_NAME
        assume_role_arn = ROLE_TEMPLATE.format(owner_id=owner_id, role_name=role_name)
        
        data = {
            "name": name,
            "authentication": {
                "protocol": "assume_role",
                "assume_role_arn": assume_role_arn,
                "assume_role_external_id": external_id
            }
        }        
        
        try:
            response = requests.put(url, headers=headers, json=data)
            response.raise_for_status()
            print("Response JSON:")
            print(json.dumps(response.json(), indent=4))  # Pretty-print JSON response
        except requests.RequestException as e:
            print(f"Failed to insert ARN for account {owner_id}: {e}")

if __name__ == "__main__":
    if not BEARER_TOKEN or not CLIENT_API_ID or not EXTERNAL_ID:
        print("Missing required environment variables. Please set BEARER_TOKEN, CLIENT_API_ID, and EXTERNAL_ID in the .env file.")
        exit(1)
    
    while True:
        print("\n=== CloudHealth Account Configuration Tool ===")
        print("1. Run on all accounts (excluding consolidated billing)")
        print("2. Run on filtered accounts (Status: UNKNOWN or RED)")
        print("3. De-register all accounts (including consolidated billing)")
        print("\nPlease enter your choice (1, 2, or 3):")
        
        choice = input().strip()
        
        if choice not in ['1', '2', '3']:
            print("\nInvalid input! Please enter either 1, 2, or 3.")
            continue
        
        if choice == '3':
            # De-register all accounts
            accounts = get_all_accounts(BEARER_TOKEN, CLIENT_API_ID, include_all=True)
            if accounts:
                print(f"\nProcessing {len(accounts)} accounts for de-registration...")
                put_arn(BEARER_TOKEN, CLIENT_API_ID, EXTERNAL_ID, accounts, is_deregister=True)
            else:
                print("No accounts retrieved. Please check your connection and try again.")
        else:
            # Normal operation
            filter_status = (choice == '2')
            accounts = get_all_accounts(BEARER_TOKEN, CLIENT_API_ID, filter_status)
            if accounts:
                print(f"\nProcessing {len(accounts)} accounts...")
                put_arn(BEARER_TOKEN, CLIENT_API_ID, EXTERNAL_ID, accounts)
            else:
                print("No accounts retrieved. Please check your filters and try again.")
        
        print("\nWould you like to run again? (y/n):")
        if input().strip().lower() != 'y':
            print("Exiting...")
            break
