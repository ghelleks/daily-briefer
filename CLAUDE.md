# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Daily Briefer is a Python-based automation system for creating daily briefing documents. The project consists of several agent-based tools that process emails, calendar events, and tasks to generate comprehensive daily summaries.

## Core Architecture

The system is organized around three main agent types:

1. **Daily Briefing Agent** - Main orchestrator that generates structured daily briefing documents
2. **Todoist Agent** - Handles task management and integration
3. **Inbox Processing Agent** - Classifies and processes emails using a label system

### Email Classification System

The project uses a specific 5-label system for email processing:
- `fyi` - Automated alerts, reminders, status updates
- `review` - Emails requiring feedback, review, or direct response 
- `2min` - Quick actions that can be resolved in under 2 minutes
- `meetings` - Calendar invites and meeting-related communications
- `todoist` - Emails converted to tasks

## Key Components

- `daily_briefer.py` - Entry point (currently minimal)
- `docs/daily-briefer.md` - Complete specification for the Daily Briefing Agent persona and workflow
- `docs/label-emails.md` - Email classification rules and instructions
- `TODO.md` - Development roadmap and task breakdown

## Development Commands

```bash
# Install dependencies
pip install -e .

# Install Todoist MCP server (required for task management)
npm install -g @modelcontextprotocol/server-todoist

# Run the main application
python daily_briefer.py

# The project uses Python 3.13+ (as specified in pyproject.toml)
```

## Environment Setup

1. Copy `.env.example` to `.env` and configure:
   - `TODOIST_API_KEY`: Your Todoist API key (required)
   - `GOOGLE_API_KEY`: Your Google AI API key for Gemini models
   - `GOOGLE_APPLICATION_CREDENTIALS`: Path to Google service account credentials

2. Set up authentication tokens in the `tokens/` directory:
   - Place your Google service account credentials at `tokens/credentials.json`
   - OAuth tokens will be automatically generated per service:
     - `tokens/gmail_api_token.json` (Gmail access)
     - `tokens/token_calendar.json` (Calendar access)
     - `tokens/token_workspace.json` (Google Workspace access)

3. The Todoist MCP server uses `npx -y todoist-mcp` (no separate installation needed)

## Daily Briefing Document Structure

The generated briefing follows a strict three-section format:

1. **Action Items**
   - From Todoist (due items for the day)
   - Suggested (derived from emails and calendar events)

2. **Email Summary** 
   - FYI (informational items)
   - Review (items requiring action)
   - Quick (2-minute tasks)

3. **Daily Agenda**
   - Chronological calendar events with context and related documents

## Integration Points

The system is designed to integrate with:
- Google Calendar (for event data)
- Gmail (for email analysis)
- Todoist (for task management)
- Google Workspace (for document access)
- Day One Journal (for archiving completed items)
- Instapaper (for reading list management)
- we use uv to manage this project and its dependencies
- always use uv to run this tool
- Always follow CrewAI best practices. When you identify patterns or behavior that deviate from those best practices, you seek guidance from the user.