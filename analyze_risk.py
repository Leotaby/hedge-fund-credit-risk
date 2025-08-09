#!/usr/bin/env python3
"""
analyze_risk.py

This module performs a simple risk analysis of a small number of hedge funds
based on their positions in a handful of publicly traded assets and factor
returns from the Fama–French five factor model.  It computes daily
portfolio returns, estimates factor exposures using linear regression,
calculates Value at Risk (VaR) and Expected Shortfall (ES), and generates
several plots.  All outputs are written to the ``results`` folder in
CSV and PNG formats.

The goal of this script is to demonstrate fundamental skills required in
credit and market risk management: working with structured data stored
in SQL, transforming it in Python, applying statistical models, and
communicating findings graphically.  While the funds, positions and
results are purely illustrative, the workflow reflects best practices
for reproducible analysis.
"""

import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def compute_asset_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate daily log returns for each asset.

    Parameters
    ----------
    prices : DataFrame
        DataFrame containing columns ``date``, ``asset`` and ``adj_close``.

    Returns
    -------
    DataFrame
        Contains columns ``date``, ``asset`` and ``return`` representing
        the daily log return of each asset.  Log returns are used
        because they aggregate naturally and are common in risk
        management applications.
    """
    # Pivot to wide format to compute returns by group easily
    wide = prices.pivot(index='date', columns='asset', values='adj_close').astype(float)
    # Sort by date to ensure correct ordering
    wide = wide.sort_index()
    # Compute log returns
    returns = np.log(wide / wide.shift(1)).dropna()
    # Melt back to long format
    ret_long = returns.reset_index().melt(id_vars='date', var_name='asset', value_name='return')
    return ret_long


def build_portfolio_returns(returns: pd.DataFrame, positions: pd.DataFrame) -> pd.DataFrame:
    """Construct portfolio returns for each fund given asset returns and quantities.

    Parameters
    ----------
    returns : DataFrame
        Long-form DataFrame with columns ``date``, ``asset``, ``return``.
    positions : DataFrame
        DataFrame with columns ``fund_id``, ``asset`` and ``quantity``.

    Returns
    -------
    DataFrame
        Indexed by ``date`` with columns ``fund_id`` and ``portfolio_return``.
        Contains portfolio log returns for each fund on each date where all
        underlying asset returns are available.
    """
    # Merge returns with positions
    merged = returns.merge(positions, on='asset', how='inner')
    # Weight returns by position quantity relative to portfolio market value on each date
    # First compute daily contributions for each fund
    merged['weighted_return'] = merged['return'] * merged['quantity']
    # Sum contributions per fund/date and normalise by total quantity to get average return
    grouped = merged.groupby(['date', 'fund_id'])
    portfolio_returns = grouped.apply(
        lambda df: df['weighted_return'].sum() / df['quantity'].sum()
    ).reset_index(name='portfolio_return')
    # Convert date to string to align with factors
    portfolio_returns['date'] = portfolio_returns['date'].astype(str)
    return portfolio_returns


def estimate_factor_exposures(portfolio_returns: pd.Series, factor_df: pd.DataFrame) -> (np.ndarray, float):
    """Estimate factor betas and alpha for a series of portfolio excess returns.

    Uses ordinary least squares regression without an intercept term on
    factor returns.  The intercept (alpha) is computed separately as
    the average of the residuals.

    Parameters
    ----------
    portfolio_returns : Series
        Excess returns of the portfolio (already subtracted the risk–free rate).
    factor_df : DataFrame
        DataFrame of factor returns aligned with portfolio returns.  Should
        contain columns ``mkt_rf``, ``smb``, ``hml``, ``rmw``, ``cma``.

    Returns
    -------
    (betas, alpha)
        betas : ndarray of shape (5,) containing factor loadings.
        alpha : float representing the average unexplained return.
    """
    # Prepare design matrix X and response vector y
    X = factor_df[['mkt_rf', 'smb', 'hml', 'rmw', 'cma']].to_numpy()
    y = portfolio_returns.to_numpy()
    # Solve least squares for betas
    betas, *_ = np.linalg.lstsq(X, y, rcond=None)
    # Compute residuals and alpha
    fitted = X @ betas
    residuals = y - fitted
    alpha = residuals.mean()
    return betas, alpha


def compute_var_es(returns: pd.Series, confidence: float = 0.95) -> (float, float):
    """Compute historical Value at Risk and Expected Shortfall.

    VaR is defined as the negative of the quantile at (1 - confidence).
    Expected Shortfall is the mean of returns below the VaR threshold.

    Parameters
    ----------
    returns : Series
        Series of portfolio returns.
    confidence : float, optional
        Confidence level for VaR; default 0.95 corresponding to 95% VaR.

    Returns
    -------
    (var, es)
        var : float, Value at Risk (positive number representing loss)
        es : float, Expected Shortfall (positive number)
    """
    # Convert to numpy array
    r = returns.to_numpy()
    # Compute VaR as negative of lower quantile
    var_threshold = np.quantile(r, 1 - confidence)
    var = -var_threshold
    # Expected Shortfall is mean of losses beyond VaR
    tail_losses = r[r < var_threshold]
    es = -tail_losses.mean() if len(tail_losses) > 0 else np.nan
    return var, es


def plot_cumulative_returns(portfolio_returns: pd.DataFrame, fund_id: int, output_path: Path) -> None:
    """Plot cumulative returns for a specific fund.

    Saves the figure to the provided path.
    """
    fund_data = portfolio_returns[portfolio_returns['fund_id'] == fund_id].copy()
    # Sort by date to compute cumulative returns
    fund_data = fund_data.sort_values('date')
    cum_returns = np.exp(fund_data['portfolio_return'].cumsum()) - 1
    plt.figure(figsize=(8, 4))
    plt.plot(fund_data['date'], cum_returns, label=f'Fund {fund_id}')
    plt.xticks(rotation=45)
    plt.ylabel('Cumulative Return')
    plt.title(f'Cumulative Returns for Fund {fund_id}')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_return_distribution(returns: pd.Series, var: float, fund_id: int, output_path: Path) -> None:
    """Plot the distribution of portfolio returns with VaR threshold indicated.

    Parameters
    ----------
    returns : Series
        Series of portfolio returns.
    var : float
        Value at Risk (positive number representing loss)
    fund_id : int
        Identifier of the fund.
    output_path : Path
        Path to save the figure.
    """
    plt.figure(figsize=(6, 4))
    plt.hist(returns, bins=50, alpha=0.7, color='steelblue', edgecolor='black')
    plt.axvline(-var, color='red', linestyle='--', linewidth=2, label=f'VaR (95%) = {-var:.4f}')
    plt.xlabel('Return')
    plt.ylabel('Frequency')
    plt.title(f'Return Distribution for Fund {fund_id}')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_factor_exposures(betas: np.ndarray, fund_id: int, output_path: Path) -> None:
    """Plot a bar chart of factor exposures (betas).

    Parameters
    ----------
    betas : ndarray
        Array of factor betas in order [mkt_rf, smb, hml, rmw, cma].
    fund_id : int
        Fund identifier.
    output_path : Path
        Destination for the figure file.
    """
    factors = ['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']
    plt.figure(figsize=(6, 4))
    plt.bar(factors, betas, color='teal')
    plt.ylabel('Beta')
    plt.title(f'Factor Exposures for Fund {fund_id}')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def main():
    project_dir = Path(__file__).resolve().parent.parent
    db_path = project_dir / 'risk_management.db'
    results_dir = project_dir / 'results'
    results_dir.mkdir(exist_ok=True)

    # Connect to database and load tables into pandas
    conn = sqlite3.connect(db_path)
    factor_df = pd.read_sql_query('SELECT * FROM factor_returns', conn)
    # Harmonise date format: convert factor dates from YYYYMMDD to YYYY-MM-DD
    # The Fama–French factors are stored as strings without dashes (e.g., 20171218).  Our
    # portfolio returns use ISO format (YYYY-MM-DD).  To align these two datasets,
    # convert the factor dates to ISO format before merging.  Without this
    # conversion there would be no overlapping dates because the strings differ.
    factor_df['date'] = pd.to_datetime(factor_df['date'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
    prices_df = pd.read_sql_query('SELECT * FROM asset_prices', conn)
    positions_df = pd.read_sql_query('SELECT * FROM positions', conn)
    funds_df = pd.read_sql_query('SELECT * FROM funds', conn)
    conn.close()

    # Compute asset returns
    returns_df = compute_asset_returns(prices_df)
    # Build portfolio returns
    portfolio_returns = build_portfolio_returns(returns_df, positions_df)
    # Write portfolio returns to CSV
    portfolio_returns.to_csv(results_dir / 'portfolio_returns.csv', index=False)

    # Prepare storage for summary metrics
    summary_records = []

    for fund_id, fund_name in funds_df.itertuples(index=False):
        # Extract returns for this fund
        fund_ret = portfolio_returns[portfolio_returns['fund_id'] == fund_id].copy()
        # Align with factor returns on date
        merged = fund_ret.merge(factor_df, on='date', how='inner')
        if merged.empty:
            print(f"No overlapping dates between fund {fund_id} returns and factor data.")
            continue
        # Compute excess portfolio returns by subtracting RF (converted to decimal)
        merged['excess_portfolio_return'] = merged['portfolio_return'] - merged['rf']/100.0
        # Convert factor returns from percent to decimal
        for col in ['mkt_rf', 'smb', 'hml', 'rmw', 'cma', 'rf']:
            merged[col] = merged[col] / 100.0
        # Estimate factor exposures
        betas, alpha = estimate_factor_exposures(merged['excess_portfolio_return'], merged)
        # Compute VaR and ES on simple (not excess) returns
        var, es = compute_var_es(fund_ret['portfolio_return'])
        # Append summary
        summary_records.append({
            'fund_id': fund_id,
            'fund_name': fund_name,
            'alpha': alpha,
            'beta_mkt_rf': betas[0],
            'beta_smb': betas[1],
            'beta_hml': betas[2],
            'beta_rmw': betas[3],
            'beta_cma': betas[4],
            'VaR_95': var,
            'ES_95': es,
        })
        # Plot cumulative returns
        plot_cumulative_returns(portfolio_returns, fund_id, results_dir / f'fund{fund_id}_cumulative_returns.png')
        # Plot return distribution with VaR
        plot_return_distribution(fund_ret['portfolio_return'], var, fund_id, results_dir / f'fund{fund_id}_return_distribution.png')
        # Plot factor exposures
        plot_factor_exposures(betas, fund_id, results_dir / f'fund{fund_id}_factor_exposures.png')

    # Save summary metrics
    summary_df = pd.DataFrame(summary_records)
    summary_df.to_csv(results_dir / 'summary_metrics.csv', index=False)
    print("Risk analysis complete. Results saved to 'results' directory.")


if __name__ == '__main__':
    main()