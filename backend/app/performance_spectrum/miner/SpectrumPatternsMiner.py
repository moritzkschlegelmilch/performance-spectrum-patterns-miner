from pandas import DataFrame
from sklearn.cluster import DBSCAN

from models import Eventlog


class SpectrumPatternsMiner:

    def __init__(self, eventlog: Eventlog):
        self.eventlog = eventlog
        self.batch_data = None

    def cluster_pms_data(self, epsilon, min_samples, pms_df, batch_type='end') -> DataFrame:
        cols = [f"{batch_type}_timestamp"] if batch_type in ['start', 'end'] else ['start_timestamp', 'end_timestamp']

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
