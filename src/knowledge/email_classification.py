from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from ..constants import (
    ACTION_LABELS, 
    GMAIL_SYSTEM_LABELS,
    get_action_priority_order, 
    get_label_description,
    get_label_display_name,
    get_label_emoji
)


def create_email_classification_knowledge() -> StringKnowledgeSource:
    """
    Create a knowledge source containing email classification rules.
    
    This knowledge source contains the definitive email classification system
    used by all email-related agents for consistent categorization.
    
    Returns:
        StringKnowledgeSource: The email classification knowledge source
    """
    
    # Generate completely dynamic content from centralized constants
    
    # Action labels with full details
    action_sections = []
    for label in ACTION_LABELS:
        emoji = get_label_emoji(label)
        display_name = get_label_display_name(label)
        description = get_label_description(label)
        action_sections.append(f"### **{emoji} {label}**\n{description}")
    
    action_labels_detailed = "\n\n".join(action_sections)
    
    # Priority order for classification
    priority_order = get_action_priority_order()
    priority_list = "\n".join([f"{i+1}. **{label}** ({get_label_description(label)})" 
                              for i, label in enumerate(priority_order)])
    
    # Gmail system labels list
    gmail_labels_list = "\n".join([f"- **{label}**" for label in GMAIL_SYSTEM_LABELS[:5]])  # Show first 5
    
    classification_content = f"""
# Dual Email Classification System

This system uses TWO ORTHOGONAL classification approaches for Gmail emails:

1. **Email Type Classification** (Gmail System Labels) - What the email IS
2. **Action Classification** (Our Custom Labels) - What to DO with it

These work together: an email can have both a type (e.g., CATEGORY_UPDATES) AND an action (e.g., todo).

---

## Email Type Classification (Gmail System Labels)

Gmail automatically applies these system labels. **DO NOT create duplicate user labels** for these categories.

### **CATEGORY_PROMOTIONS**
Marketing emails, deals, offers, sales announcements.
- **Respect this label** - don't create "promotions" user label
- **Action needed**: Usually "fyi" but can be "todo" if requiring response

### **CATEGORY_UPDATES** 
Notifications, confirmations, receipts, automated status updates.
- **Examples**: Payment confirmations, shipping notifications, deployment alerts
- **Action needed**: Usually "fyi" but can be "todo" if action required

### **CATEGORY_FORUMS**
Mailing lists, discussion groups, community communications.
- **Respect this label** - don't create "forums" user label  
- **Action needed**: Usually "fyi" or "2min" for quick responses

### **CATEGORY_SOCIAL**
Social media notifications and social network updates.
- **Action needed**: Usually "fyi"

### **CATEGORY_PRIMARY**
Important emails that don't fit other categories.
- **Action needed**: Requires content analysis for todo/review/meetings/fyi

---

## Action Classification (Our Custom Labels)

These labels indicate what ACTION should be taken with the email, regardless of its type.

{action_labels_detailed}

**Examples by Email Type:**
- CATEGORY_UPDATES + todo: Payment failure requiring action
- CATEGORY_PRIMARY + todo: School communication requiring response
- CATEGORY_FORUMS + 2min: Mailing list requiring quick confirmation
- CATEGORY_PRIMARY + review: Google Docs sharing request
- CATEGORY_PRIMARY + meetings: Calendar invites
- CATEGORY_PROMOTIONS + fyi: Marketing emails (default)

---

## Dual Classification Rules

### **Step 1: Identify Email Type (Gmail System Labels)**
- **Respect existing Gmail system labels** - never create duplicate user labels
- Gmail labels tell us WHAT the email is (promotion, update, forum, etc.)
- If no Gmail system label exists, focus only on action classification

### **Step 2: Determine Required Action**
Apply these rules to determine what ACTION is needed:

1. **Payment requests, forms, school communications** → **todo**
2. **Quick confirmations, simple replies** → **2min**
3. **Document review requests, feedback requests** → **review**
4. **Calendar invites, meeting logistics** → **meetings**
5. **Informational content, no action needed** → **fyi**

### **Action Classification Priority**
When an email could fit multiple action categories, use this priority order:

{priority_list}

---

## Gmail System Integration

### **How to Work with Gmail System Labels**

#### **CATEGORY_PROMOTIONS**
- **Don't create**: "promotions" user label
- **Do apply**: Action labels (usually "fyi", sometimes "todo")
- **Example**: Marketing email → Keep CATEGORY_PROMOTIONS + add "fyi"

#### **CATEGORY_FORUMS** 
- **Don't create**: "forums" user label
- **Do apply**: Action labels (usually "fyi" or "2min", sometimes "todo")
- **Example**: Mailing list → Keep CATEGORY_FORUMS + add "2min" if response needed

#### **CATEGORY_UPDATES**
- **Don't create**: "updates" user label  
- **Do apply**: Action labels (usually "fyi", sometimes "todo")
- **Example**: Payment failure → Keep CATEGORY_UPDATES + add "todo"

#### **CATEGORY_PRIMARY**
- **No type label needed** (already primary)
- **Do apply**: Action labels based on content analysis
- **Example**: Personal email → add "review" if asking for feedback

### **Label Application Strategy**
- **Gmail system labels**: Respect and preserve (don't modify)
- **Our action labels**: Apply exactly one per email
- **Result**: Each email has type context + action directive

---

## Classification Guidelines

### **Two-Phase Classification Process**

**Phase 1: Observe Email Type**
- Check for existing Gmail system labels (CATEGORY_*)
- Note email type context but don't create duplicate labels
- Use type information to inform action classification

**Phase 2: Classify Required Action**
- Analyze email content for required actions
- Apply exactly one action label: todo, 2min, review, meetings, fyi
- Consider urgency and complexity when choosing between todo/2min

### **Content Analysis Guidelines**
- **Read subject, sender, and content** for action indicators
- **Action words**: "please", "required", "due", "review" → likely todo/review
- **Time sensitivity**: "urgent", "asap", "deadline" → likely todo
- **Question format**: Direct questions → review or 2min
- **Calendar keywords**: "meeting", "schedule", "invite" → meetings
- **No action indicators**: Notifications, updates → fyi

### **Quality Guidelines**
- **Be consistent**: Similar emails should get similar action classifications
- **Err toward action**: When unsure between fyi and todo, choose todo
- **Respect Gmail**: Never duplicate system functionality with user labels
- **Single action**: Each email gets exactly one action label
"""
    
    return StringKnowledgeSource(
        content=classification_content,
        chunk_size=1000,
        chunk_overlap=100
    )