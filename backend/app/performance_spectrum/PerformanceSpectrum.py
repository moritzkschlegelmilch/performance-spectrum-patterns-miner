import os
from typing import Self

import cachetools
import numpy as np
import pandas as pd
from pandas import DataFrame
import time

from models import Eventlog
import performance_spectrum.miner as psminer
from pm4py.objects.conversion.log import converter as log_converter
from pydantic_models.spectrum_filter_schema import ActivityFilter, BatchFilter, TimeFilter
from pm4py.objects.log.exporter.xes import exporter as xes_exporter


class PerformanceSpectrumBuilder:
    cache = cachetools.LRUCache(maxsize=100)

    def __init__(self, eventlog: Eventlog):
        self.eventlog = eventlog
        self.miner = psminer.SpectrumMiner(eventlog)

        # Init filter parameters with none
        self.segmentFilter = None
        self.variantFilter = None
        self.caseFilter = None

    def segment(self, activities: ActivityFilter) -> Self:
        """
        Queries the segment filter to the builder
        @param activities:
        @return:
        """
        if activities is not None and activities.start_activity and activities.end_activity:
            self.segmentFilter = activities

        return self

    def variant(self, trace: list[str]):
        """
        Queries the variant filter to the builder
        @param trace:
        @return:
        """
        self.variantFilter = trace
        return self

    def get_base_df(self, log_data):
        """
        Fetches either the variant or segment filter from depending on the set filters. This is necessary,
        because segments can include the same cases twice (for loops) while this does not occur for variants, thus
        filtering gets a bit more performant.
        The filtered df is also stored in an internal cache to avoid recalculating the same filter over and over again.
        @param log_data:
        @return:
        """
        hash = self.get_hash()
        if hash in self.cache:
            return self.cache[hash]

        if self.variantFilter is not None:
            res = self.miner.filter_entire_variant(
                log_data,
                self.variantFilter
            )
            self.cache[hash] = res
            return res

        if self.segmentFilter is not None:
            res = [self.miner.filter_variant(
                log_data,
                [self.segmentFilter.start_activity,
                 self.segmentFilter.end_activity],
                activity_index=2,
                force_real_variant=False
            )]
            self.cache[hash] = res
            return res

        res = [self.miner.prepare_log_spectrum(log_data)]
        self.cache[hash] = res

        return res

    def get_hash(self):
        """
        Calculates the hash for the current filter settings. i.e. the key of the current filter configuration in the
        internal cache
        @return:
        """
        caseFilter = tuple(self.caseFilter if self.caseFilter else [])
        variantFilter = tuple(self.variantFilter if self.variantFilter else [])
        segmentFilter = tuple(self.segmentFilter if self.segmentFilter else [])
        return hash((self.eventlog.id, caseFilter, variantFilter, segmentFilter))

    def cases(self, cases):
        """
        Queries the case filter to the builder.
        @param cases:
        @return:
        """
        if cases is not None:
            self.caseFilter = cases
        return self

    def get(self):
        """
        Builds the performance spectrum collection based on the current filter settings.
        @return:
        """
        log_data = self.eventlog.log_data()
        if self.caseFilter:
            log_data = log_data[log_data[self.eventlog.case_id].isin(self.caseFilter)].reset_index(drop=True)

        # Filter the original log df for the current filter settings
        dfs = self.get_base_df(log_data)
        # Convert the filtered log data into performance spectrum dataframes
        pms_dfs = [self.miner.prepare_pms_data(df) for df in dfs]

        # Create a collection of performance spectra from the prepared dataframes
        return PerformanceSpectrumCollection(
            self.eventlog,
            [PerformanceSpectrum(pms_df) for pms_df in pms_dfs]
        )


