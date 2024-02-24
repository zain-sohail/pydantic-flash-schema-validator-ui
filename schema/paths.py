from pathlib import Path

from pydantic import BaseModel
from pydantic import DirectoryPath
from pydantic import field_validator


class DataPaths(BaseModel):
    """
    Represents paths for raw and parquet data in a beamtime directory.
    """

    data_raw_dir: DirectoryPath
    data_parquet_dir: DirectoryPath

    @field_validator("data_parquet_dir", mode="before")
    @classmethod
    def check_and_create_parquet_dir(cls, v):
        v = Path(v)
        if not v.is_dir():
            v.mkdir(parents=True, exist_ok=True)
        return v

    @classmethod
    def from_beamtime_dir(
        cls,
        loader: str,
        beamtime_dir: Path,
        beamtime_id: int,
        year: int,
        daq: str,
    ) -> "DataPaths":
        """
        Create DataPaths instance from a beamtime directory and DAQ type.

        Parameters:
        - beamtime_dir (Path): Path to the beamtime directory.
        - daq (str): Type of DAQ.

        Returns:
        - DataPaths: Instance of DataPaths.
        """
        data_raw_dir_list = []
        if loader == "flash":
            beamtime_dir = beamtime_dir.joinpath(f"{year}/data/{beamtime_id}/")
            raw_path = beamtime_dir.joinpath("raw")

            for path in raw_path.glob("**/*"):
                if path.is_dir():
                    dir_name = path.name
                    if dir_name.startswith("express-") or dir_name.startswith(
                        "online-",
                    ):
                        data_raw_dir_list.append(path.joinpath(daq))
                    elif dir_name == daq.upper():
                        data_raw_dir_list.append(path)
            data_raw_dir = data_raw_dir_list[0]

        if loader == "sxp":
            beamtime_dir = beamtime_dir.joinpath(f"{year}/{beamtime_id}/")
            data_raw_dir = beamtime_dir.joinpath("raw")

        if not data_raw_dir.is_dir():
            raise FileNotFoundError("Raw data directories not found.")

        parquet_path = "processed/parquet"
        data_parquet_dir = beamtime_dir.joinpath(parquet_path)
        data_parquet_dir.mkdir(parents=True, exist_ok=True)

        return cls(data_raw_dir=data_raw_dir, data_parquet_dir=data_parquet_dir)
