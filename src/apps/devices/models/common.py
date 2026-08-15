from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

CURRENT_YEAR = timezone.now().year
MIN_YEAR = 1900


class DeviceKind(models.TextChoices):
    SERVER = "server", _("Сервер")
    SWITCH = "switch", _("Коммутатор")
    ROUTER = "router", _("Маршрутизатор")
    STORAGE_SYSTEM = "storage_system", _("СХД")
    FIREWALL = "firewall", _("МСЭ")
    CRYPTO_GATE = "crypto_gate", _("Крипто-шлюз")


class MemoryType(models.TextChoices):
    DDR3 = "ddr3", _("DDR3")
    DDR4 = "ddr4", _("DDR4")
    DDR5 = "ddr5", _("DDR5")


class DiskType(models.TextChoices):
    SSD = "ssd", _("SSD")
    HDD = "hdd", _("HDD")
    NVME = "nvme", _("NVMe")
    SSD_NVME = "ssd_nvme", _("SSD/NVMe")
    SSD_HDD = "ssd_hdd", _("SSD/HDD")
    HDD_SSD = "hdd_ssd", _("HDD/SSD")
    HDD_NVME = "hdd_nvme", _("HDD/NVMe")
    NVME_SSD = "nvme_ssd", _("NVMe/SSD")


class SocketType(models.TextChoices):
    AM4 = "am4", _("AM4")
    AM5 = "am5", _("AM5")
    AMD = "amd", _("AMD")
    INTEL = "intel", _("Intel")


class PortPhysicalType(models.TextChoices):
    # Медные порты
    RJ45_FE = "rj45_fe", _("RJ-45 (Fast Ethernet 10/100 Mbps)")
    RJ45_GE = "rj45_ge", _("RJ-45 (Gigabit Ethernet 1 Gbps)")
    RJ45_10G = "rj45_10g", _("RJ-45 (10GBASE-T)")
    GG45 = "gg45", _("GG45/ARJ45 (Категория 7/7A)")
    TERA = "tera", _("TERA (Категория 7/7A)")

    # Оптические модули и слоты
    SFP = "sfp", _("SFP (100M/1G)")
    SFP_PLUS = "sfp_plus", _("SFP+ (10G)")
    SFP28 = "sfp28", _("SFP28 (25G)")
    QSFP_PLUS = "qsfp_plus", _("QSFP+ (40G)")
    QSFP28 = "qsfp28", _("QSFP28 (100G)")
    XFP = "xfp", _("XFP (10G)")

    # Консольный порт
    CONSOLE = "console", _("Console (RJ45/USB-B/Mini-USB)")


class PortStatus(models.TextChoices):
    ACTIVE = "active", _("Активен")
    INACTIVE = "inactive", _("Неактивен")
    DISABLED = "disabled", _("Отключен (Admin Down)")
    RESERVED = "reserved", _("Зарезервирован")
    FAULTY = "faulty", _("Неисправен")


class Vendor(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_("Название"),
    )

    class Meta:
        ordering = ["name"]
        verbose_name = _("Производитель")
        verbose_name_plural = _("Производители")
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="vendor_name_unique",
            ),
        ]

    def __str__(self):
        return self.name


class OperatingSystem(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_("Название"),
    )

    class Meta:
        ordering = ["name"]
        verbose_name = _("Операционная система")
        verbose_name_plural = _("Операционные системы")
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="operating_system_name_unique",
            ),
        ]

    def __str__(self):
        return self.name


class Protocol(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_("Название"),
    )

    class Meta:
        ordering = ["name"]
        verbose_name = _("Протокол")
        verbose_name_plural = _("Протоколы")
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="protocol_name_unique",
            ),
        ]

    def __str__(self):
        return self.name
