import hashlib
import os
import shutil
import time
from bisect import bisect_right

import numpy as np
import pandas as pd
from fastapi import UploadFile

import env


def upload_file(file: UploadFile):
    # Save the uploaded file
    _, extension = os.path.splitext(file.filename)

    # Get current timestamp as a string
    timestamp = str(time.time())
    # hash current timestamp to create a unique filename
    filename = hashlib.sha256(timestamp.encode()).hexdigest()

    file_location = os.path.join(env.UPLOAD_DIR, filename + extension)
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return filename + extension


def clean_event_log(df):
    df_cleaned = df.replace([float('inf'), float('-inf')], 0)  # Replace infinite values with None
    df_cleaned = df_cleaned.fillna(0)  # Replace NaN with None
    return df_cleaned


def lnds_on_column(df: pd.DataFrame, col: str):
    """
    Longest Non-Decreasing Subsequence (LNDS) on df[col].
    Returns (lis_index_labels, lis_values).
    NaNs are ignored but original index labels are preserved.
    """
    s = df[col].dropna()
    if s.empty:
        return [], []

    a = s.to_numpy()
    idx = s.index.to_numpy()

    # positions[k] = position in `a` of subseq tail of length k+1
    positions = []
    # links to reconstruct sequence
    prev = np.full(len(a), -1)
    # actual tail values for binary search
    tails_vals = []

    for i, x in enumerate(a):
        # allows equals neighbors
        j = bisect_right(tails_vals, x)
        if j == len(tails_vals):
            tails_vals.append(x)
            positions.append(i)
        else:
            tails_vals[j] = x
            positions[j] = i
        if j > 0:
            prev[i] = positions[j-1]

    # Reconstruct LNDS
    lnds_pos = []
    k = positions[-1]
    while k != -1:
        lnds_pos.append(k)
        k = prev[k]
    lnds_pos.reverse()

    return idx[lnds_pos].tolist()