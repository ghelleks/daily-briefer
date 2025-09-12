import os
import sys
from datetime import date, datetime
from dotenv import load_dotenv

from src.crew_config import create_daily_briefer_crew


def main():
    """Main entry point for the Daily Briefer application."""
    
    # Load environment variables
    load_dotenv()
    
    
    print("🤖 Daily Briefer - AI-Powered Daily Briefing Generator")
    print("=" * 60)
    
    # Get target date from command line or use today
    target_date = date.today()
    if len(sys.argv) > 1:
        try:
            target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
        except ValueError:
            print("❌ Invalid date format. Please use YYYY-MM-DD")
            print("   Example: python main.py 2024-01-15")
            return
    
    print(f"📅 Generating briefing for: {target_date.strftime('%A, %B %d, %Y')}")
    print()
    
    try:
        # Create and configure the crew
        print("🔧 Setting up AI crew...")
        crew = create_daily_briefer_crew(target_date)
        
        # Display crew information
        crew_info = crew.get_crew_info()
        print(f"   • {crew_info['num_agents']} specialized agents")
        print(f"   • {crew_info['num_tasks']} sequential tasks")
        print(f"   • Memory enabled: {crew_info['memory_enabled']}")
        print()
        
        # Execute the briefing generation
        print("🚀 Starting briefing generation...")
        print("   This may take a few minutes depending on data volume...")
        print()
        
        result = crew.kickoff()
        
        print("✅ Daily briefing generated successfully!")
        print()
        print("Daily Briefing:")
        print("-" * 40)
        print(result)
        
    except KeyboardInterrupt:
        print("\n❌ Process interrupted by user")
    except Exception as e:
        print(f"❌ Error generating briefing: {str(e)}")
        print("\n🔍 Troubleshooting:")
        print("   • Check your API credentials (.env file)")
        print("   • Verify internet connectivity")
        print("   • Check Google AI API credentials and model availability")
        print("   • Verify Todoist API key is set in environment")


def print_usage():
    """Print usage information."""
    print("Usage: python main.py [DATE]")
    print()
    print("Arguments:")
    print("  DATE    Target date in YYYY-MM-DD format (optional, defaults to today)")
    print()
    print("Examples:")
    print("  python main.py                    # Generate briefing for today")
    print("  python main.py 2024-01-15        # Generate briefing for January 15, 2024")
    print()
    print("Environment Setup:")
    print("  Create a .env file with your API credentials:")
    print("  - GOOGLE_API_KEY: Your Google AI API key for Gemini models")
    print("  - TODOIST_API_KEY: Your Todoist API key")
    print("  - Google API credentials (for Gmail, Calendar, Workspace)")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print_usage()
    else:
        main()
