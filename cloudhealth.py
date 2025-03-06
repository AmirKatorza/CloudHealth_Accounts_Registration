import requests
import json

BEARER_TOKEN = "75848b70-89fd-4110-90d8-d629747fb8fc"
CLIENT_API_ID = "3935"
EXTERNAL_ID = "e24a4ed3b460d3cf6fd278d15de92c"
PAYER_ACCOUNTS = ["155261140164", "569250234225"]  # List of payer accounts to ignore
ROLE_TEMPLATE = "arn:aws:iam::{owner_id}:role/{role_name}"  # Configurable ARN template
ROLE_NAME = "CLDZE-CloudHealth_Role"  # Default role name

def get_all_accounts(bearer_token, client_api_id):
    """Retrieves all AWS accounts for the given client API ID, handling pagination."""
    url = f'https://chapi.cloudhealthtech.com/v1/aws_accounts?client_api_id={client_api_id}'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {bearer_token}'
    }
    
    all_accounts = []
    page = 1  # Start with the first page
    
    while True:
        try:
            response = requests.get(f"{url}&page={page}", headers=headers)  # Add pagination
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching accounts: {e}")
            return []
        
        data = response.json()
        accounts = data.get('aws_accounts', [])

        if not accounts:  # If there are no more accounts, break the loop
            break
        
        all_accounts.extend(accounts)  # Append the accounts from this page
        page += 1  # Move to the next page
    

    unique_accounts = {(account.get('owner_id'), account.get('id'), account.get('name')) for account in all_accounts if not account.get('billing', {}).get('is_consolidated', False)}  # Use set to ensure uniqueness
    
    print([acc[0] for acc in unique_accounts])  # Print only unique owner IDs
    print(f"Total unique accounts retrieved: {len(unique_accounts)}")
    
    return list(unique_accounts)

def put_arn(bearer_token, client_api_id, external_id, accounts):
    """Updates AWS accounts with an IAM role ARN, skipping payer accounts."""
    for owner_id, id, name in accounts:  # Adjusted unpacking here
        if owner_id in PAYER_ACCOUNTS:
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
        
        assume_role_arn = ROLE_TEMPLATE.format(owner_id=owner_id, role_name=ROLE_NAME)

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
    accounts = get_all_accounts(BEARER_TOKEN, CLIENT_API_ID)
    if accounts:
        put_arn(BEARER_TOKEN, CLIENT_API_ID, EXTERNAL_ID, accounts)
    else:
        print("No accounts retrieved. Exiting.")
