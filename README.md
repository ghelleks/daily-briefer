# Daily Briefer

Daily Briefer is an AI-powered personal assistant that transforms your digital chaos into clear, actionable daily briefings. Think of it as having an executive assistant who reads through all your emails, checks your calendar, reviews your tasks, and creates a personalized briefing document that tells you exactly what you need to know and do today.

## What Daily Briefer Does for You

**Turns Email Overload into Digestible Insights**: Your emails are automatically categorized and summarized in a "Today in Tabs" style - conversational, engaging, and surprisingly enjoyable to read. No more drowning in your inbox.

**Creates Your Daily Game Plan**: Combines your calendar events, pending tasks, and email-derived action items into a single, prioritized list so you know exactly what needs your attention.

**Provides Context for Everything**: Every meeting in your agenda comes with relevant background information, related documents, and preparation notes gathered from your recent emails and shared files.

**Saves Hours of Manual Review**: Instead of spending 30-60 minutes each morning reviewing emails, calendar, and tasks, get a comprehensive briefing in under 5 minutes.

## How Your Daily Briefing Works

Daily Briefer uses a team of AI specialists working in sequence to create your briefing:

1. **Data Collector** - Gathers your emails, calendar events, and tasks
2. **Email Classification Specialist** - Sorts emails into 8 smart categories
3. **Email Summary Writer** - Creates engaging "Today in Tabs" style summaries
4. **Calendar Analyst** - Analyzes your schedule and gathers meeting context
5. **Task Manager** - Reviews your existing tasks and suggests new ones
6. **Document Assembler** - Combines everything into your final briefing

### The Email Categories That Make Sense

Your emails are automatically sorted into categories that actually help you prioritize:

- **todo** - Things requiring action (school forms, payment requests, etc.)
- **2min** - Quick tasks you can knock out immediately
- **review** - Documents and decisions that need your thoughtful input
- **news** - Industry updates and articles worth knowing about
- **fyi** - Status updates and confirmations that keep you informed
- **promotions** - Marketing emails and offers
- **forums** - Community discussions and social platform updates
- **meetings** - Calendar invites and meeting-related communications

### "Today in Tabs" Email Style

Instead of dry bullet points, your email summaries are written in the engaging, conversational style of Rusty Foster's "Today in Tabs" newsletter. This means:
- Rich, clickable links to documents and websites
- Strategic bolding that highlights what matters
- Conversational tone that makes mundane updates actually interesting to read
- Context that helps you understand why each email matters

## Quick Setup

### What You'll Need

- Python 3.13+ and UV package manager
- Google account with Gmail and Calendar
- Todoist account (for task management)
- 10 minutes for initial setup

### Installation Steps

1. **Get the code and install dependencies:**
   ```bash
   git clone <repository-url>
   cd daily-briefer
   uv sync
   ```

2. **Set up your Google access:**
   ```bash
   cp .env.example .env
   python setup_oauth_credentials.py  # Follow the guided setup
   ```

3. **Configure your accounts:**
   - Add your Todoist API key to the `.env` file
   - Add your Google AI API key for the AI processing

4. **Generate your first briefing:**
   ```bash
   uv run python daily_briefer.py
   ```

That's it! Your first briefing will be generated and displayed in your terminal.

## Your Daily Briefing Structure

Every briefing follows the same clear, three-section format so you can quickly find what you need:

### 1. Action Items
**What you need to do today**

- **From Todoist**: Tasks you've already planned that are due today
- **Suggested**: New action items discovered from your emails and calendar events, formatted in Todoist syntax so you can easily add them to your task list

### 2. Email Summary
**What's happening in your inbox, organized by priority**

Written in an engaging "Today in Tabs" style with rich links and strategic formatting:

- **Quick Wins**: 2-minute tasks you can knock out right away
- **Review Needed**: Documents and decisions requiring your thoughtful input
- **FYI**: Status updates and information worth knowing
- **News & Updates**: Industry news and relevant articles
- **Administrative**: Routine notifications and confirmations

### 3. Daily Agenda
**Your schedule with context and preparation notes**

- Chronological list of your calendar events
- Background information gathered from related emails
- Links to relevant documents and attachments
- Open action items from shared documents
- Virtual meeting links and location details

