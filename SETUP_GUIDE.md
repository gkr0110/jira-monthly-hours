# Setup Guide: Scheduling Monthly Invoice Generation

## Overview

This guide walks through setting up the Jira Monthly Invoice Generator to automatically run on the last day of each month and email the CSV to organization administrators.

## Architecture

```
┌─────────────────────────────────────────────────┐
│         GitHub Actions Workflow                 │
├─────────────────────────────────────────────────┤
│  Trigger: Last day of month (cron schedule)     │
│  Action: Run jira-invoice.py script             │
├─────────────────────────────────────────────────┤
│  Environment Setup (from GitHub Secrets):       │
│  • JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN        │
│  • HOURLY_RATE, DISCORD_WEBHOOK                │
├─────────────────────────────────────────────────┤
│  Process:                                       │
│  1. Generate invoice CSV from Jira worklogs     │
│  2. Send notification to Discord channel       │
│  3. Store artifact for 30 days on GitHub       │
└─────────────────────────────────────────────────┘
```

## Step-by-Step Setup

### Step 1: Prepare GitHub Secrets

1. **Navigate to Repository Settings**
   - Go to your GitHub repository
   - Click **Settings** → **Secrets and variables** → **Actions**

2. **Create the Following Secrets**

   #### Jira Configuration
   ```
   JIRA_URL = https://yourcompany.atlassian.net
   JIRA_EMAIL = your-account@company.com
   JIRA_API_TOKEN = [See "Generate Jira API Token" below]
   ```

   #### Billing Configuration
   ```
   HOURLY_RATE = 50
   ```

   #### Discord Configuration
   ```
   DISCORD_WEBHOOK = https://discord.com/api/webhooks/...
   ```

   #### Google Drive Configuration
   ```
   GOOGLE_CREDENTIALS = [entire service account JSON contents]
   GOOGLE_DRIVE_FOLDER_ID = 1A2B3C4D5E6F...
   ```

### Step 2: Generate Required Credentials

#### Generate Jira API Token

1. Visit https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **Create API token**
3. Name it (e.g., "GitHub Invoice Bot")
4. Copy the generated token
5. Paste into GitHub Secret `JIRA_API_TOKEN`

#### Create Discord Webhook

**For existing Discord server:**
1. Open your Discord server
2. Navigate to the channel where you want invoice notifications
3. Right-click channel name, select **Edit channel** or click the gear icon
4. Select **Integrations** from sidebar
5. Click **Webhooks** section
6. Click **Create Webhook**
7. Name it "Invoice Bot"
8. Click **Copy Webhook URL**
9. Paste into GitHub Secret `DISCORD_WEBHOOK`

