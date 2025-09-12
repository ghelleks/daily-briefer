import os
import sys
import argparse
from datetime import date, datetime
from dotenv import load_dotenv

from src.crews import create_daily_briefer_crew
from src.crews.todo_processing_crew import create_todo_processing_crew


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI-powered daily briefing generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                        Generate briefing for today
  %(prog)s 2024-01-15             Generate briefing for January 15, 2024
  %(prog)s --quiet                Generate briefing with minimal output
  %(prog)s --verbose              Generate briefing with detailed progress

Environment Setup:
  Create a .env file with your API credentials:
  - GOOGLE_API_KEY: Your Google AI API key for Gemini models
  - TODOIST_API_KEY: Your Todoist API key
  - TODOIST_INBOX_EMAIL: Email for forwarding todo emails to Todoist
  - Google API credentials in tokens/credentials.json

Todo Processing:
  %(prog)s --process-todos              Process todo emails (forward & archive)
  %(prog)s --process-todos --dry-run    Preview todo processing
  %(prog)s --process-todos --max-emails 10  Process max 10 todo emails
        """
    )
    
    parser.add_argument(
        'date',
        nargs='?',
        help='Target date in YYYY-MM-DD format (optional, defaults to today)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output with detailed progress information'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Minimize output (only show final briefing)'
    )
    
    parser.add_argument(
        '--process-todos',
        action='store_true',
        help='Process todo emails: forward to Todoist and archive from Gmail'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview mode for todo processing - analyze but don\'t forward/archive'
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


def process_todo_emails(args):
    """Process todo emails by forwarding to Todoist and archiving."""
    
    # Check for required Todoist email configuration
    todoist_email = os.getenv('TODOIST_INBOX_EMAIL')
    if not todoist_email:
        print("❌ Todo processing requires TODOIST_INBOX_EMAIL environment variable")
        print("   Please add it to your .env file:")
        print("   TODOIST_INBOX_EMAIL=your_todoist_inbox@example.com")
        return 1
    
    if not args.quiet:
        print("📧 Todo Email Processing")
        print("=" * 40)
        print(f"   Todoist Email: {todoist_email}")
        print(f"   Days Back: {args.days_back}")
        print(f"   Max Emails: {args.max_emails}")
        print(f"   Dry Run: {'Yes' if args.dry_run else 'No'}")
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


def main():
    """Main entry point for the Daily Briefer application."""
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Configure CrewAI telemetry based on quiet mode
    if args.quiet:
        os.environ['CREWAI_DISABLE_TELEMETRY'] = 'true'
    
    # Load environment variables
    load_dotenv()
    
    # Handle todo processing mode
    if args.process_todos:
        return process_todo_emails(args)
    
    if not args.quiet:
        print("🤖 Daily Briefer - AI-Powered Daily Briefing Generator")
        print("=" * 60)
    
    # Validate environment
    issues = validate_environment()
    if issues:
        print("❌ Environment validation failed:")
        for issue in issues:
            print(f"   • {issue}")
        print("\n💡 Please check the documentation for setup instructions.")
        return 1
    
    # Get target date from command line or use today
    target_date = date.today()
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print("❌ Invalid date format. Please use YYYY-MM-DD")
            print("   Example: python daily_briefer.py 2024-01-15")
            return 1
    
    if not args.quiet:
        print(f"📅 Generating briefing for: {target_date.strftime('%A, %B %d, %Y')}")
        print()
    
    try:
        # Create and configure the crew
        if args.verbose and not args.quiet:
            print("🔧 Setting up AI crew...")
        
        crew = create_daily_briefer_crew(target_date, verbose=not args.quiet)
        
        # Display crew information
        if args.verbose and not args.quiet:
            crew_info = crew.get_crew_info()
            print(f"   • {crew_info['num_agents']} specialized agents")
            print(f"   • {crew_info['num_tasks']} sequential tasks")
            print(f"   • Memory enabled: {crew_info['memory_enabled']}")
            print()
        
        # Execute the briefing generation
        if not args.quiet:
            print("🚀 Starting briefing generation...")
            print("   This may take a few minutes depending on data volume...")
            print()
        
        # Prepare inputs with verbosity settings
        inputs = {
            'verbose': args.verbose,
            'quiet': args.quiet
        }
        
        result = crew.kickoff(inputs=inputs)
        
        if not args.quiet:
            print("✅ Daily briefing generated successfully!")
            print()
            print("Daily Briefing:")
            print("-" * 40)
        
        print(result)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Process interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Error generating briefing: {str(e)}")
        if args.verbose:
            import traceback
            print("\n🔍 Full error details:")
            traceback.print_exc()
        else:
            print("\n🔍 Troubleshooting:")
            print("   • Check your API credentials (.env file)")
            print("   • Verify internet connectivity")
            print("   • Check Google AI API credentials and model availability")
            print("   • Verify Todoist API key is set in environment")
            print("   • Run with --verbose for detailed error information")
        return 1


def print_usage():
    """Print usage information for the daily briefer."""
    print("Daily Briefer - AI-Powered Daily Briefing Generator")
    print()
    print("Usage: python daily_briefer.py [DATE] [OPTIONS]")
    print()
    print("Arguments:")
    print("  DATE                   Target date in YYYY-MM-DD format (optional, defaults to today)")
    print()
    print("Options:")
    print("  --verbose, -v          Enable verbose output with detailed progress")
    print("  --quiet, -q            Minimize output (only show final briefing)")
    print("  --process-todos        Process todo emails: forward to Todoist and archive")
    print("  --dry-run              Preview mode for todo processing (no actual changes)")
    print("  --max-emails N         Maximum number of todo emails to process (default: 20)")
    print("  --days-back N          Number of days to look back for emails (default: 7)")
    print("  --help, -h             Show this help message")
    print()
    print("Examples:")
    print("  python daily_briefer.py                    # Generate briefing for today")
    print("  python daily_briefer.py 2024-01-15        # Generate briefing for January 15, 2024")
    print("  python daily_briefer.py --quiet            # Generate briefing with minimal output")
    print("  python daily_briefer.py --verbose          # Generate briefing with detailed progress")
    print("  python daily_briefer.py --process-todos    # Process todo emails")
    print("  python daily_briefer.py --process-todos --dry-run  # Preview todo processing")
    print()
    print("Environment Setup:")
    print("  Create a .env file with your API credentials:")
    print("  - GOOGLE_API_KEY: Your Google AI API key for Gemini models")
    print("  - TODOIST_API_KEY: Your Todoist API key")
    print("  - TODOIST_INBOX_EMAIL: Email for forwarding todo emails to Todoist")
    print("  - Google API credentials in tokens/credentials.json")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print_usage()
        sys.exit(0)
    else:
        sys.exit(main())
