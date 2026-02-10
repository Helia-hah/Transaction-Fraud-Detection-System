from datetime import datetime
import pandas as pd

def generate_prompt(df):
    """
    df: DataFrame containing transactions for ONE user only
    """
    
    # Limit the DataFrame to the most recent 100 rows
    df = df.tail(25)


    # Extract user info from the first row
    first_name = df["first"].iloc[0]
    last_name = df["last"].iloc[0]
    dob = df["dob"].iloc[0]
    street = df["street"].iloc[0]

    
    # Columns to include for LLM
    selected_columns = ["trans_date_trans_time", "cc_num", "merchant", "category", "amt", 
                        "trans_num", "unix_time", "merch_lat", "merch_long"]
    
    # Convert transactions to CSV-style text
    transactions_text = df[selected_columns].to_csv(index=False)
    
    # System message
    system_message = f"""
You are an AI Fraud Analyst Assistant. Your role is to analyze transaction data for a single user and detect suspicious or potentially fraudulent activity.

User context:
- First name: {first_name}
- Last name: {last_name}
- Date of birth: {dob}
- Address: {street}

You will receive this user's transactions with the following columns:
- trans_date_trans_time, cc_num, merchant, category, amt, trans_num, unix_time, merch_lat, merch_long

Instructions for categories:
- Some category codes may not be standard or known. 
- Try to interpret the category into a readable description. For example, 'grocery_pos' → 'Grocery store purchase', 'misc_net' → 'Miscellaneous online purchase'.
- If unsure about the exact meaning, describe it as a type of purchase or merchant in plain language.

Your task:
- Flag any transaction that is unusual or potentially suspicious, including borderline cases, even if the pattern is not very strong.
- Explain why each flagged transaction is suspicious using **specific reasoning**:
    - Consider whether the transaction amount is unusually high or low for the type of purchase or merchant (interpret category codes into plain language, e.g., 'grocery_pos' → 'Grocery store purchase', 'misc_net' → 'Miscellaneous online purchase').
    - Consider the timing of the transaction (e.g., late night, early morning, or unusual hours).
    - Consider patterns, such as multiple high-value transactions in a short time period.
    - Consider merchant names as context, but do not flag solely because of the word 'fraud'.
- Include the specific amount, interpreted category description, and transaction time in your explanation when relevant.
- If a category code is unclear, make a reasoned, plain-language guess about the type of purchase.
- Stay professional, clear, and structured.
- Only use the information provided; do not invent external data.

Output JSON in the following format, array of objects:

[{{ 
  "trans_num": "string",
  "trans_date_trans_time": "YYYY-MM-DD HH:MM:SS",
  "reason": "string",
  "confidence": "low | medium | high"
}}]
"""


    
    # User message
    user_message = f"""
Here is the transaction history for {first_name} {last_name}:

{transactions_text}

Please review the transactions and return ONLY the JSON array in the format specified above.
"""
    
    return system_message, user_message
