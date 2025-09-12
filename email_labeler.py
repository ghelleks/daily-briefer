#!/usr/bin/env python3
"""
Email Labeler - Automated Gmail Email Classification and Labeling

This script processes unlabeled emails in Gmail and applies appropriate classification 
labels using the same knowledge system as the daily briefer.

Usage:
    python email_labeler.py [OPTIONS]

Examples:
    python email_labeler.py                    # Process last 7 days, max 50 emails
    python email_labeler.py --days 3           # Process last 3 days
    python email_labeler.py --max-emails 100   # Process up to 100 emails
    python email_labeler.py --dry-run          # Preview what would be labeled
"""

import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

from src.crews import create_email_labeling_crew


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Automated Gmail email classification and labeling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                        Process last 7 days, max 50 emails
  %(prog)s --days 3               Process last 3 days  
  %(prog)s --max-emails 100       Process up to 100 emails
  %(prog)s --dry-run              Preview what would be labeled (read-only)

Environment Setup:
  Create a .env file with your API credentials:
  - GOOGLE_API_KEY: Your Google AI API key for Gemini models
  - Google API credentials in tokens/credentials.json
        """
    )
    
    parser.add_argument(
        '--days', '-d',
        type=int,
        default=7,
        help='Number of days to look back for emails (default: 7)'
    )
    
    parser.add_argument(
        '--max-emails', '-m',
        type=int,
        default=50,
        help='Maximum number of emails to process (default: 50)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be labeled without making changes'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Minimize output (only show summary)'
    )
    
    return parser.parse_args()


def validate_environment():
    """Validate that required environment and files are available."""
    issues = []
    
    # Check for required directories
    if not os.path.exists('tokens'):
        issues.append("Missing 'tokens' directory - please create it and add your Google credentials")
    
    # Check for Google credentials
    if not os.path.exists('tokens/credentials.json'):
        issues.append("Missing 'tokens/credentials.json' - please add your Google API credentials")
    
    # Check for .env file
    if not os.path.exists('.env'):
        issues.append("Missing '.env' file - please create it with your API keys")
    
    return issues


def main():
    """Main entry point for the Email Labeler application."""
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Load environment variables
    load_dotenv()
    
    if not args.quiet:
        print("📧 Email Labeler - Automated Gmail Classification")
        print("=" * 55)
    
    # Validate environment
    issues = validate_environment()
    if issues:
        print("❌ Environment validation failed:")
        for issue in issues:
            print(f"   • {issue}")
        print("\n💡 Please check the documentation for setup instructions.")
        return 1
    
    if not args.quiet:
        print(f"📅 Processing emails from last {args.days} days")
        print(f"📊 Maximum emails to process: {args.max_emails}")
        if args.dry_run:
            print("🔍 DRY RUN MODE: No labels will be applied")
        print()
    
    try:
        # Create and configure the email labeling crew
        if args.verbose and not args.quiet:
            print("🔧 Setting up email labeling crew...")
        
        crew = create_email_labeling_crew(
            days_back=args.days,
            max_emails=args.max_emails
        )
        
        if args.verbose and not args.quiet:
            crew_info = crew.get_crew_info()
            print(f"   • {crew_info['num_agents']} specialized agent")
            print(f"   • {crew_info['num_tasks']} labeling task")
            print(f"   • Memory enabled: {crew_info['memory_enabled']}")
            print()
        
        # Execute the email labeling process
        if not args.quiet:
            print("🚀 Starting email labeling process...")
            if args.max_emails > 50:
                print("   ⚠️  Processing large batch - this may take several minutes...")
            print()
        
        # Prepare inputs
        inputs = {
            'dry_run': args.dry_run,
            'verbose': args.verbose
        }
        
        result = crew.kickoff(inputs=inputs)
        
        if not args.quiet:
            print("✅ Email labeling completed successfully!")
            print()
            print("Labeling Report:")
            print("-" * 45)
        
        print(result)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Process interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Error during email labeling: {str(e)}")
        if args.verbose:
            import traceback
            print("\n🔍 Full error details:")
            traceback.print_exc()
        else:
            print("\n🔍 Troubleshooting:")
            print("   • Check your Google API credentials and authentication")
            print("   • Verify internet connectivity")
            print("   • Check Gmail API access and permissions")
            print("   • Run with --verbose for detailed error information")
        return 1


def print_usage():
    """Print usage information for the email labeler."""
    print("Email Labeler - Automated Gmail Classification")
    print()
    print("Usage: python email_labeler.py [OPTIONS]")
    print()
    print("Options:")
    print("  --days, -d DAYS        Number of days to look back (default: 7)")
    print("  --max-emails, -m NUM   Maximum emails to process (default: 50)")
    print("  --dry-run              Preview mode - don't apply labels")
    print("  --verbose, -v          Enable verbose output")
    print("  --quiet, -q            Minimize output")
    print("  --help, -h             Show this help message")
    print()
    print("Examples:")
    print("  python email_labeler.py                    # Process last 7 days")
    print("  python email_labeler.py --days 3           # Process last 3 days")
    print("  python email_labeler.py --max-emails 100   # Process 100 emails")
    print("  python email_labeler.py --dry-run          # Preview only")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print_usage()
        sys.exit(0)
    else:
        sys.exit(main())