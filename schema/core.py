from typing import Optional

from pydantic import BaseModel

from .paths import DataPaths


class CoreConfig(BaseModel):
    """
    Represents core configuration for Flash.
    """

    loader: str = None
    beamline: str = None
    paths: Optional[DataPaths] = None
    beamtime_id: int = None
    year: int = None
    base_folder: Optional[str] = None
