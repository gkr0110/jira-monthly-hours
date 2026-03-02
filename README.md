# Jira Monthly Invoice Generator

Automatically generates monthly invoices from Jira worklogs and emails them to organization admins on the last day of each month.

## Features

- Fetches worklogs from Jira for a specified month
- Generates a CSV invoice with hours, rates, and totals
- Sends invoice via email to designated recipients
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
# Basic usage - generate invoice without sending email
python jira-invoice.py --year 2026 --month 3 --rate 50

# Generate and send email
python jira-invoice.py \
  --year 2026 \
  --month 3 \
  --rate 50 \
  --send-email \
  --email-to "admin1@company.com,admin2@company.com" \
  --email-from "bot@company.com" \
  --email-password "app_password_here" \
  --smtp-server "smtp.gmail.com" \
  --smtp-port 587
```

#### Environment Variables (Alternative to CLI Arguments)

```bash
export JIRA_URL="https://yourcompany.atlassian.net"
export JIRA_EMAIL="your-email@company.com"
export JIRA_API_TOKEN="your-api-token"
export HOURLY_RATE="50"
export EMAIL_FROM="bot@company.com"
export EMAIL_PASSWORD="app_password"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export ORG_ADMINS="admin1@company.com,admin2@company.com"

python jira-invoice.py --year 2026 --month 3 --send-email
```

### 2. GitHub Actions Setup

#### Configure GitHub Secrets

Navigate to your repository's **Settings > Secrets and variables > Actions** and add the following secrets:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `JIRA_URL` | Your Jira instance URL | `https://yourcompany.atlassian.net` |
| `JIRA_EMAIL` | Email address for Jira API authentication | `your-email@company.com` |
| `JIRA_API_TOKEN` | Jira API token (generate from profile settings) | `ATATxxxxxxxxxxxx` |
| `HOURLY_RATE` | Billing rate per hour (USD) | `50` |
| `EMAIL_FROM` | Sender email address | `invoice-bot@company.com` |
| `EMAIL_PASSWORD` | Email password or app-specific password | `xxxx xxxx xxxx xxxx` |
| `SMTP_SERVER` | SMTP server address | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `ORG_ADMINS` | Comma-separated list of recipient emails | `admin1@company.com,admin2@company.com` |

#### How to Generate These Secrets

**Jira API Token:**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy the token and paste into GitHub Secrets

**Gmail App Password (if using Gmail):**
1. Enable 2-Step Verification on your Google Account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an app password for "Mail" and "Windows Computer"
4. Use the 16-character password (without spaces) in the `EMAIL_PASSWORD` secret

**GitHub Actions Workflow Run:**
- The workflow automatically runs on the last day of each month at 23:59 UTC
- Can be manually triggered from the Actions tab with custom year/month
- Generates CSV invoice and emails to all recipients in `ORG_ADMINS`

### 3. Monitoring

- Check the GitHub Actions tab for workflow run history
- View logs for any errors or issues
- Invoices are stored as artifacts for 30 days

## Command Line Options

```
usage: jira-invoice.py [-h] --year YEAR --month MONTH [--rate RATE] [--output OUTPUT] [--project PROJECT]
                       [--jira-url JIRA_URL] [--email EMAIL] [--token TOKEN]
                       [--send-email] [--email-to EMAIL_TO] [--email-from EMAIL_FROM]
                       [--email-password EMAIL_PASSWORD] [--smtp-server SMTP_SERVER]
                       [--smtp-port SMTP_PORT]

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
  --send-email          Send invoice via email
  --email-to EMAIL_TO   Email recipients (comma-separated, or set ORG_ADMINS env var)
  --email-from EMAIL_FROM  Sender email address (or set EMAIL_FROM env var)
  --email-password EMAIL_PASSWORD  Email password/app password (or set EMAIL_PASSWORD env var)
  --smtp-server SMTP_SERVER  SMTP server (default: smtp.gmail.com, or set SMTP_SERVER env var)
  --smtp-port SMTP_PORT  SMTP port (default: 587, or set SMTP_PORT env var)
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

### Email Not Sending
- Ensure `EMAIL_PASSWORD` is an app-specific password (not your regular password)
- Check SMTP server settings match your email provider
- Verify `EMAIL_FROM` address matches your email account

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
