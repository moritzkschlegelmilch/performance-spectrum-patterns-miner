from collections import Counter
from dataclasses import dataclass

import numpy as np
import pandas as pd
from pandas import DataFrame

from event_log_cache import get_log_data
from models import Eventlog
from performance_spectrum.common import PerformanceSpectrumMetadata, FrontendBarChart
from performance_spectrum.miner import SpectrumPatternsMiner


@dataclass
class BatchStatistics:
    num_batches: int
    avg_size: float
    avg_duration: float
    avg_batch_interval: float
    batch_frequency: float


class LogStatisticsMiner:
    def __init__(self, event_log: Eventlog):
        self.event_log = event_log
        # Retrieve original, unfiltered log data for variant extraction
        self.original_df = get_log_data(event_log)

    @staticmethod
    def extractHistogram(df):
        # Create histogram
        num_bins = 50
        duration_col = df['duration'].astype('timedelta64[s]').astype(int)
        counts, bin_edges = np.histogram(duration_col, bins=num_bins)

        # Prepare data for JSON
        return {
            'bins': bin_edges.tolist(),  # Convert to list for JSON serialization
            'counts': counts.tolist()  # Convert to list for JSON serialization
        }

    def filterCases(self, log_df, cases_to_keep: list):
        """
        Filter the original dataframe to only include cases that are in the provided list.
        @param log_df:
        @param cases_to_keep:
        @return:
        """
        return log_df[log_df[self.event_log.case_id].isin(cases_to_keep)] if cases_to_keep is not None else log_df

    def get_counts(self, log_df):
        """
        Get the number of cases and activities in the log.
        @param log_df:
        """
        return log_df[self.event_log.case_id].nunique()

    from collections import Counter

    def extractVariants(self, log_df):
        """
        Extract the most common variants from the event log as an array with items of form {trace, count}.
        """

        # Filter original log in-place
        case_ids = log_df[self.event_log.case_id].unique()
        filtered_log = self.original_df[self.original_df[self.event_log.case_id].isin(case_ids)]

        # Sort efficiently
        filtered_log = filtered_log.sort_values([self.event_log.case_id, self.event_log.timestamp])

        # Group activities into traces
        traces_series = (
            filtered_log
            .groupby(self.event_log.case_id, sort=False)[self.event_log.activity]
            .agg(list)  # faster than apply(list)
        )

        # Convert to tuples and count variants
        trace_counter = Counter(map(tuple, traces_series.values))

        # Prepare the top 5 variants
        traces = [{'trace': trace, 'count': count} for trace, count in trace_counter.most_common(5)]

        return trace_counter, traces

    def extractActivities(self, log_df):
        filtered_log = self.filterCases(self.original_df, log_df[self.event_log.case_id].unique())
        return filtered_log[self.event_log.activity].unique().tolist()

    @staticmethod
    def create_bar_chart(bins: int, records: DataFrame, ran: tuple[float, float]):
        counts, bin_edges = np.histogram(records, bins=bins, range=ran)
        return FrontendBarChart(
            bins=bin_edges.tolist(),
            counts=counts.tolist()
        )

    @staticmethod
    def metadata(spectrum) -> PerformanceSpectrumMetadata:

        if spectrum.empty:
            return PerformanceSpectrumMetadata(
                min_timestamp=0,
                max_timestamp=0,
                quartiles=[],
                mean=0,
                variance=0
            )
        nanos = spectrum.records['duration'].astype('timedelta64[s]').astype(int)
        nanos_original = spectrum.original_records['duration'].astype('timedelta64[s]').astype(int)
        return PerformanceSpectrumMetadata(
            min_timestamp=spectrum.records['start_timestamp'].min(),
            max_timestamp=spectrum.records['end_timestamp'].max(),
            quartiles=nanos_original.quantile([0.25, 0.5, 0.75]),
            mean=nanos.mean(),
            variance=nanos.var(ddof=0)
        )

    @staticmethod
    def batchStatistics(spectrum, miner) -> BatchStatistics | None:

        if 'cluster' not in spectrum.records or miner.batch_data is None or len(spectrum.records) == 0:
            return None

        batches = spectrum.records['cluster'].unique()
        grouped_batches = spectrum.records.groupby('cluster')
        sorted_batch_times = grouped_batches.agg(
            dep=('start_timestamp', 'min')
        ).sort_values(by='dep')

        avg_duration = grouped_batches.apply(lambda x: (x['end_timestamp'] - x['start_timestamp'])).mean().mean()

        sorted_batch_times['interval'] = sorted_batch_times['dep'] - sorted_batch_times['dep'].shift()

        # Drop the first row (no previous batch to compare)
        avg_batch_interval = sorted_batch_times['interval'].dropna().mean() if len(batches) > 1 else 0

        return BatchStatistics(
            num_batches=len(batches),
            avg_size=grouped_batches.size().mean(),
            avg_duration=avg_duration,
            avg_batch_interval=avg_batch_interval,
            batch_frequency=miner.batch_data['frequency']
        )

    def statistics(self, spectrum, log_df, total_range: tuple, miner: SpectrumPatternsMiner) -> dict:

        if not spectrum.metadata:
            raise ValueError("Spectrum metadata is not set.")

        case_count = self.get_counts(log_df)
        trace_counter, traces = self.extractVariants(log_df)

        histogram = {}
        frequency_diagram = {}
        frequency_end_diagram = {}
        if not spectrum.empty:
            df = pd.DataFrame(spectrum.records)
            histogram = self.extractHistogram(df)
            frequency_diagram = self.create_bar_chart(
                200,
                spectrum.records['start_timestamp'],
                ran=total_range
            )

            frequency_end_diagram = self.create_bar_chart(
                200,
                spectrum.records['end_timestamp'],
                ran=total_range
            )

        activities = self.extractActivities(log_df)

        batch_statistics = self.batchStatistics(spectrum, miner)

        return {
            'histogram': histogram,
            'frequency_diagram': frequency_diagram,
            'frequency_end_diagram': frequency_end_diagram,
            'case_count': case_count,
            'activities': activities,
            'traces': traces,
            'traces_count': len(trace_counter),
            'batches': batch_statistics
        }
