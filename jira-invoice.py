#!/usr/bin/env python3
"""
Jira Worklog Invoice Generator

Fetches worklogs from Jira for a specific month and generates an invoice CSV.
Usage:
    python jira_invoice.py --year 2026 --month 2 --rate 50 --output invoice_feb_2026.csv

Requirements:
    pip install requests python-dateutil
"""

import os
import sys
import csv
import argparse
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from dateutil import rrule
import requests
from requests.auth import HTTPBasicAuth
import json


class JiraInvoiceGenerator:
    def __init__(self, jira_url, email, api_token):
        """
        Initialize Jira connection
        
        Args:
            jira_url: Base URL of your Jira instance (e.g., https://bundlecore.atlassian.net)
            email: Your Jira email
            api_token: Jira API token (generate from https://id.atlassian.com/manage-profile/security/api-tokens)
        """
        self.jira_url = jira_url.rstrip('/')
        self.auth = HTTPBasicAuth(email, api_token)
        self.headers = {"Accept": "application/json"}
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update(self.headers)
    
    def get_current_user(self):
        """Get current user's account ID"""
        url = f"{self.jira_url}/rest/api/3/myself"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()['accountId']
    
    def get_worklogs(self, start_date, end_date, project=None):
        """
        Fetch all worklogs for the current user within date range
        
        Args:
            start_date: datetime.date object
            end_date: datetime.date object
            project: Optional project key to filter (e.g., 'GAL')
        
        Returns:
            List of worklog entries
        """
        # Use a bounded JQL query required by Jira Cloud
        # Restrict by created date (not worklogDate, which is not supported)
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        if project:
            jql = f"project = {project} AND created >= \"{start_str}\" AND created <= \"{end_str}\" ORDER BY updated DESC"
        else:
            jql = f"created >= \"{start_str}\" AND created <= \"{end_str}\" ORDER BY updated DESC"
        
        worklogs = []
        start_at = 0
        max_results = 100
        
        while True:
            url = f"{self.jira_url}/rest/api/3/search"
            params = {
                'jql': jql,
                'startAt': start_at,
                'maxResults': max_results,
                'fields': 'summary,timeoriginalestimate,timeestimate,timespent,project'
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if not data.get('issues'):
                break
            for issue in data['issues']:
                issue_key = issue['key']
                summary = issue['fields']['summary']
                project_key = issue['fields']['project']['key']
                # Get worklog details for this issue
                worklog_url = f"{self.jira_url}/rest/api/3/issue/{issue_key}/worklog"
                worklog_response = self.session.get(worklog_url)
                worklog_response.raise_for_status()
                worklog_data = worklog_response.json()
                # Filter worklogs by current user and date range
                for worklog in worklog_data['worklogs']:
                    if worklog['author']['accountId'] == self.get_current_user():
                        worklog_date = datetime.strptime(worklog['started'][:10], '%Y-%m-%d').date()
                        if start_date <= worklog_date <= end_date:
                            time_spent_seconds = worklog['timeSpentSeconds']
                            time_spent_hours = time_spent_seconds / 3600
                            
                            worklogs.append({
                                'issue_key': issue_key,
                                'summary': summary,
                                'project': project_key,
                                'date': worklog_date,
                                'time_spent_seconds': time_spent_seconds,
                                'time_spent_hours': time_spent_hours,
                            })
            
            # Check if there are more results
            if len(data['issues']) < max_results:
                break
            
            start_at += max_results
        
        return worklogs
    
    def generate_invoice_csv(self, worklogs, output_file, hourly_rate):
        """
        Generate invoice CSV from worklogs
        
        Args:
            worklogs: List of worklog dictionaries
            output_file: Output CSV filename
            hourly_rate: Billing rate per hour
        """
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Issue Key', 'Summary', 'Date', 'Time Spent (Hours)', 'Rate (USD/hr)', 'Amount (USD)', 'Project']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            total_hours = 0
            total_amount = 0
            
            # Sort by date
            sorted_worklogs = sorted(worklogs, key=lambda x: x['date'])
            
            for worklog in sorted_worklogs:
                amount = worklog['time_spent_hours'] * hourly_rate
                total_hours += worklog['time_spent_hours']
                total_amount += amount
                
                writer.writerow({
                    'Issue Key': worklog['issue_key'],
                    'Summary': worklog['summary'],
                    'Date': worklog['date'].isoformat(),
                    'Time Spent (Hours)': round(worklog['time_spent_hours'], 2),
                    'Rate (USD/hr)': hourly_rate,
                    'Amount (USD)': round(amount, 2),
                    'Project': worklog['project']
                })
            
            # Write total row
            writer.writerow({
                'Issue Key': 'TOTAL:',
                'Summary': '',
                'Date': '',
                'Time Spent (Hours)': round(total_hours, 2),
                'Rate (USD/hr)': '',
                'Amount (USD)': round(total_amount, 2),
                'Project': ''
            })
        
        return total_hours, total_amount


def main():
    parser = argparse.ArgumentParser(description='Generate invoice from Jira worklogs')

    parser.add_argument('--year', type=int, required=True, help='Year (e.g., 2026)')
    parser.add_argument('--month', type=int, required=True, help='Month (1-12)')
    parser.add_argument('--rate', type=float, default=None, help='Hourly rate in USD (or set HOURLY_RATE env var)')
    parser.add_argument('--output', type=str, default=None, help='Output CSV filename')
    parser.add_argument('--project', type=str, default=None, help='Jira project key (e.g., GAL)')
    parser.add_argument('--jira-url', type=str, default=os.getenv('JIRA_URL'), 
                       help='Jira URL (or set JIRA_URL env var)')
    parser.add_argument('--email', type=str, default=os.getenv('JIRA_EMAIL'), 
                       help='Jira email (or set JIRA_EMAIL env var)')
    parser.add_argument('--token', type=str, default=os.getenv('JIRA_API_TOKEN'), 
                       help='Jira API token (or set JIRA_API_TOKEN env var)')
    
    args = parser.parse_args()
    
    # Get hourly rate from args or environment
    hourly_rate = args.rate or os.getenv('HOURLY_RATE')
    if not hourly_rate:
        print("Error: Hourly rate not provided. Use --rate argument or set HOURLY_RATE env var")
        sys.exit(1)
    hourly_rate = float(hourly_rate)
    
    # Validate required Jira parameters
    if not all([args.jira_url, args.email, args.token]):
        print("Error: Missing Jira credentials. Provide via arguments or environment variables:")
        print("  --jira-url or JIRA_URL")
        print("  --email or JIRA_EMAIL")
        print("  --token or JIRA_API_TOKEN")
        sys.exit(1)
    
    # Calculate date range
    start_date = date(args.year, args.month, 1)
    if args.month == 12:
        end_date = date(args.year + 1, 1, 1) - relativedelta(days=1)
    else:
        end_date = date(args.year, args.month + 1, 1) - relativedelta(days=1)
    
    print(f"Fetching worklogs from {start_date} to {end_date}...")
    
    # Generate output filename if not provided
    if not args.output:
        month_name = datetime(args.year, args.month, 1).strftime('%B').lower()
        args.output = f"invoice_{month_name}_{args.year}.csv"
    
    try:
        # Initialize generator
        generator = JiraInvoiceGenerator(args.jira_url, args.email, args.token)
        
        # Fetch worklogs
        worklogs = generator.get_worklogs(start_date, end_date, args.project)
        
        if not worklogs:
            print("No worklogs found for the specified period.")
            sys.exit(0)
        
        print(f"Found {len(worklogs)} worklog entries")
        
        # Generate CSV
        total_hours, total_amount = generator.generate_invoice_csv(
            worklogs, args.output, hourly_rate
        )
        
        print(f"\n✓ Invoice generated: {args.output}")
        print(f"  Total hours: {total_hours:.2f}")
        print(f"  Total amount: ${total_amount:.2f} (at ${hourly_rate}/hr)")
        print(f"  Entries: {len(worklogs)}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Jira: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
