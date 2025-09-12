from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource


def create_email_classification_knowledge() -> StringKnowledgeSource:
    """
    Create a knowledge source containing email classification rules.
    
    This knowledge source contains the definitive email classification system
    used by all email-related agents for consistent categorization.
    
    Returns:
        StringKnowledgeSource: The email classification knowledge source
    """
    
    classification_content = """
# Email Classification System

This is the definitive email classification system for categorizing Gmail emails. Use these rules consistently across all email processing tasks.

## Classification Categories

### **todo** 
Emails that require action and cannot be completed in less than 2 minutes.

**Examples:**
- Emails about Lee Elementary school
- Security alerts requiring immediate attention
- Requests for payment or financial transactions
- Requests to complete forms or applications
- Messages from physicians requiring follow-up
- School-related communications requiring action

### **2min** 
Emails that require action but can be resolved in less than 2 minutes.

**Examples:**
- Simple confirmations or quick replies
- Brief status updates requiring acknowledgment
- Quick scheduling confirmations
- Simple form completions

### **fyi** 
Informational emails and automated updates about completed or ongoing events.

**Examples:**
- Email reminders and notifications
- Successful payment confirmations
- Transfer sent notifications
- Deployment status updates
- Shipment and postal delivery updates
- Order receipts and confirmations
- Automated "how was your experience" emails
- System status updates

### **review** 
Emails specifically asking for feedback, review, or opinion on documents in professional/collaborative contexts.

**Examples:**
- Emails from Google Documents mentioning you specifically
- Direct requests for document review or feedback
- Professional collaboration requests
- Personal questions from individuals requiring direct response
- Personal conversations requiring thoughtful replies
- NOT automated feedback requests or surveys

### **news**
Emails from journalists or news organizations.

**Examples:**
- Newsletter subscriptions from news outlets
- Press releases
- Journalist inquiries
- News alerts and updates

### **promotions**
Emails flagged as "Promotions" in Gmail.

**Examples:**
- Marketing emails
- Sales announcements
- Promotional offers
- Advertisement emails

### **forums**
Emails from group lists and community discussions.

**Examples:**
- Mailing list messages
- Community forum notifications
- Group discussion threads
- Professional association communications

### **meetings**
Meeting-related communications including invitations and meeting notes.

**Examples:**
- Calendar invites
- Meeting change notifications
- Meeting notes and summaries
- Conference call links and details
- Meeting preparation materials

## Key Classification Rules

Apply these rules when categorizing emails:

1. **Payment requests or action items** → **todo**
2. **Payment failure alerts** → **todo** 
3. **Shipment and delivery updates** → **fyi**
4. **Order receipts** → **fyi**
5. **Automated experience surveys** → **fyi**
6. **Direct document review requests** → **review**
7. **Personal questions requiring response** → **review**
8. **Calendar-related communications** → **meetings**
9. **Group mailing lists** → **forums**
10. **News organization emails** → **news**
11. **Gmail promotion-flagged emails** → **promotions**

## Classification Priority

When an email could fit multiple categories, use this priority order:

1. **meetings** (calendar-related takes precedence)
2. **todo** (action items take precedence over information)
3. **2min** (subset of todo for quick actions)
4. **review** (personal requests for feedback)
5. **news** (from news organizations)
6. **promotions** (marketing content)
7. **forums** (group communications)
8. **fyi** (informational, default for automated content)

## Gmail System Categories Integration

Gmail automatically applies system labels that should be leveraged in classification:

### **Gmail System Labels**
- `CATEGORY_PROMOTIONS` - Marketing emails, deals, offers → maps to **promotions**
- `CATEGORY_FORUMS` - Mailing lists, discussion groups → maps to **forums**  
- `CATEGORY_UPDATES` - Notifications, confirmations, receipts → maps to **fyi**
- `CATEGORY_SOCIAL` - Social media notifications → maps to **fyi**
- `CATEGORY_PRIMARY` - Important emails → requires content-based classification
- `INBOX` - General inbox marker
- `IMPORTANT` - Gmail importance marker
- `STARRED` - User-starred emails

### **Gmail Category Priority Rules**
1. **Use Gmail categories as primary signals** when they align with our system
2. **CATEGORY_PROMOTIONS** → automatically classify as **promotions**
3. **CATEGORY_FORUMS** → automatically classify as **forums**
4. **CATEGORY_UPDATES** → default to **fyi** unless content indicates otherwise
5. **CATEGORY_PRIMARY** → analyze content for todo/review/meetings/2min classification
6. **No Gmail category** → use full content-based classification

### **Label Strategy**
- **Don't duplicate** Gmail's promotional/forum categorization
- **Focus custom labels** on actionability (todo, 2min, review, meetings)
- **Complement Gmail** rather than replace system functionality
- **Respect existing** Gmail categorization when it's accurate

## Classification Guidelines

- **First check Gmail system labels** for automatic categorization hints
- Read the email subject, sender, and content carefully
- Consider the sender context (automated vs. personal)
- Look for action words and urgency indicators
- Classify based on primary purpose, not secondary content
- When Gmail categories exist, use them as strong classification signals
- When unsure, err toward the category requiring more attention (todo > review > fyi)
- Maintain consistency across similar email types
"""
    
    return StringKnowledgeSource(
        content=classification_content,
        chunk_size=1000,
        chunk_overlap=100
    )