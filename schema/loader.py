from pathlib import Path
from typing import Dict
from typing import Optional

from pydantic import BaseModel
from pydantic import model_validator

from .core import CoreConfig
from .dataframe import DataFrameConfig


class LoaderConfig(BaseModel):
    """
    Configuration for the flash loader.
    """

    core: CoreConfig
    dataframe: DataFrameConfig
    metadata: Optional[Dict] = None
    nexus: Optional[Dict] = None

    @model_validator(mode="after")
    def check_paths(self):
        if self.core.paths is None:
            # check if beamtime_id and year are set
            if self.core.beamtime_id is None or self.core.year is None:
                raise ValueError(
                    "Either 'paths' or 'beamtime_id' and 'year' must be provided.",
                )

            daq = self.dataframe.daq
            beamtime_dir_path = Path(self.dataframe.beamtime_dir[self.core.beamline])
            self.core.paths = DataPaths.from_beamtime_dir(
                self.core.loader,
                beamtime_dir_path,
                self.core.beamtime_id,
                self.core.year,
                daq,
            )

        return self
