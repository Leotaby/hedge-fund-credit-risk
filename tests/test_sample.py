import pandas as pd
from pathlib import Path

def test_sample_exists():
    # Ensure sample_returns.csv can be loaded and has at least one row
    sample_path = Path("data/sample_returns.csv")
    df = pd.read_csv(sample_path)
    assert df.shape[0] > 0
