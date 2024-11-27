import json
import pandas as pd
from pathlib import Path
from pydantic import BaseModel
from typing import Optional, Literal


class FileSeriesArguments(BaseModel):
    width: int = 14
    height: int = 6
    overlap: float = 0.15
    pixel_size: float = 0.17
    layout: Literal["snake", "raster"] = "snake"
    direction: Literal["vertical", "horizontal"] = "vertical"

    def build_arguments(self):
        build_arguments = "|".join(["=".join([key, str(val)]) for key, val in self.__dict__.items()])
        return build_arguments


def load_fileseries_config(folder: Path) -> FileSeriesArguments:
    """Load fileseries arguments from json file."""
    with open(folder / "fileseries_config.json") as f:
        arguments = json.load(f)
        fileseries_arguments = FileSeriesArguments(**arguments)
    return fileseries_arguments


def get_file_pattern_from_folder(folder: Path) -> str:
    """Builds a single file pattern for S tiles from a folder."""
    files = []

    cycle_folder = "Cycle" in folder.name

    number_of_pieces = 7 if cycle_folder else 6

    for file in folder.glob("*.tif"):
        pieces = file.stem.split("_")
        pieces = pieces[:number_of_pieces] + ["_".join(pieces[number_of_pieces:])]
        files.append(pieces)

    columns = ["cycle"] if cycle_folder else []
    columns += ["scene", "ST", "R", "W", "ROI", "series", "channel"]

    files = pd.DataFrame(files, columns=columns)

    files = files.query("ST == 'ST-S'")

    conserved_pieces = columns[:-2]

    for col in conserved_pieces:
        if len(files[col].unique()) != 1:
            print(col)
            raise Exception(f"There is more than one pattern in {folder}.")
        
    pattern = "_".join(files[conserved_pieces].iloc[0].values)
    pattern += "_F-{series:3}_{channel}.tif"

    return f"pattern={pattern}"


def get_fileseries_argument_for_subfolders(folder: Path, 
                                           fileseries_arguments: Optional[dict] = None) -> list:
    """Builds all filseries commands for ashlar to interpret as separate files."""
    file_series = []

    folder_list = [cycle_folder for cycle_folder in folder.parent.glob(f"**/{folder.stem}/*/") if cycle_folder.is_dir()]
    folder_list.sort()
    for folder in folder_list:
        folder_path = f'{str(folder.resolve())}'
        file_pattern = get_file_pattern_from_folder(folder)

        this_fileseries = f"fileseries|{folder_path}|{file_pattern}"

        this_fileseries += "|" + fileseries_arguments.build_arguments()

        file_series.append(f"'{this_fileseries}'")
    return file_series


def guess_image_name(folder: Path) -> str:
    """Guess an image name from the path relative to RawData."""
    ignore = True
    image_name = []
    for part in folder.parts:
        if part == "RawData":
            ignore = False
            continue
        if not ignore:
            image_name.append(part)

    image_name = "_".join(image_name)
    return image_name


def guess_save_filepath(folder: Path) -> str:
    """Guess the filepath to save the image from the path relative to RawData."""
    image_name = guess_image_name(folder)

    save_dir = folder.parent
    while save_dir.stem != "RawData":
        save_dir = save_dir.parent
    save_dir = save_dir.parent

    save_dir /= "registered"
    save_dir.mkdir(exist_ok=True)

    save_filepath = save_dir / (image_name + ".ome.tif")
    return save_filepath


def get_ashlar_command(folder: Path,
                       save_filepath: Optional[Path] = None,
                       align_channel: str = "D-DAPI_EXP-40",
                       fileseries_arguments: Optional[dict] = None) -> str:
    """Builds the command for ASHLAR to stitch and register the iamges."""
    if save_filepath is None:
        save_filepath = guess_save_filepath(folder)

    if fileseries_arguments is None:
        try:
            fileseries_arguments = load_fileseries_config(folder)
        except:
            fileseries_arguments = FileSeriesArguments()

    command = " ".join(["ashlar"] + 
                       get_fileseries_argument_for_subfolders(folder, fileseries_arguments) + 
                       ["--align-channel", '"' + align_channel + '"'] + 
                       ["--output", '"' + str(save_filepath.resolve()) + '"'])
    
    return command
