import ast
import re
import os
import pandas as pd
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


# Bank mapping utilities
BANK_TOKENS = {
    "AXIS": "AXIS", 
    "HDFC": "HDFC", 
    "KOTAK": "KOTAK",
    "ICICI": "ICICI", 
    "INDUSIND": "INDUSIND_BANK", 
    "RBL": "RBL",
    "SCB": "STANDARD_CHARTERED_BANK", 
    "YES": "YES",
    "PNB": "PNB", 
    "IOB": "INDIAN_OVERSEAS_BANK"
}


def safe_divide(numer, denom):
    """Safe division function to avoid division by zero errors."""
    return numer / denom if denom else 0


def map_acquirer(acq):
    """Map acquirer names to standardized bank tokens."""
    s = re.sub(r"[^A-Z]", "", str(acq).upper())
    for k, v in BANK_TOKENS.items():
        if k in s:
            return v
    return "OTHER"


def load_data(file_path="data/data_cleaned.csv"):
    """Load and prepare the cleaned data."""
    try:
        df = pd.read_csv(file_path)
        # Convert Date column to datetime if it exists
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        return df
    except FileNotFoundError:
        print(f"Error: Could not find file {file_path}")
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def get_system_message():
    """Return the system message for the LLM."""
    return """You are an expert Python data-analyst and payments-domain SME.
Your job is to read natural-language questions about Pine Labs payment data and respond **only** with a short, runnable Python snippet (pandas-style) that produces the requested result from a DataFrame named `df` (already loaded from **data_cleaned.csv**).

─────────────────────────────
DATA OVERVIEW
─────────────────────────────
The DataFrame `df` has these key columns:

- Payment Mode Name                 (e.g. "CREDIT/DEBIT CARD", "UPI")
- Transaction Status Name          ("CAPTURED", "REFUNDED", …)
- Acquirer Response Code           (e.g. "AUTHORIZED", "0")
- Time To Complete                 (seconds from init to capture)
- Pine Payment Gateway Integration Mode Name ("SEAMLESS", "REDIRECT")
- Refund Amount                    ₹ refunded
- Settlement Amount                ₹ settled
- Bank Commision                   ₹ MDR / acquiring fee
- Convenience Fees Amount In (Paise)
- Acquirer Issuer Match            {1, 0}
- Payout Status                    ("PAID", "PENDING")
- Bank Service Tax                 GST on MDR
- Amount To Be Deducted …         extra bank charges
- Date                             ISO "yyyy-mm-dd"

Derived KPIs you often compute:

* Total GMV              = df['Settlement Amount'].sum()
* Refund Rate            = safe_divide(df['Refund Amount'].sum(), df['Settlement Amount'].sum())
* Success Rate           = share of rows where Transaction Status Name == "CAPTURED"
* Avg Time To Capture    = df['Time To Complete'].mean()
* Net Bank Cost          = Bank Commision + Bank Service Tax + Amount To Be Deducted …

Always define:

```python
def safe_divide(numer, denom):
    return numer / denom if denom else 0


─────────────────────────────
TIME-PERIOD CONVENTIONS
─────────────────────────────
df["Date"] is parsed with pd.to_datetime.
A dict called time_periods is pre-computed per request, e.g.:


time_periods = {
    "lw":  {"start": "2025-05-05", "end": "2025-05-11",
            "compare_start": "2024-05-06", "compare_end": "2024-05-12"},
    "mtd": {…},
    "qtd": {…},
    "ytd": {…},
    "trailing_13_weeks": {…}
}
Guidelines:

For "lw", "mtd", "qtd", "ytd", or "trailing 13 weeks", filter df["Date"] between start and end.

For explicit weeks like "202518 week" or "5th week of this year", convert to ISO week and filter directly.

When YoY comparison is required, build compare_df using compare_start and compare_end, and return percentage change columns (positive = increase, negative = decrease).

─────────────────────────────
CODE-STYLE RULES
─────────────────────────────

Return only Python code – no extra commentary.

Use pandas idioms (groupby, agg, vectorised ops).

Always qualify columns: df['Settlement Amount'], not bare names.

Use safe_divide for any division.

Handle nulls with .fillna(0) or .dropna() as appropriate.

If unsure, output exactly: 'Unable to generate python snippet.'

─────────────────────────────
BANK-MAPPING UTILITIES
─────────────────────────────
import re

BANK_TOKENS = {
    "AXIS": "AXIS", "HDFC": "HDFC", "KOTAK": "KOTAK",
    "ICICI": "ICICI", "INDUSIND": "INDUSIND_BANK", "RBL": "RBL",
    "SCB": "STANDARD_CHARTERED_BANK", "YES": "YES",
    "PNB": "PNB", "IOB": "INDIAN_OVERSEAS_BANK"
}

def map_acquirer(acq):
    s = re.sub(r"[^A-Z]", "", str(acq).upper())
    for k, v in BANK_TOKENS.items():
        if k in s:
            return v
    return "OTHER"
─────────────────────────────
EXAMPLE – Q ⇒ PYTHON
─────────────────────────────
Question: "Show last-week refund rate by payment mode."

python
Copy
Edit
mask = df["Date"].between(time_periods["lw"]["start"],
                          time_periods["lw"]["end"])
tmp = df.loc[mask]

result = (tmp.groupby("Payment Mode Name")
              .apply(lambda g: safe_divide(g["Refund Amount"].sum(),
                                           g["Settlement Amount"].sum()))
              .reset_index(name="refund_rate"))
result
"""


