import os
import collections

from .json_handling import to_json


class sinara_hardware:

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def dict(self):
        d = {}
        for key, val in self.default_dict.items():
            if val != None:
                d[key] = val
            if hasattr(self, key) and getattr(self, key) != None:
                d[key] = getattr(self, key)
        return d
    
    def to_json(
        self,
        json_file_path : str,
        verbose        : bool = True,
    ):
        json_file_path = os.path.realpath(json_file_path, strict=False)
        to_json(
            dictionary     = self.dict,
            json_file_path = json_file_path,
            verbose        = verbose,
        )
        if hasattr(self, "build_dict"):
            json_folder_path = os.path.dirname(json_file_path)
            build_info_file_path = os.path.join(json_folder_path, "build_info.json")
            to_json(
                dictionary     = self.build_dict,
                json_file_path = build_info_file_path,
                verbose        = verbose,
            )


class dio_sma(sinara_hardware):

    # example: [dio_sma(ports=[port]).dict for port in range(12)]
    
    default_dict = {
        "type"   : "dio",
        "board"  : "DIO_SMA",
        "hw_rev" : "v1.4.1",
        "ports"  : None,
        "edge_counter"        : None,
        "bank_direction_low"  : "input",
        "bank_direction_high" : "input",
    }
    
    def __init__(
        self,
        ports : list, # such as [0] or [6]
    ):
        self.ports = ports


class fastino(sinara_hardware):

    # example: [fastino(ports=[port]).dict for port in range(0,4,2)]
    
    default_dict = {
        "type"       : "fastino",
        "hw_rev"     : "v1.3",
        "ports"      : None,
        "log2_width" : None,
    }
    
    def __init__(
        self,
        ports : list, # such as [0,1] or [6,7]
    ):
        self.ports = ports


class urukul(sinara_hardware):

    # example: [urukul(ports=[port, port+1]).dict for port in range(0,12,2)]
    
    default_dict = {
        "type"            : "urukul",
        "dds"             : None,
        "board"           : None,
        "hw_rev"          : "v1.5",
        "ports"           : None,
        "synchronization" : None,
        "refclk"          : None,
        "clk_sel"         : 2,
        "clk_div"         : None,
        "pll_n"           : None,
        "pll_en"          : None,
        "pll_vco"         : None,
    }
    
    def __init__(
        self,
        ports : list, # such as [0,1] or [6,7]
        dds   : str,  # "ad9910" or "ad9912"
    ):
        self.ports = ports
        self.dds = dds
        if self.dds == "ad9910":
            self.synchronization = True


class kasli_soc(sinara_hardware):
    
    default_dict = {
        "target"            : "kasli_soc",
        "hw_rev"            : "v1.1",
        "base"              : "use_drtio_role",
        "drtio_role"        : None,
        "enable_wrpll"      : None,
        "sed_lanes"         : None,
        "min_artiq_version" : "8.0",
        "core_addr"         : None,
        "variant"           : None,
        "peripherals"       : None,
    }

    def __init__(
        self,
        drtio_role   : str,  # "master" or "satellite" or "standalone"
        enable_wrpll : bool,
        sed_lanes    : int,  # 8 or 16 or 32
        core_addr    : str,  # example: "10.0.0.50"
        peripherals  : list, # must contain instances of peripherals
        crate_id     : str,
        artiq_zynq_branch : str, # "release-X" or "master"
        artiq_zynq_commit : str,
    ):
        assert artiq_zynq_branch in ["master"] + [f"release-{i}" for i in range(8,9,1)]
        self.drtio_role = drtio_role
        self.enable_wrpll = enable_wrpll
        self.sed_lanes = sed_lanes
        self.core_addr = core_addr
        self._peripherals = peripherals
        self.crate_id = crate_id
        self.artiq_zynq_branch = artiq_zynq_branch
        self.artiq_zynq_commit = artiq_zynq_commit

    @property
    def peripherals(self):
        return [p.dict for p in self._peripherals]

    @property
    def peripheral_names(self):
        # return example: "dio_sma_8_urukul_2" (sorted alphabetically)
        names = [p.name for p in self._peripherals]
        d = dict(sorted(collections.Counter(names).items()))
        return "_".join([key + "_" + str(val) for key, val in d.items()])

    @property
    def variant(self):
        return f"crate_{self.crate_id}"\
        +f"_kasli_soc_{self.default_dict['hw_rev']}"\
        +f"_artiq_zynq_{self.artiq_zynq_branch}_{self.artiq_zynq_commit}"\
        +f"_drtio_{self.drtio_role}"\
        +f"_wrpll_{self.enable_wrpll}"\
        +f"_sed_{self.sed_lanes}"\
        +f"_periph_{self.peripheral_names if self.peripheral_names else 'none'}"\
        +f"_addr_{self.core_addr}"

    @property
    def build_dict(self):
        return {
            "artiq_zynq_branch" : self.artiq_zynq_branch,
            "artiq_zynq_commit" : self.artiq_zynq_commit,
        }