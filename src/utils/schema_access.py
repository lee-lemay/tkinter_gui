"""Schema access utilities.

Provides helpers to resolve logical field names to physical dataframe column names
based on per-dataset schema mappings stored in DatasetInfo.schema.
"""
from __future__ import annotations
from typing import Optional, Dict, Any
import pandas as pd

LOGICAL_DEFAULTS = {
    'tracks': {
        'timestamp': 'timestamp',
        'lat': 'lat',
        'lon': 'lon',
        'alt': 'alt',
        'track_id': 'track_id'
    },
    'truth': {
        'timestamp': 'timestamp',
        'lat': 'lat',
        'lon': 'lon',
        'alt': 'alt',
        'truth_id': 'id'
    },
    'errors': {
        'timestamp': 'timestamp',
        'track_id': 'track_id',
        'north_error': 'north_error',
        'east_error': 'east_error'
    }
}

def get_col(schema: Optional[Dict[str, Dict[str,str]]], role: str, logical_name: str) -> str:
    """Return physical column name for role/logical, falling back to defaults."""
    if schema and role in schema and logical_name in schema[role]:
        return schema[role][logical_name]
    return LOGICAL_DEFAULTS.get(role, {}).get(logical_name, logical_name)

def safe_series(df: Optional[pd.DataFrame], schema: Optional[Dict[str, Dict[str,str]]], role: str, logical_name: str):
    """Return a Series if column exists else empty Series."""
    import pandas as pd  # local import for safety
    if df is None or df.empty:
        return pd.Series([], dtype='float64')
    col = get_col(schema, role, logical_name)
    if col in df.columns:
        return df[col]
    return pd.Series([], dtype='float64')

__all__ = ['get_col', 'safe_series', 'LOGICAL_DEFAULTS']
