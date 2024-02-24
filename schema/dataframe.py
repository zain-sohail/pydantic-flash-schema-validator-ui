from typing import Any
from typing import Dict
from typing import Optional

from pydantic import BaseModel
from pydantic import field_validator
from pydantic import model_validator

from .channel import Channel


class DataFrameConfig(BaseModel):
    """
    Represents configuration for DataFrame.
    """

    daq: str
    ubid_offset: int
    forward_fill_iterations: int = 2
    split_sector_id_from_dld_time: bool = False
    sector_id_reserved_bits: Optional[int] = None
    channels: Dict[str, Any]
    units: Dict[str, str] = None
    stream_name_prefixes: Dict[str, str] = None
    stream_name_prefix: str = ""
    stream_name_postfixes: Dict[str, str] = None
    stream_name_postfix: str = ""
    beamtime_dir: Dict[str, str]
    sector_id_column: Optional[str] = None
    tof_column: Optional[str] = "dldTimeSteps"
    num_trains: Optional[int] = None

    @field_validator("channels", mode="before")
    @classmethod
    def populate_channels(cls, v):
        return {name: Channel(name=name, **data) for name, data in v.items()}

    # validate that pulseId
    @field_validator("channels", mode="after")
    @classmethod
    def check_channels(cls, v):
        if "pulseId" not in v:
            raise ValueError("Channel: pulseId must be provided.")
        return v

    # valide split_sector_id_from_dld_time and sector_id_reserved_bits
    @model_validator(mode="after")
    def check_sector_id_reserved_bits(self):
        if self.split_sector_id_from_dld_time:
            if self.sector_id_reserved_bits is None:
                raise ValueError(
                    "'split_sector_id_from_dld_time' is True",
                    "Please provide 'sector_id_reserved_bits'.",
                )
            if self.sector_id_column is None:
                print("No sector_id_column provided. Defaulting to dldSectorID.")
                self.sector_id_column = "dldSectorID"
        return self

    # compute stream_name_prefix and stream_name_postfix
    @model_validator(mode="after")
    def set_stream_name_prefix_and_postfix(self):
        if self.stream_name_prefixes is not None:
            # check if daq is in stream_name_prefixes
            if self.daq not in self.stream_name_prefixes:
                raise ValueError(
                    f"DAQ type '{self.daq}' not found in stream_name_prefixes.",
                )
            self.stream_name_prefix = self.stream_name_prefixes[self.daq]

        if self.stream_name_postfixes is not None:
            # check if daq is in stream_name_postfixes
            if self.daq not in self.stream_name_postfixes:
                raise ValueError(
                    f"DAQ type '{self.daq}' not found in stream_name_postfixes.",
                )
            self.stream_name_postfix = self.stream_name_postfixes[self.daq]

        return self
