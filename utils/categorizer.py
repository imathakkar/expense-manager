def categorize_transaction(description: str, memory: dict) -> str:
    desc = description.lower()
    for key in memory:
        if key in desc:
            return memory[key]
    if any(word in desc for word in ['grocery', 'walmart', 'food']):
        return 'Groceries'
    elif any(word in desc for word in ['uber', 'lyft', 'taxi', 'bus', 'presto']):
        return 'Public Transporation'
    elif any(word in desc for word in ['restaurant', 'cafe', 'tim hortons', 'starbucks']):
        return 'Dining Out'
    elif any(word in desc for word in ['rent', 'mortgage', 'landlord']):
        return 'Rent'
    elif any(word in desc for word in ['netflix', 'spotify', 'subscription']):
        return 'Subscriptions (Google,  Prime, Apple)'
    elif any(word in desc for word in ['phone', 'internet', 'wifi']):
        return 'Phone'
    elif any(word in desc for word in ['electronic funds transfer', 'preauthorized debit']):
        return 'Other Fees'
    else:
        return 'Other'