## Sample Briefing Output

Here's what a typical briefing section looks like:

```markdown
## Email Summary

### Review Needed

**Sarah** from the marketing team shared the **Q4 Campaign Deck** 
for your feedback before tomorrow's client presentation. The deck 
includes three creative concepts, and she's specifically looking 
for input on the messaging strategy for the healthcare vertical.

**The Jenkins Project** status doc was updated with some **concerning 
budget variances** that merit a closer look. The infrastructure 
costs are running 23% over budget, and there are some questions 
about the timeline that Tom flagged for review.

### Quick Wins

**Expense approval** for Maria's conference travel is sitting in 
your inbox - just needs a click to approve the $847 for the 
Design Systems Conference next month.
```

## Detailed Setup Guide

### Google Account Integration

Daily Briefer needs access to your Gmail, Calendar, and Google Drive to gather information for your briefings.

#### Step 1: Get Google API Access

1. **Create a Google Cloud Project:**
   - Go to https://console.cloud.google.com
   - Create a new project or select an existing one
   - Enable billing (required for API access, but actual usage is typically free)

2. **Enable Required APIs:**
   - Gmail API (for email access)
   - Google Calendar API (for calendar events)
   - Google Drive API (for document access)
   - Generative Language API (for AI processing)

3. **Create OAuth 2.0 Credentials:**
   - Go to "Credentials" in the Cloud Console
   - Create "OAuth 2.0 Client ID" for "Desktop application"
   - Download the credentials file as `credentials.json`
   - Place it in your daily-briefer directory

#### Step 2: Get API Keys

1. **Gemini API Key:**
   - Visit https://makersuite.google.com/app/apikey
   - Create a new API key
   - Add it to your `.env` file as `GOOGLE_AI_API_KEY=your_key_here`

2. **Todoist API Key:**
   - Go to Todoist Settings > Integrations
   - Copy your API token
   - Add it to your `.env` file as `TODOIST_API_TOKEN=your_token_here`

#### Step 3: First Run Authorization

When you first run Daily Briefer, it will:
1. Open your web browser for Google OAuth consent
2. Ask you to grant permissions for Gmail and Calendar access
3. Save the authorization tokens automatically
4. Generate your first briefing

### Alternative: Use the Setup Helper

For a guided setup experience:

```bash
python setup_oauth_credentials.py
```

This script walks you through the entire process with step-by-step instructions.

## Using Daily Briefer

### Basic Usage

```bash
# Generate today's briefing
uv run python daily_briefer.py

# Generate a briefing for a specific date
uv run python daily_briefer.py 2024-01-15

# Show help and usage information
uv run python daily_briefer.py --help
```

### What Happens When You Run It

1. **Data Collection** (30-60 seconds): Gathers emails from the past 7 days, today's calendar events, and current Todoist tasks

2. **Email Processing** (60-90 seconds): AI agents classify and summarize your emails in the engaging "Today in Tabs" style

3. **Calendar Analysis** (30-45 seconds): Analyzes your schedule and gathers context from related emails and documents

4. **Task Integration** (15-30 seconds): Reviews your Todoist tasks and suggests new ones based on email content

5. **Document Assembly** (15-30 seconds): Combines everything into your final briefing document

**Total time**: Usually 2-4 minutes depending on email volume

### Tips for Best Results

- **Run it daily**: The system works best when used consistently
- **Keep your calendar updated**: More context in calendar events = better briefings
- **Use descriptive email subjects**: Helps the AI categorize more accurately
- **Connect your key tools**: Link Google Docs, Sheets, and other files to calendar events when possible

## Configuration Options

### Required Settings (.env file)

```bash
# Google AI API (for processing)
GOOGLE_AI_API_KEY=your_gemini_api_key

# Google Services (automatically configured during setup)
GOOGLE_APPLICATION_CREDENTIALS=credentials.json

# Todoist Integration
TODOIST_API_TOKEN=your_todoist_token

# Optional: Disable telemetry
CREWAI_TELEMETRY=false
```

### Customization Options

**Email Date Range**: By default, Daily Briefer analyzes emails from the past 7 days. This provides good context without being overwhelming.

**Output Format**: Briefings are generated in Markdown format, making them easy to read in your terminal, copy to other documents, or save as files.

