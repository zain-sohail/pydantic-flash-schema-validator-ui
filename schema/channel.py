from enum import Enum
from typing import Optional

from pydantic import BaseModel
from pydantic import model_validator


class DataFormat(str, Enum):
    PER_ELECTRON = "per_electron"
    PER_PULSE = "per_pulse"
    PER_TRAIN = "per_train"


class AuxiliaryChannel(BaseModel):
    """
    Represents auxiliary channels in DLD.
    """

    name: str
    slice: int
    dtype: Optional[str] = None


class Channel(BaseModel):
    """
    Represents a data channel.
    """

    name: str
    format: DataFormat
    group_name: Optional[str] = None
    index_key: Optional[str] = None
    dataset_key: Optional[str] = None
    slice: Optional[int] = None
    dtype: Optional[str] = None
    dldAuxChannels: Optional[dict] = None
    max_hits: Optional[int] = None
    scale: Optional[float] = None

    @model_validator(mode="after")
    def set_index_dataset_key(self):
        if self.index_key and self.dataset_key:
            return self
        if self.group_name:
            self.index_key = self.group_name + "index"
            if self.name == "timeStamp":
                self.dataset_key = self.group_name + "time"
            else:
                self.dataset_key = self.group_name + "value"
        else:
            raise ValueError(
                "Channel:",
                self.name,
                "Either 'group_name' or 'index_key' AND 'dataset_key' must be provided.",
            )
        return self

    # if name is dldAux, check format to be per_train. If per_pulse, correct to per_train
    @model_validator(mode="after")
    def dldAux_format(self):
        if self.name == "dldAux":
            if self.format != DataFormat.PER_TRAIN:
                print(
                    "The correct format for dldAux is per_train, not per_pulse. Correcting.",
                )
                self.format = DataFormat.PER_TRAIN
        return self

    # validate dldAuxChannels
    @model_validator(mode="after")
    def check_dldAuxChannels(self):
        if self.name == "dldAux":
            if self.dldAuxChannels is None:
                raise ValueError(
                    f"Channel 'dldAux' requires 'dldAuxChannels' to be defined.",
                )
            for name, data in self.dldAuxChannels.items():
                # if data is int, convert to dict
                if isinstance(data, int):
                    self.dldAuxChannels[name] = AuxiliaryChannel(name=name, slice=data)
                elif isinstance(data, dict):
                    self.dldAuxChannels[name] = AuxiliaryChannel(name=name, **data)

        return self
