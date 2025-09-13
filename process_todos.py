#!/usr/bin/env python3
"""
Todo Processing Script - Standalone todo email processing crew

This script provides a dedicated entry point for processing todo emails,
allowing it to be run independently or integrated into larger workflows.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

from src.crews.todo_processing_crew import create_todo_processing_crew


def parse_arguments():
    """Parse command line arguments for todo processing."""
    parser = argparse.ArgumentParser(
        description="Process todo emails by forwarding to Todoist and archiving from Gmail",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                        Process todo emails with default settings
  %(prog)s --dry-run              Preview what would be processed
  %(prog)s --max-emails 10        Process up to 10 todo emails
  %(prog)s --days-back 14         Look back 14 days for todo emails
  %(prog)s --quiet                Minimize output

Environment Setup:
  Create a .env file with:
  - TODOIST_API_KEY: Your Todoist API key
  - TODOIST_INBOX_EMAIL: Email for forwarding todo emails to Todoist
  - Google API credentials in tokens/credentials.json
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview mode - analyze emails but don\'t forward or archive'
    )
    
    parser.add_argument(
        '--max-emails',
        type=int,
        default=20,
        help='Maximum number of todo emails to process (default: 20)'
    )
    
    parser.add_argument(
        '--days-back',
        type=int,
        default=7,
        help='Number of days to look back for todo emails (default: 7)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output with detailed progress information'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Minimize output (only show final report)'
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
    
    # Check for Todoist email configuration
    todoist_email = os.getenv('TODOIST_INBOX_EMAIL')
    if not todoist_email:
        issues.append("Missing TODOIST_INBOX_EMAIL in .env file")
    
    return issues


def main():
    """Main entry point for the todo processing script."""
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Configure CrewAI telemetry based on quiet mode
    if args.quiet:
        os.environ['CREWAI_DISABLE_TELEMETRY'] = 'true'
    
    # Load environment variables
    load_dotenv()
    
    if not args.quiet:
        print("📧 Todo Email Processor - Automated Todoist Integration")
        print("=" * 55)
    
    # Validate environment
    issues = validate_environment()
    if issues:
        print("❌ Environment validation failed:")
        for issue in issues:
            print(f"   • {issue}")
        print("\n💡 Please check the documentation for setup instructions.")
        return 1
    
    # Get Todoist email from environment
    todoist_email = os.getenv('TODOIST_INBOX_EMAIL')
    
    if not args.quiet:
        print(f"📧 Configuration:")
        print(f"   • Todoist Email: {todoist_email}")
        print(f"   • Days Back: {args.days_back}")
        print(f"   • Max Emails: {args.max_emails}")
        print(f"   • Dry Run: {'Yes' if args.dry_run else 'No'}")
        print()
    
    try:
        # Create and configure the todo processing crew
        if args.verbose and not args.quiet:
            print("🔧 Setting up todo processing crew...")
        
        crew = create_todo_processing_crew(
            todoist_email=todoist_email,
            days_back=args.days_back,
            max_emails=args.max_emails,
            dry_run=args.dry_run,
            verbose=not args.quiet
        )
        
        # Display crew information
        if args.verbose and not args.quiet:
            crew_info = crew.get_crew_info()
            print(f"   • {crew_info['num_agents']} specialized agents")
            print(f"   • {crew_info['num_tasks']} sequential tasks")
            print(f"   • Todoist Email: {crew_info['todoist_email']}")
            print()
        
        # Execute the todo processing
        if not args.quiet:
            action = "Analyzing" if args.dry_run else "Processing"
            print(f"🚀 {action} todo emails...")
            print("   This may take a few minutes depending on email volume...")
            print()
        
        # Prepare inputs
        inputs = {
            'verbose': args.verbose,
            'quiet': args.quiet
        }
        
        result = crew.kickoff(inputs=inputs)
        
        if not args.quiet:
            success_msg = "analyzed" if args.dry_run else "processed"
            print(f"✅ Todo emails {success_msg} successfully!")
            print()
            print("Todo Processing Report:")
            print("-" * 40)
        
        print(result)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Process interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Error processing todo emails: {str(e)}")
        if args.verbose:
            import traceback
            print("\n🔍 Full error details:")
            traceback.print_exc()
        else:
            print("\n🔍 Troubleshooting:")
            print("   • Check Gmail API credentials and permissions")
            print("   • Verify TODOIST_INBOX_EMAIL is configured correctly")
            print("   • Ensure todo emails exist in the specified time period")
            print("   • Check network connectivity")
            print("   • Run with --verbose for detailed error information")
        return 1


def print_usage():
    """Print usage information for the todo processor."""
    print("Todo Email Processor - Automated Todoist Integration")
    print()
    print("Usage: python process_todos.py [OPTIONS]")
    print()
    print("Options:")
    print("  --dry-run              Preview mode - analyze emails but don't forward/archive")
    print("  --max-emails N         Maximum number of todo emails to process (default: 20)")
    print("  --days-back N          Number of days to look back for emails (default: 7)")
    print("  --verbose, -v          Enable verbose output with detailed progress")
    print("  --quiet, -q            Minimize output (only show final report)")
    print("  --help, -h             Show this help message")
    print()
    print("Examples:")
    print("  python process_todos.py                    # Process todos with default settings")
    print("  python process_todos.py --dry-run          # Preview what would be processed")
    print("  python process_todos.py --max-emails 10    # Process up to 10 emails")
    print("  python process_todos.py --days-back 14     # Look back 14 days")
    print("  python process_todos.py --quiet            # Minimal output")
    print()
    print("Environment Setup:")
    print("  Create a .env file with your API credentials:")
    print("  - TODOIST_API_KEY: Your Todoist API key")
    print("  - TODOIST_INBOX_EMAIL: Email for forwarding todo emails to Todoist")
    print("  - Google API credentials in tokens/credentials.json")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print_usage()
        sys.exit(0)
    else:
        sys.exit(main())