**Privacy**: All processing happens locally or through your own API keys. Your data isn't shared with third parties.

### What Daily Briefer Connects To

- **Gmail**: Reads your emails to create summaries and identify action items
- **Google Calendar**: Analyzes your schedule and gathers meeting context
- **Google Drive/Docs**: Accesses documents linked in calendar events and emails
- **Todoist**: Retrieves your existing tasks and can suggest new ones
- **Google AI (Gemini)**: Powers the AI analysis and summary generation

## Troubleshooting Common Issues

### "Error generating briefing" Messages

**Check your API credentials first:**
1. Verify your `.env` file has all required keys
2. Test your Google API key at https://makersuite.google.com/app/apikey
3. Confirm your Todoist token works by logging into Todoist

**Authentication issues:**
- Delete `token.json` and run the program again to re-authenticate
- Make sure you granted all requested permissions during OAuth setup
- Check that Gmail and Calendar APIs are enabled in Google Cloud Console

### "No emails found" or "Calendar empty"

**This usually means:**
- You're generating a briefing for a weekend or day with no activity
- Your email filters are too restrictive
- The date range doesn't include recent emails

**Try:**
- Generate a briefing for a recent weekday instead
- Check that you have emails in your Gmail inbox from the past week

### "Slow performance" or "Takes too long"

**Common causes:**
- Large volume of emails to process
- Many calendar events with extensive details
- Network connectivity issues

**Solutions:**
- Be patient - complex briefings take 3-5 minutes
- Run during off-peak hours for better API response times
- Consider reducing the email analysis timeframe if needed

### First-Time Setup Issues

**"credentials.json not found":**
1. Run `python setup_oauth_credentials.py` for guided setup
2. Make sure you downloaded the OAuth credentials from Google Cloud Console
3. Verify the file is named exactly `credentials.json`

**"Permission denied" errors:**
1. Enable all required APIs in Google Cloud Console
2. Configure the OAuth consent screen
3. Make sure your Google account has access to the necessary data

### Getting Help

If problems persist:
1. Check that all your accounts (Google, Todoist) are accessible via web
2. Verify your internet connection is stable
3. Try running the setup scripts again
4. Review error messages for specific API or authentication issues

## Privacy and Security

Daily Briefer is designed with privacy in mind:

- **Local Processing**: Your emails and calendar data are processed locally on your machine
- **Your API Keys**: Uses your own Google and Todoist API keys - no data goes through third-party servers
- **No Data Storage**: Briefings are generated fresh each time; no personal data is permanently stored
- **Secure Credentials**: Keep your `credentials.json`, `token.json`, and `.env` files secure and never share them

## Understanding the Technology

Daily Briefer uses advanced AI technology to understand and summarize your information:

- **CrewAI Framework**: Coordinates multiple AI agents working together
- **Google Gemini AI**: Powers the natural language understanding and generation
- **Todoist MCP Protocol**: Connects to your task management system
- **Google Workspace APIs**: Accesses your Gmail, Calendar, and Drive data

## Customizing Your Experience

While Daily Briefer works great out of the box, you can customize it:

- **Email Categories**: The system learns from your email patterns over time
- **Summary Style**: The "Today in Tabs" style can be adjusted in the agent configurations
- **Date Ranges**: Modify how far back to look for emails and tasks
- **Output Format**: Briefings can be saved to files or integrated with other tools

## What Makes Daily Briefer Different

**Personal and Contextual**: Unlike generic email summaries, Daily Briefer understands your specific workflows, projects, and priorities.

**Actionable Intelligence**: Every briefing is designed to help you make decisions and take action, not just stay informed.

**Conversational Tone**: The "Today in Tabs" style makes routine updates engaging and actually enjoyable to read.

**Comprehensive View**: Combines emails, calendar, and tasks into a single coherent view of your day.

## Support and Community

Daily Briefer is actively developed and maintained. For support:

1. Check the troubleshooting guide above for common issues
2. Review your API credentials and permissions if something isn't working
3. Open an issue with specific error messages for technical problems
4. Share feedback about the briefing format and suggestions for improvement

---

*Built with [CrewAI](https://crewai.com), powered by Google Gemini AI, and designed to make your mornings more productive and less overwhelming.*