**For new Discord server:**
1. Create a new Discord server
2. Create a channel (e.g., #invoices)
3. Follow steps 3-9 above

**Webhook URL Format:** `https://discord.com/api/webhooks/{WEBHOOK_ID}/{TOKEN}`

#### Create Google Service Account & Drive Access

**Step 1: Create Google Cloud Project**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Drive API:
   - Click **APIs & Services** → **Library**
   - Search for "Google Drive API"
   - Click **Enable**

**Step 2: Create Service Account**
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **Service Account**
3. Fill service account details:
   - Name: "invoice-bot" (or your preference)
   - Skip optional steps
4. Click **Create and Continue**, then **Done**

**Step 3: Create JSON Key**
1. In **APIs & Services** → **Credentials**
2. Find your service account in the list
3. Click the service account email
4. Go to **Keys** tab
5. Click **Add Key** → **Create new key** → **JSON**
6. A JSON file downloads automatically (save this safely)

**Step 4: Share Google Drive Folder**
1. Open/create a Google Drive folder for invoices
2. Copy folder ID from URL: `https://drive.google.com/drive/folders/{FOLDER_ID}`
3. In the downloaded JSON file, find the `client_email` field
4. Share the Google Drive folder with this email
5. Grant **Editor** permissions

**Step 5: Add to GitHub Secrets**
1. Open the downloaded JSON file
2. Copy the **entire contents**
3. Paste into GitHub Secret `GOOGLE_CREDENTIALS`
4. Paste the folder ID into GitHub Secret `GOOGLE_DRIVE_FOLDER_ID`

### Step 3: Verify Workflow Configuration

The workflow file (`.github/workflows/monthly-invoice.yml`) includes:

- **Schedule Trigger**: Runs at 23:59 UTC on days 28-31 (covers all possible month-end dates)
- **Manual Trigger**: Can be run manually from Actions tab with custom year/month
- **Automatic Last-Day Check**: Script verifies it's actually the last day before running
- **Environment Variables**: All GitHub Secrets are passed as environment variables
- **Discord Integration**: Posts message to Discord channel with invoice summary
- **Google Drive Upload**: Uploads CSV to specified Google Drive folder
- **Artifact Storage**: CSV is saved as artifact for 30 days
- **Error Handling**: Sends failure notification to Discord if something goes wrong

### Step 4: Test the Setup

#### Option A: Manual Test (Recommended First)

1. Go to **Actions** tab in your GitHub repository
2. Select **"Generate and Send Monthly Invoice to Discord"** workflow
3. Click **Run workflow**
4. In the dropdown, optionally specify custom year/month, or leave blank for current month
5. Monitor the workflow execution
6. Check Discord channel for invoice notification

#### Option B: Review Workflow Run

1. Go to **Actions** tab
2. Click the workflow run
3. Review logs for any errors
4. Check Discord channel for notification
5. Download the generated CSV from **Artifacts**

### Step 5: Schedule Verification

The workflow is scheduled to run at **23:59 UTC on the last day of each month**:

- **Monthly Execution**: Cron `59 23 28-31 * *` covers all possible last days
- **Time Zone**: UTC (adjust if needed in `monthly-invoice.yml`)
- **Automatic Detection**: Script checks if today is actually the last day to prevent false triggers

#### Adjusting Schedule

Edit `.github/workflows/monthly-invoice.yml` to change the schedule:

```yaml
schedule:
  - cron: '59 23 28-31 * *'  # Current: 23:59 UTC on potential last days
```

Examples:
- `0 0 * * *` = Daily at midnight UTC
- `0 9 L * *` = Not supported; use workaround with script logic
- `0 0 1 * *` = First day of month at midnight UTC

### Step 6: Monitoring & Maintenance

#### Monitor Workflow Runs
- Check **Actions** tab regularly
- Set up GitHub notifications for workflow failures
- Review logs if invoice isn't received

#### Verify Email Delivery
- Check spam/junk folder
- Confirm sender email is whitelisted
- Test with manual trigger first

#### Update Credentials
If any secrets expire or need rotation:
1. Update the GitHub Secret
2. No changes needed in code or workflow
3. Next run will use new credentials

## Workflow File Breakdown

### Triggers in `monthly-invoice.yml`

```yaml
on:
  schedule:
    - cron: '59 23 28-31 * *'    # Automatic monthly run
  workflow_dispatch:               # Manual trigger capability
    inputs:
      year:                       # Optional custom year
      month:                      # Optional custom month
```

### Environment Variables

```yaml
env:
  JIRA_URL: ${{ secrets.JIRA_URL }}
  JIRA_EMAIL: ${{ secrets.JIRA_EMAIL }}
  # ... all required secrets automatically available
```

### Last-Day Detection Logic

```bash
# Checks if tomorrow is the 1st (meaning today is last day of month)
TOMORROW=$(date -d "+1 day" +%d)
if [ "$TOMORROW" = "01" ]; then
  # Proceed with invoice generation
fi
```

## Customization Options

### Add Project Filter
To only include worklogs from specific Jira projects:

```yaml
python jira-invoice.py \
  --year ${{ steps.month.outputs.year }} \
  --month ${{ steps.month.outputs.month }} \
  --rate "$HOURLY_RATE" \
  --project "GAL"  # Add this line
```

### Change Discord Webhook
To send to a different Discord channel, update the `DISCORD_WEBHOOK` secret with the new channel's webhook URL

### Adjust Rate Dynamically
Modify `HOURLY_RATE` secret as needed; takes effect on next workflow run

### Multiple Discord Channels
Create additional webhooks and manually duplicate workflow with different `DISCORD_WEBHOOK` secrets

## Troubleshooting

### Workflow Doesn't Run on Schedule

**Cause**: Workflow dispatch might not be enabled or cron is not in UTC

**Solution**:
1. Verify workflow file is committed to default branch
2. Check cron expression in `monthly-invoice.yml`
3. Use manual trigger to test first

### Discord Notification Not Received

**Cause**: Webhook URL is invalid, expired, or network issue

**Solution**:
1. Verify `DISCORD_WEBHOOK` secret is set and complete
2. Test webhook manually using curl:
   ```bash
   curl -X POST ${{ secrets.DISCORD_WEBHOOK }} \
     -H 'Content-Type: application/json' \
     -d '{"content":"Test message"}'
   ```
3. Check webhook hasn't been revoked in Discord channel settings
4. Verify Discord channel permissions are correct

### Jira Connection Error

**Cause**: Invalid URL, email, or token

**Solution**:
1. Verify `JIRA_URL` doesn't have trailing slash
2. Test Jira API token is valid (not expired)
3. Confirm email has Jira access permissions
4. Check network connectivity to Jira

### No Worklogs Found

**Cause**: User hasn't logged work in that month or wrong user

**Solution**:
1. Verify worklogs exist in Jira for target month
2. Confirm `JIRA_EMAIL` is the correct user account
3. Check if project filter is excluding relevant issues

### Google Drive Upload Fails

**Cause**: Invalid credentials, permissions, or folder ID

**Solution**:
1. Verify `GOOGLE_CREDENTIALS` JSON is properly formatted (entire file contents pasted as single string)
2. Verify `GOOGLE_DRIVE_FOLDER_ID` is correct:
   - Open Google Drive folder in browser
   - Copy ID from URL: `https://drive.google.com/drive/folders/{ID}`
3. Confirm service account has been shared:
   - Check Google Drive folder sharing settings
   - Verify service account email has **Editor** permissions
4. Verify Google Drive API is enabled:
   - Go to Google Cloud Console
   - Check **APIs & Services** → **Enabled APIs & services**
   - Ensure "Google Drive API" is listed
5. Check workflow logs for detailed error message

### Permission Denied on Google Drive

**Cause**: Service account doesn't have access to folder

**Solution**:
1. Get service account email from JSON file (field: `client_email`)
2. In Google Drive folder, click **Share**
3. Add service account email as collaborator
4. Grant **Editor** role
5. Wait a moment for permissions to propagate

## Security Best Practices

1. **Protect Webhook URLs**: Treat `DISCORD_WEBHOOK` like a password - never share it publicly
2. **Protect Credentials JSON**: Treat `GOOGLE_CREDENTIALS` as sensitive - it grants file access
3. **Use Separate Webhooks**: Consider using separate Discord webhooks for different environments
4. **Rotate Credentials**: Periodically update API tokens and service account keys
5. **Audit Access**: Review who has access to the repository and secrets
6. **Monitor Workflow**: Set up alerts for workflow failures
7. **Revoke Access**: Regularly revoke unused service account keys in Google Cloud Console

## Next Steps

1. ✅ Configure all GitHub Secrets
2. ✅ Test with manual workflow dispatch
3. ✅ Monitor first automatic run on last day of month
4. ✅ Verify email delivery and CSV accuracy
5. ✅ Document any custom project filters or recipients
