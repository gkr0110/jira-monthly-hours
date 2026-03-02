# Jira Monthly Invoice Generator

Automatically generates monthly invoices from Jira worklogs on the last day of each month. Sends notifications to Discord and uploads CSV to Google Drive via GitHub Actions.

## Features

- Fetches worklogs from Jira for a specified month
- Generates a CSV invoice with hours, rates, and totals
- Sends invoice summary to Discord channel (with rich formatting)
- Uploads invoice CSV to Google Drive folder
- Stores invoice as GitHub artifact (30-day retention)
- Scheduled to run automatically on the last day of each month via GitHub Actions
- Supports manual triggering for specific months

## Setup

### 1. Local Development

#### Prerequisites
- Python 3.9+
- pip

#### Installation

```bash
# Clone or navigate to the repository
cd jira-monthly-hours

# Install dependencies
pip install -r requirements.txt
```

#### Running Locally

```bash
# Generate invoice (CSV only, no notifications)
python jira-invoice.py --year 2026 --month 3 --rate 50

# Or use environment variable for rate
export HOURLY_RATE=50
python jira-invoice.py --year 2026 --month 3
```

#### Environment Variables (Alternative to CLI Arguments)

```bash
# Jira configuration
export JIRA_URL="https://yourcompany.atlassian.net"
export JIRA_EMAIL="your-email@company.com"
export JIRA_API_TOKEN="your-api-token"
export HOURLY_RATE="50"

python jira-invoice.py --year 2026 --month 3
```

**Note:** Discord and Google Drive uploads are only available via GitHub Actions workflow (not locally).

### 2. GitHub Actions Setup

#### Configure GitHub Secrets

Navigate to your repository's **Settings > Secrets and variables > Actions** and add the following secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `JIRA_URL` | Your Jira instance URL | `https://yourcompany.atlassian.net` |
| `JIRA_EMAIL` | Email address for Jira API authentication | `your-email@company.com` |
| `JIRA_API_TOKEN` | Jira API token (generate from profile settings) | `ATATxxxxxxxxxxxx` |
| `HOURLY_RATE` | Billing rate per hour (USD) | `50` |
| `DISCORD_WEBHOOK` | Discord channel webhook URL | `https://discord.com/api/webhooks/...` |
| `GOOGLE_CREDENTIALS` | Google service account JSON (entire file contents) | `{"type": "service_account", ...}` |
| `GOOGLE_DRIVE_FOLDER_ID` | Google Drive folder ID for CSV storage | `1A2B3C4D5E6F...` |

#### How to Generate These Secrets

For detailed instructions on generating all secrets, see [SETUP_GUIDE.md](SETUP_GUIDE.md). Quick summary:

**Jira API Token:**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token" and copy to `JIRA_API_TOKEN` secret

**Discord Webhook:**
1. In Discord, go to channel settings > Integrations > Webhooks
2. Create a webhook and copy URL to `DISCORD_WEBHOOK` secret

**Google Drive Setup:**
1. Create Google Cloud service account
2. Enable Google Drive API
3. Create JSON key and share folder with service account email
4. Paste entire JSON file into `GOOGLE_CREDENTIALS` secret
5. Paste folder ID into `GOOGLE_DRIVE_FOLDER_ID` secret

**GitHub Actions Workflow:**
- Automatically runs on the last day of each month at 23:59 UTC
- Can be manually triggered from the Actions tab with custom year/month
- Sends Discord notification with invoice summary
- Uploads CSV to Google Drive
- Stores CSV as GitHub artifact (30-day retention)

### 3. Monitoring

- Check the GitHub Actions tab for workflow run history
- View logs for any errors or issues
- Invoices are stored as artifacts for 30 days

## Command Line Options

```
usage: jira-invoice.py [-h] --year YEAR --month MONTH [--rate RATE] [--output OUTPUT] [--project PROJECT]
                       [--jira-url JIRA_URL] [--email EMAIL] [--token TOKEN]

Generate invoice from Jira worklogs

optional arguments:
  -h, --help            show this help message and exit
  --year YEAR           Year (e.g., 2026)
  --month MONTH         Month (1-12)
  --rate RATE           Hourly rate in USD (or set HOURLY_RATE env var)
  --output OUTPUT       Output CSV filename
  --project PROJECT     Jira project key (e.g., GAL)
  --jira-url JIRA_URL   Jira URL (or set JIRA_URL env var)
  --email EMAIL         Jira email (or set JIRA_EMAIL env var)
  --token TOKEN         Jira API token (or set JIRA_API_TOKEN env var)
```

## Output

The script generates a CSV file with the following columns:
- Issue Key
- Summary
- Date
- Time Spent (Hours)
- Rate (USD/hr)
- Amount (USD)
- Project

And a final TOTAL row with aggregated hours and amount.

## Troubleshooting

### Discord Webhook Not Working
- Verify `DISCORD_WEBHOOK` secret contains a valid webhook URL
- Check webhook hasn't expired (recreate if needed)
- Ensure Discord bot has permission to post in channel
- Check GitHub Actions logs for webhook response errors

### Google Drive Upload Failing
- Verify `GOOGLE_CREDENTIALS` JSON is complete and valid
- Confirm service account email has access to target folder
- Check `GOOGLE_DRIVE_FOLDER_ID` is correct
- Look for permission errors in GitHub Actions logs
- Ensure Google Drive API is enabled in Google Cloud project

### Jira Connection Errors
- Verify `JIRA_URL` is correct (no trailing slash)
- Confirm `JIRA_EMAIL` and `JIRA_API_TOKEN` are valid
- Check firewall/network connectivity to Jira

### No Worklogs Found
- Ensure worklogs were logged in the specified month
- Verify the Jira user has permission to view their own worklogs
- Check project filter if specified

## License

MIT
