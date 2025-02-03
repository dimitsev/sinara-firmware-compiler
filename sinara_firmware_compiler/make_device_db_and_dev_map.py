import os
import pandas as pd

from .json_handling import from_json
from .shell_handling import shell_wrapper
from .git_handling import prepare_repo_in_defined_state


urukul_cpld_hotfix = """from artiq.coredevice.urukul import CPLD

class CPLD2(CPLD):
    pass

"""

def _apply_urukul_cpld_hotfix(
    row : pd.Series, # single row from `device_db_df`, which is loaded from `to_device_db.txt`
):
    """
    Add a hotfix to `device_db.py`, see:
    https://github.com/m-labs/artiq/issues/2664
    https://github.com/m-labs/artiq/issues/2309
    """
    json_file_paths = [row["master_json_file_path"]] + row["satellite_json_file_paths"]
    sys_descs = [from_json(p) for p in json_file_paths]
    urukuls_sorted = sorted([
        per for desc in sys_descs for per in desc["peripherals"] if per["type"] == "urukul"
    ], key=lambda per: max(per["ports"]))
    ad9910_exists = any([
        True for uru in urukuls_sorted
        if "dds" not in uru.keys() or uru["dds"] == "ad9910"
    ])
    cplds_ad9912 = [
        f'device_db["urukul{j}_cpld"]' for j, uru in enumerate(urukuls_sorted)
        if "dds" in uru.keys() and uru["dds"] == "ad9912"
    ]
    if ad9910_exists and cplds_ad9912:
        with open(row["output_file_path"], "r") as file:
            lines = file.readlines()
        modified_lines = []
        in_ad9912_section = False
        for line in lines:
            if any([(c in line or c.replace("\"", "'") in line) for c in cplds_ad9912]):
                in_ad9912_section = True
            if in_ad9912_section and ('"module"' in line or "'module'" in line):
                line = line.replace("artiq.coredevice.urukul", "device_db")
            if in_ad9912_section and ('"class"' in line or "'class'" in line):
                line = line.replace("CPLD", "CPLD2")
            if in_ad9912_section and ('"arguments"' in line or "'arguments'" in line):
                in_ad9912_section = False
            modified_lines.append(line)
        with open(row["output_file_path"], "w") as file:
            file.write(urukul_cpld_hotfix + "".join(modified_lines))


def make_device_dbs_and_dev_maps(
    to_device_db_file_path : str,
    artiq_path             : str,
):
    device_db_df = pd.read_csv(to_device_db_file_path, sep=";", header=0)
    satellite_columns = [c for c in device_db_df.columns if c.startswith("satellite_")]
    device_db_df["satellite_json_file_paths"] = device_db_df[satellite_columns].apply(
        lambda row: [x for x in row if pd.notna(x)],
        axis="columns",
    )
    device_db_df = device_db_df.drop(columns=satellite_columns)
    for i, row in device_db_df.iterrows():
        device_db_path = row["output_file_path"]
        system_folder_path = os.path.dirname(device_db_path)
        os.makedirs(system_folder_path, exist_ok=True)
        prepare_repo_in_defined_state(
            repo_path = artiq_path,
            branch    = row["artiq_branch"],
            commit    = row["artiq_commit"],
        )
        command = f'artiq_ddb_template --output {device_db_path}'
        for i, path in enumerate(row["satellite_json_file_paths"]):
            command += f' --satellite {i+1} {path}'
        command += f' {row["master_json_file_path"]}'
        shell_wrapper(command, strict=True)
        dev_map_bin = os.path.join(system_folder_path, "dev_map.bin")
        dev_map_txt = os.path.join(system_folder_path, "dev_map.txt")
        shell_wrapper(f'artiq_rtiomap --device-db {device_db_path} {dev_map_bin}', strict=True)
        shell_wrapper(f'artiq_rtiomap --show {dev_map_bin} > {dev_map_txt}', strict=True)
        _apply_urukul_cpld_hotfix(row)
        drtio_role = ("master" if len(row["satellite_json_file_paths"]) > 0 else "standalone")
        for j, json_file_path in enumerate([row["master_json_file_path"]] + row["satellite_json_file_paths"]):
            if j > 0:
                drtio_role = "satellite"
            json_folder_path = os.path.dirname(json_file_path)
            json_folder_name = os.path.basename(json_folder_path)
            os.symlink(
                src = json_folder_path,
                dst = os.path.join(system_folder_path, f'{j}_{drtio_role}_{json_folder_name}'),
                target_is_directory = True,
            )