"""
Email Classification Constants

This module defines the canonical email classification labels used throughout
the Daily Briefer system. All agents, tasks, and tools should import from
this module to ensure consistency.
"""

from typing import List, Dict

# Action classification labels - what to DO with the email
ACTION_LABELS: List[str] = [
    'todo',      # Emails requiring action that cannot be completed in less than 2 minutes
    '2min',      # Emails requiring action that can be resolved in less than 2 minutes
    'fyi',       # Informational emails requiring no action
    'review',    # Emails asking for feedback, review, or opinion on documents
    'meetings'   # Meeting-related communications including invitations and notes
]

# Gmail system labels - what the email IS (handled by Gmail automatically)
GMAIL_SYSTEM_LABELS: List[str] = [
    'CATEGORY_PROMOTIONS',  # Marketing emails, deals, offers
    'CATEGORY_FORUMS',      # Mailing lists, discussion groups
    'CATEGORY_UPDATES',     # Notifications, confirmations, receipts
    'CATEGORY_SOCIAL',      # Social media notifications
    'CATEGORY_PRIMARY',     # Important emails that don't fit other categories
    'INBOX',                # Inbox folder
    'IMPORTANT',            # Important marker
    'STARRED',              # Starred emails
    'SENT',                 # Sent folder
    'DRAFT',                # Draft folder
    'SPAM',                 # Spam folder
    'TRASH',                # Trash folder
    'UNREAD'                # Unread marker
]

# Action label metadata for display and documentation
ACTION_LABEL_METADATA: Dict[str, Dict[str, str]] = {
    'todo': {
        'display_name': 'Todo',
        'description': 'Emails requiring action that cannot be completed in less than 2 minutes',
        'emoji': '📋',
        'priority': '1'
    },
    '2min': {
        'display_name': '2min',
        'description': 'Emails requiring action that can be resolved in less than 2 minutes',
        'emoji': '⚡',
        'priority': '2'
    },
    'review': {
        'display_name': 'Review',
        'description': 'Emails asking for feedback, review, or opinion on documents',
        'emoji': '🔍',
        'priority': '3'
    },
    'meetings': {
        'display_name': 'Meetings',
        'description': 'Meeting-related communications including invitations and notes',
        'emoji': '📅',
        'priority': '4'
    },
    'fyi': {
        'display_name': 'FYI',
        'description': 'Informational emails requiring no action',
        'emoji': '💡',
        'priority': '5'
    }
}

# Helper functions for working with labels
def get_action_labels() -> List[str]:
    """Get the list of action classification labels."""
    return ACTION_LABELS.copy()

def get_gmail_system_labels() -> List[str]:
    """Get the list of Gmail system labels."""
    return GMAIL_SYSTEM_LABELS.copy()

def get_action_priority_order() -> List[str]:
    """Get action labels in priority order (for daily briefing organization)."""
    return sorted(ACTION_LABELS, key=lambda label: ACTION_LABEL_METADATA[label]['priority'])

def get_label_display_name(label: str) -> str:
    """Get the display name for an action label."""
    return ACTION_LABEL_METADATA.get(label, {}).get('display_name', label)

def get_label_emoji(label: str) -> str:
    """Get the emoji for an action label."""
    return ACTION_LABEL_METADATA.get(label, {}).get('emoji', '')

def get_label_description(label: str) -> str:
    """Get the description for an action label."""
    return ACTION_LABEL_METADATA.get(label, {}).get('description', '')