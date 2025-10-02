import hashlib
import os
import shutil
import time

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
