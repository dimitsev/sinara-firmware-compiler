# Sinara Firmware Compiler

... is an installable python package:

 - `git clone https://github.com/dimitsev/sinara-firmware-compiler.git sinara-firmware-compiler`
 - `cd sinara-firmware-compiler && pip install -e .`

## This package automates:

 - The creation of [system description files](https://m-labs.hk/artiq/manual-beta/building_developing.html#system-description-file) for the [Kasli SoC](https://github.com/sinara-hw/Kasli-SOC), including peripherals.
 - The creation of [device database files](https://m-labs.hk/artiq/manual-beta/environment.html#the-device-database) and [device map files](https://m-labs.hk/artiq/manual-beta/configuring.html#config-rtiomap) based on existing system description files.
 - The compilation of firmware for the Kasli SoC based on [https://git.m-labs.hk/M-Labs/artiq-zynq](https://git.m-labs.hk/M-Labs/artiq-zynq), as described in [Artiq beta manual: Building and developing ARTIQ](https://m-labs.hk/artiq/manual-beta/building_developing.html).

## What does the output look like?

The full output for our lab @ MPQ can be found in `/examples/system_description_files`.

## How to use?

Delete `/examples/system_description_files` and re-generate it by running the jupyter notebooks in `/examples` in numerical order and then running `/examples/run_compilation.py`. The python script runs the actual firmware compilation, so it takes a while to complete and is best run in a tmux session.

## Requirements

- Successfully tested on Linux.
- Might also work on Windows and Macintosh.
- The appropriate tools must all be installed and available, including but not limited to [Vivado](https://m-labs.hk/artiq/manual-beta/building_developing.html#installing-vivado) and [nix](https://m-labs.hk/artiq/manual-beta/installing.html#installing-via-nix-linux).

## Why only Kasli SoC?

Because that's all we needed in winter 2024-25. If you need to compile firmware for other Sinara hardware, feel free to extend this package!

## Ideas for new features

 - The upload of compiled binaries to a [MongoDB](https://www.mongodb.com/) database together with all relevant metadata: commit hashes, compilation options, system description files, build logs, etc.
