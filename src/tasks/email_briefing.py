from crewai import Task
from datetime import date

from ..agents.email_briefing_agent import create_email_briefing_agent
from ..constants import get_action_priority_order, get_label_emoji, get_label_display_name


def create_email_briefing_task(target_date: date, verbose: bool = True) -> Task:
    """Create a task for producing 'Today in Tabs' style email summaries for the daily briefing."""
    
    # Generate dynamic section headers using centralized constants
    priority_order = get_action_priority_order()
    sections = []
    for label in priority_order:
        emoji = get_label_emoji(label)
        display_name = get_label_display_name(label)
        sections.append(f"{emoji} **{display_name}**")
    
    sections_text = "\n        ".join([f"{i+1}. {section}" for i, section in enumerate(sections)])
    
    return Task(
        description=f"""Transform categorized email data into engaging email summaries for daily briefing on {target_date.isoformat()}.
        
        Your task is to take the structured email classification data from the Email Analyst and create 
        compelling "Today in Tabs" style summaries for the **Email Summary** section of the daily briefing.
        
        **CRITICAL: Use Dual Classification System**
        
        **Input**: Structured email classification data organized by ACTION categories (todo, 2min, review, meetings, fyi)
        with Gmail system label context (CATEGORY_PROMOTIONS, CATEGORY_FORUMS, etc.)
        
        **Output Sections to Generate (ACTION Priority Order):**
        
        {sections_text}
        
        **Section Guidelines:**
        - Present each item as an engaging narrative
        - **Bold** key deadlines, amounts, and action items  
        - Link to [original emails](gmail-url) and any mentioned documents/websites
        - Add context about why these items matter
        - Use email type context to add flavor when relevant
        - For FYI section: Make dry notifications feel interesting and connected
        
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
        - Five distinct subsections organized by ACTION priority (Todo, 2min, Review, Meetings, FYI)
        - Rich hyperlinks throughout all sections
        - Strategic **bold** formatting for key information
        - Engaging "Today in Tabs" style writing that makes email updates compelling to read
        - Email type context woven in naturally when it adds flavor or clarity""",
        
        agent=create_email_briefing_agent(verbose=verbose),
        expected_output="Complete Email Summary section with engaging 'Today in Tabs' style summaries, comprehensive hyperlinks, and strategic formatting"
    )