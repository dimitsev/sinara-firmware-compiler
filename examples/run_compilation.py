"""
Run this file in a tmux session
to guarantee that firmware compilation will not be interrupted by problems with the ssh connection!
"""

import os
import sinara_firmware_compiler as sinara


output_folder_path = os.path.abspath("system_description_files")
to_compile_file = os.path.join(output_folder_path, "to_compile.txt")

artiq_zynq_path = "/opt/m1/workspace/artiq-zynq-original-untouched"

json_file_paths = {}
with open(to_compile_file, "r") as file:
    json_file_paths = [line.strip() for line in file.readlines() if line.strip()]

# print(json_file_paths)

for json_file_path in json_file_paths:
    sinara.run_firmware_compilation(artiq_zynq_path, json_file_path)