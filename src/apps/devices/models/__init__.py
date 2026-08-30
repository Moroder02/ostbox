from .common import (
    Protocol,
    Vendor,
    OperatingSystem,
)
from ...core.models import CURRENT_YEAR, MIN_YEAR, DeviceKind, MemoryType, DiskType, SocketType, PortPhysicalType, \
    PortStatus, ProductionCountry, Countries, OSFamily

from .device_model import (
    DeviceModel,

)

from .device import Device

from .ports import (
    NetworkPortGroup,
    PhysicalNetworkPort,
)
