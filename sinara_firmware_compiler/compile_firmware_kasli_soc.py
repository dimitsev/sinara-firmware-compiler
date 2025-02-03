import os
import json
import warnings

from .json_handling import from_json, to_json
from .shell_handling import shell_wrapper
from .git_handling import get_commit_date, prepare_repo_in_defined_state


def nix_build_expression_kasli_soc(
    artiq_zynq_path : str, # path of top-level directory inside git repository, where `flake.nix` is
    json_file_path  : str, # path of system description file
):
    artiq_zynq_path = os.path.realpath(artiq_zynq_path, strict=True)
    json_file_path = os.path.realpath(json_file_path, strict=True)
    drtio_role = from_json(json_file_path)["drtio_role"]
    return f"""--impure --expr '
    let
        fl = builtins.getFlake "{artiq_zynq_path}";
    in
        (fl.makeArtiqZynqPackage {{
            target  = "kasli_soc";
            variant = "{drtio_role}";
            json    = "{json_file_path}";
        }}).kasli_soc-{drtio_role}-sd
'"""


def get_nix_derivations_and_outputs(
    artiq_zynq_path : str, # path of top-level directory inside git repository, where `flake.nix` is
    json_file_path  : str, # path of system description file
):
    nix_build_expression = nix_build_expression_kasli_soc(artiq_zynq_path, json_file_path)
    r = shell_wrapper(f"nix develop --command nix derivation show {nix_build_expression}",
                      cwd=artiq_zynq_path, strict=True)
    d = json.loads(r.stdout)
    def get_unique_key(keys, unique_pattern):
        matching_keys = [k for k in keys if unique_pattern in k]
        assert len(matching_keys) == 1
        return matching_keys[0]
    sd_drv = get_unique_key(d.keys(), "-sd.drv")
    gateware_drv = get_unique_key(d[sd_drv]["inputDrvs"].keys(), "-gateware.drv")
    firmware_drv = get_unique_key(d[sd_drv]["inputDrvs"].keys(), "-firmware.drv")
    def get_nix_store_output(nix_store_drv):
        d = json.loads(shell_wrapper(f'nix derivation show "{nix_store_drv}"', strict=True).stdout)
        return d[nix_store_drv]["outputs"]["out"]["path"]
    return {
        "firmware.drv" : firmware_drv,
        "gateware.drv" : gateware_drv,
        "sd.drv" : sd_drv,
        "firmware" : get_nix_store_output(firmware_drv),
        "gateware" : get_nix_store_output(gateware_drv),
        "sd" : get_nix_store_output(sd_drv),
    }


def run_firmware_compilation(
    artiq_zynq_path : str, # path of top-level directory inside git repository, where `flake.nix` is
    json_file_path  : str, # path of system description file
):
    # ---- define file and folder structure ----
    artiq_zynq_path = os.path.realpath(artiq_zynq_path, strict=True)
    json_file_path = os.path.realpath(json_file_path, strict=True)
    json_folder_path = os.path.dirname(json_file_path)
    build_info_file_path = os.path.join(json_folder_path, "build_info.json")
    # ---- obtain nix store derivations and outputs ----
    build_info = from_json(build_info_file_path)
    build_info["artiq_zynq_commit_date"] = get_commit_date(build_info["artiq_zynq_commit"], artiq_zynq_path)
    prepare_repo_in_defined_state(
        repo_path = artiq_zynq_path,
        branch    = build_info["artiq_zynq_branch"],
        commit    = build_info["artiq_zynq_commit"],
    )
    build_info = build_info | get_nix_derivations_and_outputs(artiq_zynq_path, json_file_path)
    # ---- compile firmware ----
    nix_build_expression = nix_build_expression_kasli_soc(artiq_zynq_path, json_file_path)
    shell_wrapper(f"nix develop --command nix build --print-build-logs {nix_build_expression}",
                  cwd=artiq_zynq_path, strict=True, output_to_terminal=True)
    # ---- get build logs ----
    assert shell_wrapper("readlink result", cwd=artiq_zynq_path, strict=True).stdout.strip() == build_info["sd"]
    for output_name in ["firmware", "gateware", "sd"]:
        log_file_path = os.path.join(json_folder_path, output_name + ".log")
        shell_wrapper(f'nix log "{build_info[output_name]}" > "{log_file_path}"', strict=True)
        if output_name == "gateware":
            with open(log_file_path, "r") as log_file:
                build_info["timing_constraints_met"] = ("All user specified timing constraints are met." in log_file.read())
            if not build_info["timing_constraints_met"]:
                warnings.warn(f'Timing constraints were not met for "{json_file_path}" (see "./gateware.log").')
    # ---- write nix info to disc ----
    to_json(
        dictionary     = build_info,
        json_file_path = build_info_file_path,
        verbose        = True,
    )
    # ---- get binary ----
    boot_file_path = os.path.join(build_info["sd"], "boot.bin")
    shell_wrapper(f'cp "{boot_file_path}" "{json_folder_path}"', strict=True)
    # ---- clean up ----
    shell_wrapper("rm result", cwd=artiq_zynq_path, strict=True)