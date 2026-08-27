from .common import (
    MemoryType,
    DiskType,
    SocketType,
    PortPhysicalType,
    PortStatus,
    Protocol,
    DeviceKind,
    MIN_YEAR,
    CURRENT_YEAR,
    Vendor,
    ProductionCountry,
    Countries,
    OperatingSystem,
    OSFamily,
)

from .device_model import (
    DeviceModel,

)

from .device import Device

# from .componentes import (
#     CPUModel, CPU,
#     RAMModel, RAM,
#     DiskModel, Disk,
#     MotherboardModel, Motherboard,
#     AbstractComponentModel, AbstractComponent
# )

from .ports import (
    NetworkPortGroup,
    PhysicalNetworkPort,
)
