# Sinara Firmware Compiler

Installable python package:

 - `git clone https://gitlab.mpcdf.mpg.de/mpq-bloch/sinara-firmware-compiler.git sinara-firmware-compiler`
 - `cd sinara-firmware-compiler && pip install -e .`

This package automates:

 - The creation of [system description files](https://m-labs.hk/artiq/manual-beta/building_developing.html#system-description-file) for the [Kasli SoC](https://github.com/sinara-hw/Kasli-SOC), including peripherals.
 - The creation of [device database files](https://m-labs.hk/artiq/manual-beta/environment.html#the-device-database) and [device map files](https://m-labs.hk/artiq/manual-beta/configuring.html#config-rtiomap).
 - The compilation of firmware for the Kasli SoC based on [https://git.m-labs.hk/M-Labs/artiq-zynq](https://git.m-labs.hk/M-Labs/artiq-zynq) and [Artiq beta manual: Building and developing ARTIQ](https://m-labs.hk/artiq/manual-beta/building_developing.html).

If you don't already know how to compile firmware for the Kasli SoC, then read up: [MQV atoms wiki: Artiq and Sinara](https://w-mqv-atoms.qm.physik.uni-muenchen.de/doku.php?id=teams:m1machine:projects:artiq_and_sinara:start)

## Why only Kasli SoC?

Because that's all we needed in winter 2024-25. If you need to compile firmware for other Sinara hardware, feel free to add to this repository!

## Ideas for new features

 - The upload of compiled binaries to a [MongoDB](https://www.mongodb.com/) database together with all relevant metadata: commit hashes, compilation options, system description files, build logs, etc.
