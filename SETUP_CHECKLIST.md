# ✅ Setup Checklist

Use this checklist to track your setup progress.

## Part 1: Code Review & Preparation
- [ ] Review updated `jira-invoice.py` with email functionality
- [ ] Verify `requirements.txt` contains needed dependencies
- [ ] Read through `README.md` for understanding
- [ ] Review `SETUP_GUIDE.md` for detailed steps

## Part 2: Gather Credentials
- [ ] Generate Jira API Token from https://id.atlassian.com/manage-profile/security/api-tokens
- [ ] Create Discord server/channel for invoice notifications
- [ ] Get Discord Webhook URL from the channel settings
- [ ] List your hourly billing rate

## Part 3: Configure GitHub Secrets

Navigate to: **Settings → Secrets and variables → Actions** and create these secrets:

### Jira Configuration
- [ ] `JIRA_URL`: Jira instance URL (e.g., `https://company.atlassian.net`)
- [ ] `JIRA_EMAIL`: Your Jira email account
- [ ] `JIRA_API_TOKEN`: Jira API token from step 2

### Billing Configuration
- [ ] `HOURLY_RATE`: Hourly billing rate (e.g., `50`)

### Discord Configuration
- [ ] `DISCORD_WEBHOOK`: Discord webhook URL (see instructions below)

### Google Drive Configuration
- [ ] `GOOGLE_CREDENTIALS`: Service account JSON (see "Creating Google Service Account" below)
- [ ] `GOOGLE_DRIVE_FOLDER_ID`: Google Drive folder ID where CSVs will be uploaded

**Verification**: All 7 secrets should now appear in your repository secrets page.

### Creating Discord Webhook URL

1. Open your Discord server and navigate to the channel where you want invoice notifications
2. Click the channel settings icon (gear icon)
3. Select **Integrations** → **Webhooks**
4. Click **New Webhook**
5. Name it "Invoice Bot" (or preferred name)
6. Click **Copy Webhook URL**
7. Paste the URL into GitHub Secret `DISCORD_WEBHOOK`

The webhook URL looks like: `https://discord.com/api/webhooks/123456789/abcdefghijklmnop`

### Creating Google Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable Google Drive API:
   - Click **APIs & Services** → **Library**
   - Search for "Google Drive API"
   - Click **Enable**
4. Create service account credentials:
   - Click **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **Service Account**
   - Fill in service account name (e.g., "invoice-bot")
   - Click **Create and Continue**
   - Skip optional steps, click **Done**
5. Create JSON key:
   - Go to **APIs & Services** → **Credentials**
   - Find your service account in the list
   - Click the service account email
   - Go to **Keys** tab
   - Click **Add Key** → **Create new key**
   - Choose **JSON**
   - This downloads a JSON file
6. Share Google Drive folder:
   - Create or open a Google Drive folder for invoices
   - Copy the folder ID from URL: `https://drive.google.com/drive/folders/{FOLDER_ID}`
   - Share the folder with service account email (from JSON file)
   - Grant **Editor** permissions
7. Add to GitHub Secrets:
   - **For `GOOGLE_CREDENTIALS`**: Open downloaded JSON file, copy entire contents, paste into secret
   - **For `GOOGLE_DRIVE_FOLDER_ID`**: Paste the folder ID

## Part 4: Test the Workflow

### Option A: Manual Test (Recommended)
- [ ] Go to **Actions** tab in your repository
- [ ] Select **"Generate and Send Monthly Invoice to Discord"** workflow
- [ ] Click **"Run workflow"** button
- [ ] Leave year/month blank (or specify for testing)
- [ ] Click **"Run workflow"** to confirm
- [ ] Monitor the workflow execution
- [ ] Check Discord channel for the notification
- [ ] Verify all invoice details are displayed
- [ ] Check Google Drive folder for uploaded CSV file
- [ ] Download artifact CSV to verify content

### Option B: Review Workflow Execution (if already ran)
- [ ] Go to **Actions** tab
- [ ] Click on the completed workflow run
- [ ] Review logs for any errors (including Google Drive upload)
- [ ] Check Discord channel for notification
- [ ] Check Google Drive folder for uploaded CSV file
- [ ] Download artifact CSV to verify content

## Part 5: Verify Discord Notification & Google Drive Upload
- [ ] Check Discord channel for message "Monthly Invoice Generated"
- [ ] Verify all invoice details are displayed (hours, amount, entries, rate)
- [ ] Click link to download artifact CSV from GitHub
- [ ] Verify CSV attachment and contents
- [ ] Open Google Drive folder
- [ ] Confirm CSV file is present
- [ ] Verify file can be opened and contains correct data

## Part 6: Prepare for Automation
- [ ] Note the last day of next month
- [ ] Workflow will automatically run at 23:59 UTC
- [ ] Set up calendar reminder to monitor Discord next month
- [ ] Plan to review Actions tab after first automatic run

## Part 7: Documentation & Handoff (Optional)
- [ ] Share setup documentation with team
- [ ] Document any custom settings or modifications
- [ ] Create internal wiki entry for troubleshooting
- [ ] Assign backup admin for workflow maintenance

## Part 8: Monitoring Setup (Optional but Recommended)
- [ ] Enable GitHub email notifications for this repository
- [ ] Subscribe to workflow run notifications
- [ ] Document escalation procedure if invoice doesn't arrive
- [ ] Set monthly calendar reminder to spot-check

## Common Issues & Quick Fixes

### Workflow Doesn't Appear in Actions Tab
**Action**: Ensure workflow file is committed to main/default branch
```bash
git add .github/workflows/monthly-invoice.yml
git commit -m "Add monthly invoice workflow"
git push
```

### Discord Webhook Shows as Invalid
**Action**: Verify webhook URL is complete and hasn't been copied partially

### No Message in Discord Channel
**Action**: Check that Discord webhook secret is correctly set and workflow executed successfully

### Google Drive Upload Fails
**Action**: 
1. Verify `GOOGLE_CREDENTIALS` JSON is correctly formatted (paste entire file contents)
2. Verify `GOOGLE_DRIVE_FOLDER_ID` is correct (from URL: `https://drive.google.com/drive/folders/{ID}`)
3. Ensure service account has Editor access to the folder
4. Check workflow logs for detailed error message
5. Verify Google Drive API is enabled in Google Cloud Console

### Google File Already Exists Error
**Action**: The workflow will overwrite existing files with the same name. This is expected behavior for monthly updates.

### Secret Shows as "Not Found" During Workflow
**Action**: Wait a few minutes after creating secret; GitHub indexes them periodically

---

## Next Steps After Setup

1. ✅ **Immediate**: Test with manual workflow dispatch
2. ✅ **First Month**: Monitor automatic run on last day of month
3. ✅ **Ongoing**: Review Actions tab monthly for any errors
4. ✅ **As Needed**: Update secrets when credentials change

---

## Support Resources

- **Python Script Help**: See `README.md`
- **Setup Instructions**: See `SETUP_GUIDE.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Jira API Docs**: https://developer.atlassian.com/cloud/jira/rest/v3/

---

**Estimated Setup Time**: 15-20 minutes
**Last Updated**: March 2, 2026
