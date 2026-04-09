import numpy as np
import pandas as pd
from pandas import DataFrame
from sklearn.cluster import DBSCAN

from helper import lnds_on_column
from models import Eventlog


class SpectrumPatternsMiner:

    def __init__(self, eventlog: Eventlog):
        self.eventlog = eventlog
        self.batch_data = None

    def cluster_pms_data(self, epsilon, min_samples, pms_df, batch_type='end', fifo_only=False) -> DataFrame:

        cols = [f"{batch_type}_timestamp"] if batch_type in ['start', 'end'] else ['start_timestamp', 'end_timestamp']

        if fifo_only:
            # sort start timestamps
            pms_df.sort_values(by="start_timestamp", ascending=True, inplace=True)
            idx = lnds_on_column(pms_df, 'end_timestamp')
            pms_df = pms_df.loc[idx]

        if epsilon == 0:
            # Exact-match clustering:
            # rows are neighbors only if all values in `cols` are exactly equal.
            # groups with size < min_samples are noise (-1).

            pms_df = pms_df.copy()

            # groupby(...).ngroup() assigns a group id to every exact duplicate group
            group_ids = pms_df.groupby(cols, sort=False, dropna=False).ngroup()

            # group sizes for each row's group
            group_sizes = group_ids.map(group_ids.value_counts())

            # Assign outlier to every point
            pms_df["cluster"] = -1

            # keep only groups large enough to be clusters
            mask = group_sizes >= min_samples

            # remap valid group ids to consecutive cluster labels 0..k-1
            valid_groups = pd.unique(group_ids[mask])
            remap = {g: i for i, g in enumerate(valid_groups)}

            pms_df.loc[mask, "cluster"] = group_ids[mask].map(remap).to_numpy()
        else:
            db = DBSCAN(eps=epsilon, min_samples=min_samples).fit(pms_df[cols])
            pms_df["cluster"] = db.labels_

        before = pms_df.copy()
        pms_df = pms_df[pms_df.cluster != -1].reset_index(drop=True)
        self.batch_data = {
            'frequency': len(pms_df) / len(before)
        }

        return pms_df

    @staticmethod
    def filter_quartiles(pms_df, original_pms_df, filtered_quartile: float) -> DataFrame:
        # Calculate the quantiles for the entire dataset
        duration_series = original_pms_df['duration'].astype('timedelta64[s]').astype(int)
        quantiles_for_filtering_lower = duration_series.quantile(filtered_quartile - 0.25)
        quantiles_for_filtering_upper = duration_series.quantile(filtered_quartile)
        pms_df = pms_df[
            (pms_df['duration'].astype('timedelta64[s]').astype(int) > quantiles_for_filtering_lower) &
            (pms_df['duration'].astype('timedelta64[s]').astype(int) <= quantiles_for_filtering_upper)
            ]

        return pms_df

    @staticmethod
    def filter_time(pms_df, start_time, end_time) -> DataFrame:
        if not len(pms_df) > 0:
            return pms_df
        # Filter the DataFrame based on the time range

        mask = (pms_df['start_timestamp'] >= start_time) & (pms_df['start_timestamp'] <= end_time)
        filtered_df = pms_df.loc[mask].reset_index(drop=True)

        return filtered_df
