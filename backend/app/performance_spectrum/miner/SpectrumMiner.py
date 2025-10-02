import pandas as pd
from pandas import DataFrame

from models import Eventlog


# class of Performance Spectrum that is used to store the performance spectrum in a format to be displayed in the
# frontend
class SpectrumMiner:
    def __init__(self, eventlog: Eventlog):
        self.eventlog = eventlog

    def prepare_pms_data(self, filtered_log) -> DataFrame:
        # prepare pms data before extraction

        pms_df = pd.DataFrame(data={
            "case_ID": filtered_log.iloc[::2][self.eventlog.case_id].array,
            "activity": filtered_log.iloc[::2][self.eventlog.activity].array,
            "start_timestamp": filtered_log.iloc[::2][self.eventlog.timestamp].array,
            "duration": filtered_log[self.eventlog.timestamp].diff().iloc[1::2].array,
            "end_timestamp": filtered_log.iloc[1::2][self.eventlog.timestamp].array,
        })

        pms_df.sort_values(by=['end_timestamp', 'start_timestamp'], inplace=True)
        pms_df.reset_index(drop=True, inplace=True)

        pms_df["start_timestamp"] = pms_df["start_timestamp"].apply(lambda x: x.timestamp())
        pms_df["end_timestamp"] = pms_df["end_timestamp"].apply(lambda x: x.timestamp())

        return pms_df

    def prepare_log_spectrum(self, log_data) -> DataFrame:
        """
        Get the Performance Spectrum for the entire log, i.e.
        for every case, start with the start event and end with the end event and take the difference as the duration.
        @return:
        """
        # Sort the dataframe by case and time
        df = log_data.sort_values(by=[self.eventlog.case_id, self.eventlog.timestamp])

        # Group by case_id and get start and end activities
        start_activities = df.groupby(self.eventlog.case_id).first().reset_index()
        end_activities = df.groupby(self.eventlog.case_id).last().reset_index()

        # Create two separate dataframes
        start_df = start_activities[[self.eventlog.case_id, self.eventlog.timestamp, self.eventlog.activity]].copy()
        end_df = end_activities[[self.eventlog.case_id, self.eventlog.timestamp, self.eventlog.activity]].copy()

        # Add a helper column to distinguish start and end
        start_df['order'] = 0
        end_df['order'] = 1

        # Concatenate start and end
        final_df = pd.concat([start_df, end_df], axis=0)

        # Sort so that for each case_id, start comes before end
        final_df = final_df.sort_values(by=[self.eventlog.case_id, 'order']).drop(columns='order').reset_index(
            drop=True)

        return final_df

    def filter_variant(self, log_data, variant: list[str], activity_index: int, force_real_variant=True):
        # Start with a mask of all True
        mask = pd.Series(True, index=log_data.index)

        # Check if each shifted activity matches the corresponding one in the variant
        for i, act in enumerate(reversed(variant[:activity_index])):
            shifted = log_data[self.eventlog.activity].shift(i)
            mask &= shifted == act

        for i, act in enumerate(variant[activity_index:]):
            shifted = log_data[self.eventlog.activity].shift(-(i + 1))
            mask &= shifted == act

        # Ensure all activities are in the same case
        for i in range(1, activity_index):
            same_case = log_data[self.eventlog.case_id] == log_data[self.eventlog.case_id].shift(i)
            mask &= same_case

        if force_real_variant:
            # Ensure the last activity is the same as the one in the variant
            mask &= log_data[self.eventlog.case_id] != log_data[self.eventlog.case_id].shift(len(variant))

        end_indices = log_data.index[mask]
        # Just get rows for the last two activities of the matched sequence
        # last activity is at end_indices, second last is one above (shift by 1)
        last_two_indices = []
        for end_idx in end_indices:
            last_two_indices.extend([end_idx - 1, end_idx])

        filtered_df = log_data.loc[last_two_indices].sort_values(
            by=[self.eventlog.case_id, self.eventlog.timestamp]).reset_index(drop=True)
        return filtered_df

    def filter_entire_variant(self, log_data, variant: list[str]):
        return [
            self.filter_variant(log_data, variant, i)
            for i in range(2, len(variant) + 1)
        ]

    def filter_segment(self, log_data, start_activity, end_activity):
        df = log_data.sort_values(by=[self.eventlog.case_id, self.eventlog.timestamp]).reset_index(drop=True)
        activity_col = self.eventlog.activity
        case_col = self.eventlog.case_id

        # Boolean mask for valid (start → end) transitions
        is_start = df[activity_col] == start_activity
        is_end_next = df[activity_col].shift(-1) == end_activity
        same_case = df[case_col] == df[case_col].shift(-1)

        mask = is_start & is_end_next & same_case
        start_indices = df.index[mask]
        end_indices = start_indices + 1

        # Combine rows into a single DataFrame
        all_indices = start_indices.tolist() + end_indices.tolist()
        filtered_df = df.loc[all_indices].sort_values(by=[case_col, self.eventlog.timestamp]).reset_index(drop=True)

        return filtered_df