def get_llm_response(user_input, api_key):
    """Get response from LLM for the given user input."""
    system_message = get_system_message()
    
    messages = [
        ("system", system_message),
        ("human", user_input),
    ]

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=api_key
    )

    ai_msg = llm.invoke(messages)
    return ai_msg.content


def get_english_response(user_question, computed_result, api_key):
    """Generate a natural English sentence response from the user question and computed result."""
    system_message = """You are an expert data analyst who explains analytical results in clear, natural English.

Your job is to take a user's question about payment data and the computed result, then provide a concise, professional English response that directly answers their question.

Guidelines:
- Be conversational but professional
- Include specific numbers/percentages when relevant
- Keep responses concise (1-2 sentences typically)
- If the result is a DataFrame, summarize the key insights
- If the result is a single number, provide context about what it means
- If there's an error in the result, acknowledge it politely

Examples:
Question: "What was the total GMV last week?"
Result: 1250000.50
Response: "The total Gross Merchandise Value (GMV) for last week was ₹12.5 lakhs."

Question: "Show refund rates by payment mode"
Result: DataFrame with payment modes and their refund rates
Response: "Here are the refund rates by payment mode: Credit/Debit Cards had a 2.3% refund rate, while UPI transactions had a 1.8% refund rate."
"""
    
    prompt = f"""
User Question: {user_question}
Computed Result: {computed_result}

Please provide a natural English response that answers the user's question based on the computed result.
"""
    
    messages = [
        ("system", system_message),
        ("human", prompt),
    ]

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.3,  # Slightly higher temperature for more natural language
        max_tokens=200,   # Limit response length
        timeout=None,
        max_retries=2,
        api_key=api_key
    )

    ai_msg = llm.invoke(messages)
    return ai_msg.content


