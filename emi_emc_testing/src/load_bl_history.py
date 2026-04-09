import sqlite3
import pandas as pd
from pathlib import Path

def interactive_load_baselines(db_dir: str, chip_names: list) -> dict:
    """
    Reads the SQLite DB, presents a menu of unique save_notes,
    and returns a dictionary of DataFrames mapped by chip_name.
    """
    db_path = Path(db_dir) / 'BaselineHistory.sqlite'

    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}. You must run calibration at least once.")

    # 1. Fetch strictly unique notes
    with sqlite3.connect(db_path) as conn:
        try:
            query = "SELECT DISTINCT save_notes FROM baselines WHERE save_notes != ''"
            history = pd.read_sql_query(query, conn)
        except pd.io.sql.DatabaseError:
            raise RuntimeError("Database exists, but 'baselines' table is missing. Run calibration first.")

    if history.empty:
        raise ValueError("No baseline history found in the database.")

    # 2. Print the Simplified Interactive Menu
    print("\n" + "="*40)
    print(" AVAILABLE BASELINE HISTORIES")
    print("="*40)
    for idx, row in history.iterrows():
        print(f" [{idx}] Note: '{row['save_notes']}'")
    print("="*40)

    # 3. Get User Input Safely
    while True:
        try:
            choice = input(f"\nSelect a history index to load [0-{len(history)-1}]: ")
            choice_idx = int(choice)
            if 0 <= choice_idx < len(history):
                selected_note = history.iloc[choice_idx]['save_notes']
                break
            else:
                print("Error: Index out of range. Try again.")
        except ValueError:
            print("Error: Please enter a valid number.")

    print(f"\n>>> Loading baselines for note: '{selected_note}'...")

    # 4. Fetch the actual data based strictly on the note
    chip_dfs = {}
    with sqlite3.connect(db_path) as conn:
        for chip in chip_names:
            query = f"SELECT * FROM baselines WHERE save_notes='{selected_note}' AND chip_name='{chip}'"
            df = pd.read_sql_query(query, conn)

            if df.empty:
                print(f"  WARNING: No data found for chip '{chip}' with note '{selected_note}'!")
            else:
                # Safeguard: If you used the same note twice, just keep the newest data
                if 'timestamp' in df.columns:
                    df = df.sort_values('timestamp').drop_duplicates(subset=['row', 'col'], keep='last')
                print(f"  SUCCESS: Loaded {len(df)} pixels for '{chip}'")

            chip_dfs[chip] = df

    return chip_dfs