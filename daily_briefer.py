import os
import sys
import argparse
from datetime import date, datetime
from dotenv import load_dotenv

from src.crews import create_daily_briefer_crew


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
  - Google API credentials in tokens/credentials.json
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
    """Main entry point for the Daily Briefer application."""
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Configure CrewAI telemetry based on quiet mode
    if args.quiet:
        os.environ['CREWAI_DISABLE_TELEMETRY'] = 'true'
    
    # Load environment variables
    load_dotenv()
    
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
    print("  --help, -h             Show this help message")
    print()
    print("Examples:")
    print("  python daily_briefer.py                    # Generate briefing for today")
    print("  python daily_briefer.py 2024-01-15        # Generate briefing for January 15, 2024")
    print("  python daily_briefer.py --quiet            # Generate briefing with minimal output")
    print("  python daily_briefer.py --verbose          # Generate briefing with detailed progress")
    print()
    print("Environment Setup:")
    print("  Create a .env file with your API credentials:")
    print("  - GOOGLE_API_KEY: Your Google AI API key for Gemini models")
    print("  - TODOIST_API_KEY: Your Todoist API key")
    print("  - Google API credentials in tokens/credentials.json")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print_usage()
        sys.exit(0)
    else:
        sys.exit(main())