def execute_llm_code(code: str, df: pd.DataFrame):
    """Execute LLM-generated code with the provided DataFrame."""
    try:
        # Clean the code - remove markdown code blocks if present
        cleaned_code = code.strip()
        if cleaned_code.startswith('```python'):
            # Remove ```python at the start and ``` at the end
            lines = cleaned_code.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]  # Remove first line
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]  # Remove last line
            cleaned_code = '\n'.join(lines)
        elif cleaned_code.startswith('```'):
            # Remove generic ``` blocks
            lines = cleaned_code.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            cleaned_code = '\n'.join(lines)
        
        # Set up local variables with the DataFrame and utility functions
        local_vars = {
            'df': df, 
            'pd': pd, 
            'safe_divide': safe_divide,
            'map_acquirer': map_acquirer,
            'BANK_TOKENS': BANK_TOKENS,
            're': re
        }
        
        # Parse code into AST
        tree = ast.parse(cleaned_code)

        # Separate all but the last statement (for exec) and the last (for eval)
        *initial_stmts, last_stmt = tree.body

        # Compile and exec initial statements
        if initial_stmts:
            exec(compile(ast.Module(body=initial_stmts, type_ignores=[]), 
                        filename="<ast>", mode="exec"), {}, local_vars)

        # Handle final statement: expression or assignment
        if isinstance(last_stmt, ast.Expr):
            result = eval(compile(ast.Expression(body=last_stmt.value), 
                                filename="<ast>", mode="eval"), {}, local_vars)
        else:
            exec(compile(ast.Module(body=[last_stmt], type_ignores=[]), 
                        filename="<ast>", mode="exec"), {}, local_vars)
            result = None  # No result to return if it's an assignment

        return result
    except Exception as e:
        return f"Execution error: {e}"


def test_with_real_data():
    """Test the execute_llm_code function with real data."""
    # Load the actual data
    df = load_data()
    
    if df is None:
        print("Failed to load data. Exiting test.")
        return
    
    print("Data loaded successfully!")
    print(f"DataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst few rows:")
    print(df.head())
    print("\n" + "="*50 + "\n")
    
    # Test with a sample query
    if 'Date' in df.columns and 'Refund Amount' in df.columns:
        # Check available dates
        print("Available date range:")
        print(f"From: {df['Date'].min()} To: {df['Date'].max()}")
        
        # Test LLM code execution
        llm_code = '''
# Get average refund amount for a specific date (using first available date)
first_date = df["Date"].min()
mask = df["Date"] == first_date
avg_refund_amount = df.loc[mask, "Refund Amount"].mean()
avg_refund_amount
'''
        
        print(f"\nExecuting test code:")
        print(llm_code)
        print("\nResult:")
        result = execute_llm_code(llm_code, df)
        print(result)
    else:
        print("Required columns (Date, Refund Amount) not found in the dataset.")


def process_query(user_input: str, api_key: str = None):
    """
    Process a user query and return structured response with code, result, and English explanation.
    
    Args:
        user_input (str): The user's natural language question
        api_key (str, optional): OpenAI API key. If not provided, will use OPENAI_API_KEY environment variable
        
    Returns:
        dict: Contains 'success', 'llm_code', 'result', 'english_response', and 'error' fields
    """
    try:
        # Get API key from parameter or environment variable
        if api_key is None:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key is None:
                return {
                    "success": False,
                    "error": "API key not provided. Please set OPENAI_API_KEY environment variable or pass api_key parameter",
                    "llm_code": None,
                    "result": None,
                    "english_response": None
                }
        
        # Load data
        df = load_data()
        if df is None:
            return {
                "success": False,
                "error": "Failed to load data",
                "llm_code": None,
                "result": None,
                "english_response": None
            }
        
        # Get LLM response
        llm_response = get_llm_response(user_input, api_key)
        
        # Execute the code
        result = execute_llm_code(llm_response, df)
        
        # Generate English response
        english_response = get_english_response(user_input, result, api_key)
        
        return {
            "success": True,
            "llm_code": llm_response,
            "result": str(result),  # Convert to string for JSON serialization
            "english_response": english_response,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "llm_code": None,
            "result": None,
            "english_response": None
        }


if __name__ == "__main__":
    """Main function to demonstrate the functionality."""
    # Example usage
    user_input = "What was the average time-to-capture for UPI transactions on May 5th?"
    
    # Process the query (API key will be read from environment variable)
    response = process_query(user_input)
    
    if response["success"]:
        print(f"LLM Generated Code:\n{response['llm_code']}")
        print(f"\nResult: {response['result']}")
        print(f"\nEnglish Response: {response['english_response']}")
    else:
        print(f"Error: {response['error']}")