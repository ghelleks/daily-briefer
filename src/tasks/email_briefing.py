from crewai import Task
from datetime import date

from ..agents.email_briefing_agent import create_email_briefing_agent


def create_email_briefing_task(target_date: date) -> Task:
    """Create a task for producing 'Today in Tabs' style email summaries for the daily briefing."""
    
    return Task(
        description=f"""Transform categorized email data into engaging email summaries for daily briefing on {target_date.isoformat()}.
        
        Your task is to take the structured email classification data from the Email Analyst and create 
        compelling "Today in Tabs" style summaries for the **Email Summary** section of the daily briefing.
        
        **Input**: Structured email classification data with categorized emails (todo, review, fyi, forums)
        
        **Output Sections to Generate:**
        
        1. **📋 Todo** - Emails requiring action (>2 minutes)
           - Present each item as an engaging narrative
           - **Bold** key deadlines, amounts, and action items
           - Link to [original emails](gmail-url) and any mentioned documents/websites
           - Add context about why these items matter
        
        2. **🔍 Review** - Emails requesting feedback or professional response  
           - Transform requests into compelling summaries
           - **Bold** important names, projects, and deadlines
           - Link to [original emails](gmail-url) and documents needing review
           - Explain the significance of each review request
        
        3. **💡 FYI** - Informational updates and automated notifications
           - **This is your showcase section for "Today in Tabs" style**
           - Make dry notifications feel interesting and connected
           - **Bold** key terms, amounts, companies, and status updates
           - Rich linking to [original emails](gmail-url) and related resources
           - Add commentary and context that makes mundane updates engaging
           - Connect related notifications into coherent themes
        
        4. **💬 Forums** - Group discussions and community updates
           - Summarize interesting discussions and community activity
           - **Bold** key topics, contributors, and discussion themes
           - Link to [original emails](gmail-url) and relevant forum threads
           - Highlight noteworthy conversations and developments
        
        **Critical Requirements:**
        
        🔗 **Mandatory Linking:**
        - **EVERY email mention MUST include a hyperlink to the original Gmail message**
        - **EVERY website, document, or resource mentioned MUST be hyperlinked**
        - Use Gmail URLs in format: https://mail.google.com/mail/u/0/#inbox/[message-id]
        - Use descriptive link text that enhances readability
        
        ✨ **"Today in Tabs" Style Guidelines:**
        - Conversational, engaging tone with personality
        - Strategic use of **bold** for visual hierarchy and emphasis
        - Add context and commentary that makes items interesting
        - Create narrative connections between related emails
        - Transform mundane updates into engaging mini-stories
        
        📝 **Content Standards:**
        - Each section should feel cohesive and well-curated
        - Maintain professional tone while being engaging
        - Focus on why things matter, not just what happened
        - Never create synthetic data - only work with provided email data
        - If a category has no emails, note it briefly and move on
        
        **Expected Output**: A complete "Email Summary" section formatted in markdown with:
        - Four distinct subsections (Todo, Review, FYI, Forums)
        - Rich hyperlinks throughout all sections
        - Strategic **bold** formatting for key information
        - Engaging "Today in Tabs" style writing that makes email updates compelling to read""",
        
        agent=create_email_briefing_agent(),
        expected_output="Complete Email Summary section with engaging 'Today in Tabs' style summaries, comprehensive hyperlinks, and strategic formatting"
    )