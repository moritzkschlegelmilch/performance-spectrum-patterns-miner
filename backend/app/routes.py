import os

from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException

from fastapi.responses import FileResponse
from models import Eventlog
from pydantic_models.event_log_schema import EventLogColumnRequest
from pydantic_models.spectrum_filter_schema import SpectrumFilterRequest
from services.eventlog_service import upload_event_log, get_event_log, get_event_log_field_choosing_data, \
    update_event_log_column_data, get_mined_event_log_data, get_event_log_simple, remove_event_log_data, \
    get_event_log_as_file
from database import get_db

router = APIRouter()


# Get routes
@router.get('/event-logs')
def get_event_logs(db=Depends(get_db)):
    return db.query(Eventlog).all()


@router.get("/download/{filename}")
def download_file(filename: str):
    file_path = f"exports/{filename}"
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            media_type='application/octet-stream',
            filename=filename,
        )
    return {"error": "File not found"}


@router.get("/event-log/basic/{event_log_id}")
def get_event_log_basic_data(event_log: Eventlog = Depends(get_event_log_simple), db=Depends(get_db)):
    return get_event_log_field_choosing_data(event_log, db=db)


@router.get("/event-log/{event_log_id}/data")
def get_event_log_data(event_log: Eventlog = Depends(get_event_log)):
    return event_log


# Post routes
@router.post("/event-log/{event_log_id}/mined-data")
def get_mined_data(filters: SpectrumFilterRequest, event_log: Eventlog = Depends(get_event_log)):
    return get_mined_event_log_data(event_log, filters)


@router.post("/event-log/{event_log_id}/mined-data/export")
def export_mined_data(filters: SpectrumFilterRequest, event_log: Eventlog = Depends(get_event_log)):
    return get_event_log_as_file(event_log, filters)


@router.post("/commit-event-log/{event_log_id}")
def commit_event_log(
        request: EventLogColumnRequest,
        event_log: Eventlog = Depends(get_event_log_simple),
        db=Depends(get_db)
):
    return update_event_log_column_data(event_log, request.case_id, request.activity, request.timestamp, db=db)


@router.post("/upload-event-log/")
def upload_event_log_data(name: str = Form(...), file: UploadFile = File(...), db=Depends(get_db)):
    if not file.filename.endswith(".xes"):
        raise HTTPException(status_code=422, detail="Only .xes files are allowed")
    return upload_event_log(name, file, db)


# Delete routes
@router.delete("/delete-event-log/{event_log_id}")
def delete_event_log(event_log: Eventlog = Depends(get_event_log_simple), db=Depends(get_db)):
    return remove_event_log_data(event_log, db)
