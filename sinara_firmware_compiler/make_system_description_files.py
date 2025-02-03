import os
import numpy as np
import pandas as pd

from .sinara_hardware import kasli_soc
from .json_handling import to_json
from .git_handling import is_commit_in_branch


def make_crate_df(crates):
    return pd.DataFrame(crates, columns=["crate_id", "target", "peripherals"]).set_index("crate_id")


def make_system_df_compile_df(
    crate_df                              : pd.DataFrame,
    systems                               : list,
    schema_keys                           : list,
    default_config                        : list,
    artiq_zynq_branches_and_commit_hashes : dict,
    check_commits_in_branches             : bool,
    artiq_zynq_path                       : str,
    output_folder_path                    : str,
):
    data = []
    for branch, commits in artiq_zynq_branches_and_commit_hashes.items():
        for commit in commits:
            if check_commits_in_branches:
                assert is_commit_in_branch(commit, branch, artiq_zynq_path)
            for system in systems:
                system_id = system[0]
                drtio_role = ("standalone" if len(system[1]) == 1 else "master")
                for i, crate in enumerate(system[1]):
                    drtio_role = (drtio_role if i == 0 else "satellite")
                    if isinstance(crate, str):
                        crate_id = crate
                        crate_config = default_config
                    else:
                        crate_id = list(crate.keys())[0]
                        crate_config = crate[crate_id]
                    data.append([system_id, crate_id, drtio_role] + crate_config + [branch, commit])
    system_df = pd.DataFrame(
        data, columns = ["system_id", "crate_id", "drtio_role"] + schema_keys + ["artiq_zynq_branch", "artiq_zynq_commit"],
    )
    data = []
    diff_keys = ["crate_id", "drtio_role"] + schema_keys + ["artiq_zynq_branch", "artiq_zynq_commit"]
    for args, group_df in system_df.groupby(diff_keys):
        crate_id = args[0]
        k = globals()[crate_df["target"].loc[crate_id]](
            peripherals = crate_df["peripherals"].loc[crate_id],
            **dict(zip(diff_keys, args)),
        )
        system_df.loc[group_df.index, "variant"] = k.variant
        data.append([k.variant, k])
    compile_df = pd.DataFrame(data, columns=["variant", "target_instance"])
    compile_df["json_folder_path"] = output_folder_path + os.sep + compile_df["variant"]
    compile_df["json_file_path"] = compile_df["json_folder_path"] + os.sep + compile_df["variant"]+".json"
    compile_df = compile_df.set_index("variant")
    system_df["system_folder_name"] = system_df.apply(
        lambda r: f'system_{r["system_id"]}_artiq_zynq_{r["artiq_zynq_branch"]}_{r["artiq_zynq_commit"]}',
        axis="columns",
    )
    system_df["system_folder_path"] = output_folder_path + os.sep + system_df["system_folder_name"]
    system_df = system_df.set_index(["artiq_zynq_commit", "system_id", "drtio_role"]).sort_index()
    system_df["drtio_address"] = system_df.groupby(["artiq_zynq_commit", "system_id"]).cumcount()
    system_df = system_df.set_index("drtio_address", append=True)
    return system_df, compile_df


def make_to_compile(
    to_compile_file : str,
    compile_df      : pd.DataFrame,
):
    with open(to_compile_file, "a") as file:
        for variant, row in compile_df.iterrows():
            os.makedirs(row["json_folder_path"])
            row["target_instance"].to_json(
                json_file_path = row["json_file_path"],
                verbose        = False,
            )
            file.write("\n" + row["json_file_path"])
            print(os.path.basename(row["json_file_path"]))


def make_to_device_db(
    to_device_db_file : str,
    system_df         : pd.DataFrame,
    compile_df        : pd.DataFrame,
    artiq_branch      : str,
    artiq_commit      : str,
):
    data = []
    for index, group_df in system_df.groupby(level=[0,1]):
        master_id = group_df.xs(0, axis="index", level=3).index.get_level_values(2)[0]
        master = group_df.loc[*index, master_id, 0]
        output_file_path = os.path.join(master["system_folder_path"], "device_db.py")
        master_json_file_path = compile_df["json_file_path"].loc[master["variant"]]
        satellite_variants = ([] if "satellite" not in group_df.index.get_level_values(2)
                              else group_df["variant"].xs("satellite", axis="index", level=2).to_list())
        satellite_json_file_paths = compile_df["json_file_path"].loc[satellite_variants].to_list()
        data.append([
            artiq_branch, artiq_commit, output_file_path, master_json_file_path, *satellite_json_file_paths
        ])
    standard_columns = ["artiq_branch", "artiq_commit", "output_file_path", "master_json_file_path"]
    n_sat_max = max(len(l) for l in data) - len(standard_columns)
    satellite_columns = [f"satellite_{i}_json_file_path" for i in range(n_sat_max)]
    device_db_df = pd.DataFrame(data, columns=standard_columns+satellite_columns)
    device_db_df.to_csv(to_device_db_file, sep=";", header=True, index=False)
    return device_db_df