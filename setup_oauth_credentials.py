#!/usr/bin/env python3
"""
OAuth Credentials Setup Script for Daily Briefer
This script helps set up OAuth 2.0 credentials for Gmail and Calendar access
"""

import os
import json
import webbrowser
from pathlib import Path


def print_header():
    print("=" * 50)
    print("  Daily Briefer - OAuth Setup")
    print("=" * 50)
    print()


def check_existing_credentials():
    """Check if credentials already exist"""
    files_to_check = [
        "credentials.json",
        "oauth_credentials.json", 
        "token.json"
    ]
    
    existing = []
    for file in files_to_check:
        if os.path.exists(file):
            existing.append(file)
    
    if existing:
        print(f"⚠️  Found existing credential files: {', '.join(existing)}")
        response = input("Do you want to continue and potentially overwrite them? (y/N): ")
        if response.lower() != 'y':
            print("Exiting...")
            exit(1)
    
    return existing


def create_oauth_instructions():
    """Create step-by-step OAuth setup instructions"""
    
    instructions = """
🔧 OAUTH 2.0 SETUP INSTRUCTIONS

Follow these steps to set up OAuth 2.0 credentials for Gmail and Calendar access:

1. 📱 GO TO GOOGLE CLOUD CONSOLE
   → Open: https://console.cloud.google.com
   → Select your project (or create one if needed)

2. 🔌 ENABLE REQUIRED APIS (if not already done)
   → Go to: APIs & Services > Library
   → Search and enable:
     - Gmail API
     - Google Calendar API
     - Google Drive API (for document access)

3. 🔒 CONFIGURE OAUTH CONSENT SCREEN
   → Go to: APIs & Services > OAuth consent screen
   → Choose User Type:
     - Internal (if you have Google Workspace)
     - External (for personal Gmail accounts)
   → Fill in required fields:
     - App name: "Daily Briefer"
     - User support email: your email
     - Developer contact: your email
   → Add scopes (if asked):
     - gmail.readonly
     - calendar.readonly
     - drive.readonly
   → Add test users (for External apps):
     - Add your own email address

4. 📋 CREATE OAUTH 2.0 CREDENTIALS
   → Go to: APIs & Services > Credentials
   → Click: + CREATE CREDENTIALS > OAuth 2.0 Client ID
   → Application type: Desktop application
   → Name: "Daily Briefer Desktop"
   → Click: CREATE

5. 💾 DOWNLOAD CREDENTIALS
   → Click the download button (⬇️) next to your new OAuth client
   → Save the file as 'credentials.json' in your project directory

6. ✅ VERIFY SETUP
   → Make sure you have 'credentials.json' in your project root
   → Run: uv run python main.py
   → First run will open browser for OAuth consent

📝 CREDENTIAL FILES EXPLAINED:
   - credentials.json: OAuth 2.0 client configuration (download from Google)
   - token.json: Access/refresh tokens (created automatically after first auth)
   - .env: API keys and configuration

🔗 HELPFUL LINKS:
   - Google Cloud Console: https://console.cloud.google.com
   - OAuth 2.0 Setup Guide: https://developers.google.com/gmail/api/quickstart/python
   - API Scopes Reference: https://developers.google.com/identity/protocols/oauth2/scopes
"""
    
    return instructions


def create_test_credentials():
    """Create a template credentials.json file"""
    
    template = {
        "installed": {
            "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
            "project_id": "your-project-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "YOUR_CLIENT_SECRET",
            "redirect_uris": ["http://localhost"]
        }
    }
    
    with open("credentials_template.json", "w") as f:
        json.dump(template, f, indent=2)
    
    print("✅ Created credentials_template.json as reference")
    return "credentials_template.json"


def validate_credentials():
    """Validate existing credentials.json file"""
    
    if not os.path.exists("credentials.json"):
        print("❌ credentials.json not found")
        return False
    
    try:
        with open("credentials.json", "r") as f:
            creds = json.load(f)
        
        # Check for required fields
        required_fields = ["installed"]
        if "installed" in creds:
            required_installed_fields = [
                "client_id", 
                "client_secret", 
                "auth_uri", 
                "token_uri"
            ]
            
            for field in required_installed_fields:
                if field not in creds["installed"]:
                    print(f"❌ Missing required field: installed.{field}")
                    return False
        else:
            print("❌ Missing 'installed' section in credentials.json")
            return False
        
        print("✅ credentials.json appears valid")
        return True
        
    except json.JSONDecodeError:
        print("❌ credentials.json is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ Error validating credentials.json: {e}")
        return False


def open_console():
    """Open Google Cloud Console in browser"""
    response = input("🌐 Open Google Cloud Console in browser? (y/N): ")
    if response.lower() == 'y':
        webbrowser.open("https://console.cloud.google.com")
        print("✅ Opened Google Cloud Console")


def main():
    print_header()
    
    # Check existing files
    existing = check_existing_credentials()
    
    # Show instructions
    print(create_oauth_instructions())
    
    # Create template file
    create_test_credentials()
    
    # Open browser if requested
    open_console()
    
    # Validate existing credentials if present
    if "credentials.json" in existing:
        print("\n" + "="*50)
        print("VALIDATING EXISTING CREDENTIALS")
        print("="*50)
        validate_credentials()
    
    print("\n" + "="*50)
    print("SETUP COMPLETE")
    print("="*50)
    print()
    print("📋 Next steps:")
    print("1. Follow the instructions above to create OAuth credentials")
    print("2. Download and save as 'credentials.json'")
    print("3. Update GOOGLE_AI_API_KEY in .env file")
    print("4. Run: uv run python main.py")
    print()
    print("📁 Files in project:")
    for file in ["credentials.json", "credentials_template.json", "token.json", ".env"]:
        status = "✅" if os.path.exists(file) else "❌"
        print(f"   {status} {file}")


if __name__ == "__main__":
    main()