import re

def name_validator(name):
    if not name.strip():
        return "Campaign name is required."
    if len(name.strip()) < 3:
        return "Campaign name must be at least 3 characters."

def message_validator(message):
    if not message.strip():
        return "Message is required."
    if len(message.strip()) < 15:
        return "Campaign message must be at least 15 characters."
    
def sender_number_validator(sender_number):
    if not sender_number.strip():
        return "Sender number is required."