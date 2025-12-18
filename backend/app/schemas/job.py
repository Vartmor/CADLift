from datetime import datetime

from pydantic import BaseModel, ConfigDict

class JobBase(BaseModel):
    job_type: str
    mode: str
    status: str
    params: dict | None = None
    error_code: str | None = None
    error_message: str | None = None


class JobRead(JobBase):
    id: str
    progress: int = 0  # Progress percentage 0-100
    input_file_id: str | None = None
    output_file_id: str | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    
    # Computed fields
    download_url: str | None = None
    dxf_download_url: str | None = None
    step_download_url: str | None = None
    glb_download_url: str | None = None
    outputName: str | None = None

    model_config = ConfigDict(from_attributes=True)


class JobCreate(BaseModel):
    job_type: str
    mode: str
    params: dict | None = None
