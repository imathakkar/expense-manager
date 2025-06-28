import pandas as pd
from io import StringIO
from utils.categorizer import categorize_transaction

def parse_csv(csv_data, is_credit=True, memory={}):
    if not csv_data.strip():
        return pd.DataFrame(columns=['Date', 'Month', 'Description', 'Amount', 'Category', 'Type'])
    df = pd.read_csv(StringIO(csv_data), header=None, quotechar='"', skipinitialspace=True)
    col_count = len(df.columns)
    new_cols = ['Date', 'Description', 'Amount'] + [f'Ignore{i}' for i in range(col_count - 3)]
    df.columns = new_cols
    df = df.drop(columns=new_cols[3:])
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    df = df.dropna(subset=['Date', 'Amount'])
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    if not is_credit:
        df['Amount'] = -df['Amount'].abs()
    df['Category'] = df['Description'].apply(lambda x: categorize_transaction(x, memory))
    df['Type'] = 'Credit' if is_credit else 'Debit'
    return df[['Date', 'Month', 'Description', 'Amount', 'Category', 'Type']]