class PerformanceSpectrum:

    def __init__(self, records):
        self.records = records
        self.metadata = None
        self.statistics = None
        self.empty = records.empty
        # Create a filter wrapper for the performance spectrum
        self.filter_wrapper = PerformanceSpectrumFilterWrapper(self)
        # Store the original records for quartile filtering
        self.original_records = records.copy()

    @staticmethod
    def using(eventlog: Eventlog):
        """
        Creates a new PerformanceSpectrumBuilder for the given eventlog.
        @param eventlog:
        @return:
        """
        return PerformanceSpectrumBuilder(eventlog)

    def set_records(self, records: DataFrame):
        """
        Sets the records of the performance spectrum to the given dataframe and recalculates the empty state.
        @param records:
        """
        self.records = records
        self.empty = records.empty

    def batches(self, batches: BatchFilter, miner: psminer.SpectrumPatternsMiner) -> Self:
        """
        Filters the performance spectrum records based on the given batch filter.
        @param batches:
        @param miner:
        @return:
        """
        self.set_records(
            miner.cluster_pms_data(
                batches.epsilon,
                batches.minSamples,
                self.records,
                batches.batchType,
                batches.fifoOnly
            )
        )
        return self

    def quartile(self, quartile: float, miner: psminer.SpectrumPatternsMiner) -> Self:
        """
        Filters the performance spectrum records based on the given quartile.
        @param quartile:
        @param miner:
        @return:
        """
        self.set_records(miner.filter_quartiles(self.records, self.original_records, quartile))
        return self

    def time(self, start_time, end_time, miner: psminer.SpectrumPatternsMiner) -> Self:
        """
        Filters the performance spectrum records based on the given time range.
        @param start_time:
        @param end_time:
        @param miner:
        @return:
        """
        self.set_records(miner.filter_time(self.records, start_time.timestamp(), end_time.timestamp()))
        return self

    def cases(self, cases):
        """
        Filters the performance spectrum records based on the given cases.
        @param cases:
        @return:
        """
        if cases is not None:
            self.set_records(self.records[self.records['case_ID'].isin(cases)].reset_index(drop=True))

        return self


class PerformanceSpectrumFilterWrapper:
    def __init__(self, spectrum):
        self.batchFilter = None
        self.quartileFilter = None
        self.spectrum = spectrum

    def quartile(self, quartile: float) -> Self:
        """
        Queries the quartile filter to the filter wrapper.
        @param quartile:
        @return:
        """
        if quartile is not None and 0 < quartile <= 1:
            self.quartileFilter = quartile
        return self

    def batches(self, batches: BatchFilter) -> Self:
        """
        Queries the batch filter to the filter wrapper.
        @param batches:
        @return:
        """
        if (
                batches is not None and
                batches.batchType is not None
                and batches.epsilon is not None and batches.epsilon > 0
                and batches.minSamples is not None and batches.minSamples > 0
        ):
            self.batchFilter = batches
        return self

    def prepare(self, miner):
        """
        Applies all filters to the performance spectrum using the given miner.
        @param miner:
        @return:
        """
        if self.batchFilter:
            self.spectrum.batches(self.batchFilter, miner)
        if self.quartileFilter:
            self.spectrum.quartile(self.quartileFilter, miner)

    def build(self, statistics_miner):
        """
        Builds the performance spectrum by obtaining metadata required for frontend display.
        @param statistics_miner:
        """
        self.spectrum.metadata = statistics_miner.metadata(self.spectrum)


