from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class TimeFilter(BaseModel):
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None


class ActivityFilter(BaseModel):
    start_activity: str = None
    end_activity: str = None


class BatchFilter(BaseModel):
    batchType: str = None
    epsilon: float = None
    minSamples: int = None
    fifoOnly: bool = False


CaseFilter = List[str]
VariantFilter = List[str]
QuartileFilter = float


class SpectrumFilter(BaseModel):
    on: int
    batches: Optional[BatchFilter] = None
    quartile: Optional[QuartileFilter] = None


class GlobalFilter(BaseModel):
    cases: Optional[CaseFilter] = None
    variant: Optional[VariantFilter] = None
    activities: Optional[ActivityFilter] = None
    time: Optional[TimeFilter] = None


class SpectrumFilterRequest(BaseModel):
    spectra: List[SpectrumFilter] = []
    global_filters: GlobalFilter = None
