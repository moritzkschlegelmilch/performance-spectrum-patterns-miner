from dataclasses import dataclass

from pandas import Timestamp


@dataclass
class PerformanceSpectrumMetadata:
    min_timestamp: Timestamp
    max_timestamp: Timestamp
    quartiles: list[float]
    mean: float
    variance: float


@dataclass
class FrontendBarChart:
    bins: list[float]
    counts: list[int]


@dataclass
class PerformanceSpectrumStatistics:
    histogram: dict
    frequency_diagram: FrontendBarChart
    frequency_end_diagram: FrontendBarChart
    case_count: int
    activities: list[str]
    traces: list[dict]
    trace_count: int
