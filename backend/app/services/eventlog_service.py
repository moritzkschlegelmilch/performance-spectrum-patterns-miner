import pm4py
from fastapi import UploadFile, Path, Depends, HTTPException
from sqlalchemy.orm import Session
from pm4py.objects.conversion.log import converter as log_converter

import constants
import helper
from database import SessionLocal, get_db
from event_log_cache import get_log_data, remove_from_cache
from models import Eventlog
from pydantic_models.spectrum_filter_schema import SpectrumFilterRequest
from performance_spectrum.PerformanceSpectrum import PerformanceSpectrum, PerformanceSpectrumCollection


# Set the basic metadata columns of the event log.
def update_event_log_column_data(event_log: Eventlog, case_id: str, activity: str, timestamp: str, db=SessionLocal):
    event_log.case_id = case_id
    event_log.activity = activity
    event_log.timestamp = timestamp

    db.commit()

    return True


# Get the event log for the choose data page in the frontend. Has side effect of updating trace and case count
def get_event_log_field_choosing_data(event_log: Eventlog, db=SessionLocal):
    # Retrieve event log data
    log_data = get_log_data(event_log)

    event_log.entry_count = len(log_data)
    df = helper.clean_event_log(log_converter.apply(log_data, variant=log_converter.Variants.TO_DATA_FRAME)[:20])
    event_log.column_count = log_data.shape[1]

    # Check if the event log has at least 3 columns, otherwise no useful configuration is possible
    if event_log.column_count < 3:
        raise HTTPException(status_code=400, detail={'err': constants.INVALID_EVENT_LOG_ERROR, 'id': event_log.id})
    db.commit()
    db.refresh(event_log)
    return {"event_log": event_log, "df": df.to_dict(orient="records")}


# Helper function to get the event log from the database
def get_event_log(event_log_id: int = Path(...), db: Session = Depends(get_db)):
    event_log = get_event_log_simple(event_log_id, db)

    # If metadata is not set, raise an error
    if not event_log.case_id or not event_log.activity or not event_log.timestamp:
        raise HTTPException(400, {'err': constants.NOT_CONFIGURED_ERROR, 'id': event_log.id})
    return event_log


# Helper function to get the event log from the database
def get_event_log_simple(event_log_id: int = Path(...), db: Session = Depends(get_db)):
    event_log = db.query(Eventlog).filter(Eventlog.id == event_log_id).first()
    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")
    return event_log


# Basic upload function for the event log with name and file
def upload_event_log(name: str, file: UploadFile, db: SessionLocal):
    filename = helper.upload_file(file)

    event_log = Eventlog(name=name, path=filename, case_id=None, timestamp=None, activity=None)
    db.add(event_log)
    db.commit()
    db.refresh(event_log)

    return event_log


def get_mined_event_log_spectrum_collection(event_log: Eventlog, filters: SpectrumFilterRequest):
    query = PerformanceSpectrum.using(event_log)

    global_filters = filters.global_filters
    if global_filters.variant:
        query = query.variant(global_filters.variant)
    elif global_filters.activities:
        query = query.segment(global_filters.activities)

    collection: PerformanceSpectrumCollection = query.cases(global_filters.cases).get()
    collection.time(global_filters.time)

    for spectrumfilter in filters.spectra:
        collection.on(spectrumfilter.on).batches(spectrumfilter.batches).quartile(spectrumfilter.quartile)

    return collection.spectrum()


def get_event_log_as_file(event_log: Eventlog, filters: SpectrumFilterRequest):
    return get_mined_event_log_spectrum_collection(event_log, filters).to_xes()


# Get the performance spectrum basic data to display it in the frontend.
def get_mined_event_log_data(event_log: Eventlog, filters: SpectrumFilterRequest):
    return get_mined_event_log_spectrum_collection(event_log, filters).withStatistics().to_response()


def remove_event_log_data(event_log: Eventlog, db: SessionLocal):
    db.delete(event_log)
    db.commit()
    remove_from_cache(event_log)
