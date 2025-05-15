# CloudHealth AWS Account Configuration Tool

This tool automates the process of configuring AWS accounts in CloudHealth by setting up IAM roles and authentication for multiple accounts. It provides an interactive menu to either process all accounts, focus on problematic accounts, or de-register accounts from CloudHealth.

## Features

- Interactive menu for choosing processing options
- Automatic pagination for handling large numbers of accounts
- Filtering options for targeting specific account statuses
- Automatic exclusion of consolidated billing accounts (except for de-registration)
- Detailed output and progress tracking
- Error handling and retry options
- Account de-registration functionality

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)
- CloudHealth API access (Bearer Token)
- AWS accounts that need to be configured

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install requests python-dotenv
```

## Configuration

1. Create a `.env` file in the root directory of the project:
```bash
touch .env
```

2. Add the following environment variables to your `.env` file:
```
BEARER_TOKEN=your_cloudhealth_api_token
CLIENT_API_ID=your_client_api_id
EXTERNAL_ID=your_external_id
PAYER_ACCOUNTS=account1,account2,account3
ROLE_TEMPLATE=arn:aws:iam::{owner_id}:role/{role_name}  # Optional
ROLE_NAME=CLDZE-CloudHealth_Role  # Optional
```

### Environment Variables Description

- `BEARER_TOKEN`: Your CloudHealth API authentication token
- `CLIENT_API_ID`: Your CloudHealth Client API ID
- `EXTERNAL_ID`: The External ID used for cross-account IAM role authentication
- `PAYER_ACCOUNTS`: Comma-separated list of AWS account IDs that are payer accounts (these will be skipped during normal operations)
- `ROLE_TEMPLATE`: (Optional) Template for the IAM role ARN. Default: "arn:aws:iam::{owner_id}:role/{role_name}"
- `ROLE_NAME`: (Optional) Name of the IAM role to be used. Default: "CLDZE-CloudHealth_Role"

## Usage

1. Ensure your virtual environment is activated:
```bash
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

2. Run the script:
```bash
python cloudhealth.py
```

3. Choose your processing option from the interactive menu:
   - Option 1: Process all accounts (excluding consolidated billing accounts)
   - Option 2: Process only accounts with status 'UNKNOWN' or 'RED' (excluding consolidated billing accounts)
   - Option 3: De-register all accounts (including consolidated billing accounts)

### Processing Options

#### Option 1: All Accounts
- Processes all AWS accounts in CloudHealth
- Automatically excludes consolidated billing accounts
- Configures IAM roles for remaining accounts

#### Option 2: Filtered Accounts
- Only processes accounts with status 'UNKNOWN' or 'RED'
- Automatically excludes consolidated billing accounts
- Useful for focusing on problematic accounts that need attention

#### Option 3: De-register Accounts
- Processes ALL accounts in CloudHealth (including consolidated billing)
- Uses hardcoded role name "CLDZE-CloudHealth_Role_XXX"
- Includes payer accounts in the process
- Useful for bulk de-registration of accounts

### Script Behavior

The script will:
1. Load and validate environment variables
2. Present an interactive menu for processing options
3. Retrieve and filter accounts based on your selection
4. Show the number of accounts that will be processed
5. Configure IAM roles for the selected accounts
6. Provide detailed output for each account processed
7. Offer the option to run additional processing cycles

## Output

The script provides detailed output including:
- Environment variable status at startup
- Number of accounts matching selected criteria
- List of account IDs to be processed
- Configuration status for each account
- Any errors that occur during processing
- Option to run additional processing cycles

## Troubleshooting

1. If environment variables are not loading:
   - Verify the `.env` file exists in the same directory as the script
   - Check the `.env` file format (no spaces around '=' signs)
   - Ensure the `.env` file has the correct permissions

2. If API calls fail:
   - Verify your BEARER_TOKEN is correct and not expired
   - Check your internet connection
   - Verify the CLIENT_API_ID is correct

3. If accounts are skipped:
   - Check if they are in the PAYER_ACCOUNTS list (for normal operations)
   - Verify their status in CloudHealth console
   - Confirm if they are consolidated billing accounts (for normal operations)

4. If no accounts are found:
   - When using Option 2, verify that accounts have the correct status (UNKNOWN or RED)
   - For normal operations, confirm that the accounts are not consolidated billing accounts
   - Check the CloudHealth console for account status

5. For de-registration issues:
   - Verify that the hardcoded role name "CLDZE-CloudHealth_Role_XXX" exists in your AWS accounts
   - Check if you have the necessary permissions to update all accounts
   - Ensure the external ID is correct for all accounts

## Security Notes

- Never commit your `.env` file to version control
- Keep your BEARER_TOKEN and EXTERNAL_ID secure
- Regularly rotate your credentials
- Use appropriate IAM role permissions
- Be cautious when using the de-registration option as it affects all accounts

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 