class PerformanceSpectrumCollection:
    def __init__(self, eventlog: Eventlog, spectra: list[PerformanceSpectrum]):
        self.spectra = spectra
        self.miner = psminer.SpectrumPatternsMiner(eventlog)
        self.statisticsMiner = psminer.LogStatisticsMiner(eventlog)

        self.timeFilter = None
        self.caseFilter = None
        self.range = None

    def withStatistics(self):
        # Can only be applied after the spectrum has been fully initialized, i.e. metadata was loaded
        if not self.range:
            raise ValueError("Range is not set. Please initialize spectrum first.")

        # Calculate statistics for each spectrum
        for spectrum in self.spectra:
            spectrum.statistics = self.statisticsMiner.statistics(
                spectrum,
                self.get_spectrum_df(spectrum),
                total_range=self.range,
                miner=self.miner
            )
        return self

    def spectrum(self) -> Self:
        filtered_cases = self.spectra[0].records['case_ID'].unique() if not self.spectra[0].empty else []
        for index, spectrum in enumerate(self.spectra):
            spectrum.filter_wrapper.prepare(self.miner)
            if self.timeFilter:
                spectrum.time(self.timeFilter.time_start, self.timeFilter.time_end, miner=self.miner)
            # Calculate the current spectrum records shared by all segments
            filtered_cases = np.intersect1d(filtered_cases, spectrum.records['case_ID'].unique())

        # Make sure all segments have the same cases, i.e. the intersection of all spectra
        for index, spectrum in enumerate(self.spectra):
            spectrum.cases(filtered_cases)
            spectrum.filter_wrapper.build(self.statisticsMiner)

        # Calculate the entire range for all spectra of e.g. a trace
        self.range = (
            min([spectrum.metadata.min_timestamp if not spectrum.empty else 0 for spectrum in self.spectra]),
            max([spectrum.metadata.max_timestamp if not spectrum.empty else 0 for spectrum in self.spectra]),
        )
        return self

    def time(self, time_filter: TimeFilter) -> Self:
        """
        Queries the time filter to the collection. This is required because it is applied last and must therefore be
        applied by the collection itself
        @param time_filter:
        @return:
        """
        if time_filter is not None and (time_filter.time_start is not None or time_filter.time_end is not None):
            self.timeFilter = time_filter

        return self

    def get_spectrum_df_with_collisions(self, spectrum: PerformanceSpectrum) -> DataFrame:
        """
        Filters the original event log with respect to a performance spectrum records dataframe.
        @param spectrum:
        @return:
        """
        event_log = self.miner.eventlog
        log_data = event_log.log_data()
        filter_set = set(
            zip(spectrum.records['case_ID'], spectrum.records['start_timestamp'], spectrum.records['activity']))
        log_pairs = list(
            zip(
                log_data[event_log.case_id],
                log_data[event_log.timestamp].apply(lambda x: x.timestamp()),
                log_data[event_log.activity]
            ),
        )
        mask = pd.Series(log_pairs, index=log_data.index).isin(filter_set)
        res = log_data[mask]
        return res

    def filter_df_for_cases(self, spectrum) -> DataFrame:
        """
        Filters the original event log with respect to a set of cases.
        @param spectrum:
        @return:
        """
        log_data = self.miner.eventlog.log_data()
        res = log_data[log_data[self.miner.eventlog.case_id].isin(spectrum.records['case_ID'])].reset_index(drop=True)
        return res

    def get_spectrum_df(self, spectrum: PerformanceSpectrum) -> DataFrame:
        collisions_possible = len(self.spectra) == 1
        if collisions_possible:
            return self.get_spectrum_df_with_collisions(spectrum)
        return self.filter_df_for_cases(spectrum)

    def on(self, spectrum):
        """
        Returns the filter wrapper of the performance spectrum with the given index.
        @param spectrum:
        @return:
        """
        return self.spectra[spectrum].filter_wrapper

    def to_response(self):
        """
        Converts the collection to a frontend response type object
        @return:
        """
        return {
            'spectra': [
                {
                    'records': spectrum.records.to_dict(orient='records'),
                    'empty': spectrum.empty,
                    'statistics': spectrum.statistics,
                    'metadata': spectrum.metadata,
                }
                for spectrum in self.spectra
            ],
            'event_log': self.miner.eventlog
        }

    def to_xes(self):
        """
        Exports the event log of the performance spectrum as an XES file and saves it in the exports folder.
        @return:
        """
        if not self.range:
            raise ValueError("Not initialized spectrum yet. Please initialize spectrum first.")

        eventlog = self.miner.eventlog
        filtered_df = self.filter_df_for_cases(self.spectra[0])
        parameters = {
            eventlog.case_id: "case:concept:name",
            eventlog.activity: "concept:name",
            eventlog.timestamp: "time:timestamp"
        }

        event_log = log_converter.apply(filtered_df, variant=log_converter.Variants.TO_EVENT_LOG, parameters=parameters)

        for trace in event_log:
            for event in trace:
                keys_to_remove = [k for k, v in event.items() if pd.isna(v)]
                for k in keys_to_remove:
                    del event[k]

        path = f"export_{hash(time.time())}.xes"
        os.makedirs('exports/', exist_ok=True)
        xes_exporter.apply(event_log, 'exports/' + path)

        return path
