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


class ProductionCountry(models.TextChoices):
    FOREIGN = "foreign", _("За рубежом")
    DOMESTIC = "domestic", _("Отечественный")


class Countries(models.TextChoices):
    UNITED_KINGDOM = "GB", _("Великобритания")
    GERMANY = "DE", _("Германия")
    DENMARK = "DK", _("Дания")
    ISRAEL = "IL", _("Израиль")
    IRELAND = "IE", _("Ирландия")
    ITALY = "IT", _("Италия")
    CANADA = "CA", _("Канада")
    CHINA = "CN", _("Китай")
    LATVIA = "LV", _("Латвия")
    RUSSIA = "RU", _("Россия")
    USA = "US", _("США")
    TAIWAN = "TW", _("Тайвань")
    FINLAND = "FI", _("Финляндия")
    SWITZERLAND = "CH", _("Швейцария")
    SWEDEN = "SE", _("Швеция")
    SOUTH_KOREA = "KR", _("Южная Корея")
    JAPAN = "JP", _("Япония")


class OSFamily(models.TextChoices):
    LINUX = "linux", "Linux"
    WINDOWS_DESKTOP = "windows_desktop", "Windows (клиентская)"
    WINDOWS_SERVER = "windows_server", "Windows Server"
    UNIX = "unix", "UNIX"
    BSD = "bsd", "BSD"
    MACOS = "macos", "macOS"
    NETWORK_OS = "network_os", "Сетевая ОС / прошивка"
    HYPERVISOR = "hypervisor", "Гипервизор"
    STORAGE = "storage_os", "ОС СХД"
    SECURITY = "security_os", "ОС безопасности (МСЭ, криптошлюз)"
    EMBEDDED = "embedded", "Встроенная / специализированная"
    OTHER = "other", "Прочее"


class CPUArchitecture(models.TextChoices):
    X86 = "x86", "x86 (32-bit)"
    X86_64 = "x86_64", "x86-64"
    ARM32 = "arm32", "ARM (32-bit)"
    ARM64 = "arm64", "ARM64 (AArch64)"
    PPC64LE = "ppc64le", "POWER (ppc64le)"
    S390X = "s390x", "IBM Z (s390x)"
    MIPS = "mips", "MIPS"
    RISCV = "riscv", "RISC-V"
    UNKNOWN = "unknown", "Неизвестна"


class Vendor(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_("Название"),
    )
    production = models.CharField(
        choices=ProductionCountry,
        max_length=100,
    )
    country = models.CharField(
        choices=Countries,
        max_length=2,
        blank=True,
        null=True,
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


# class OperatingSystem(models.Model):
#     name = models.CharField(
#         max_length=100,
#         verbose_name=_("Название"),
#     )
#
#     class Meta:
#         ordering = ["name"]
#         verbose_name = _("Операционная система")
#         verbose_name_plural = _("Операционные системы")
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["name"],
#                 name="operating_system_name_unique",
#             ),
#         ]
#
#     def __str__(self):
#         return self.name


# class OperatingSystem(models.Model):
#     vendor = models.ForeignKey(
#         Vendor,
#         verbose_name=_("Производитель"),
#         on_delete=models.PROTECT,
#         related_name="operating_systems",
#     )
#
#     name = models.CharField(
#         verbose_name=_("Название"),
#         max_length=120,
#     )
#
#     family = models.CharField(
#         verbose_name=_("Семейство ОС"),
#         max_length=20,
#         choices=OSFamily,
#         default=OSFamily.OTHER,
#     )
#
#     codename = models.CharField(
#         verbose_name=_("Кодовое наименование"),
#         max_length=80,
#         blank=True,
#         help_text=_("Например: Jammy Jellyfish, 22H2, VRP V200R019.")
#     )
#
#     version = models.CharField(
#         verbose_name=_("Версия"),
#         max_length=64,
#         blank=True,
#         help_text=_("Например: 22.04, 2022, 17.9.4, ESXi 8.0."),
#     )
#
#     edition = models.CharField(
#         verbose_name="Редакция / вариант",
#         max_length=100,
#         blank=True,
#         help_text=_(
#             "Например: Standard, Datacenter, Enterprise, Community Edition."),
#     )
#
#     build = models.CharField(
#         verbose_name="Сборка / прошивка",
#         max_length=80,
#         blank=True,
#         help_text=_("Номер сборки, прошивки или ревизии, если применимо."),
#     )
#
#     architecture = models.CharField(
#         verbose_name=_("Архитектура"),
#         max_length=20,
#         choices=CPUArchitecture,
#         blank=True,
#         help_text=_("Архитектура процессора, если применимо."),
#     )
#
#     kernel = models.CharField(
#         verbose_name=_("Ядро"),
#         max_length=80,
#         blank=True,
#         help_text=_(
#             "Версия ядра или базовой платформы, если нужно детализировать."),
#     )
#
#     is_lts = models.BooleanField(
#         verbose_name="LTS",
#         default=False,
#         help_text=_("Признак версии с длительной поддержкой."),
#     )
#
#     release_date = models.DateField(
#         verbose_name=_("Дата выпуска"),
#         null=True,
#         blank=True,
#     )
#
#     eol_date = models.DateField(
#         verbose_name=_("Дата окончания поддержки"),
#         null=True,
#         blank=True,
#         help_text="EOL / End of Life / End of Support, если известно.",
#     )
#
#     class Meta:
#         verbose_name = "Операционная система"
#         verbose_name_plural = "Операционные системы"
#         db_table = "devices_operating_system"
#         ordering = ["name", "version"]
#
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["vendor", "name", "version", "edition", "build"],
#                 name="uniq_devices_operating_system",
#             ),
#             models.CheckConstraint(
#                 condition=(
#                         models.Q(release_date__isnull=True)
#                         | models.Q(eol_date__isnull=True)
#                         | models.Q(eol_date__gte=models.F("release_date"))
#                 ),
#                 name="devices_os_eol_not_before_release",
#             ),
#         ]
#
#         indexes = [
#             models.Index(
#                 fields=["family"],
#                 name="devices_os_family_idx",
#             ),
#             models.Index(
#                 fields=["eol_date"],
#                 name="devices_os_eol_date_idx",
#             ),
#         ]
#
#     def get_full_name(self, include_architecture: bool = False) -> str:
#         """
#         Возвращает человекочитаемое полное название ОС.
#         """
#         parts = [self.name]
#
#         if self.version:
#             version = self.version.strip()
#
#             if self.is_lts and "LTS" not in version.upper():
#                 version = f"{version} LTS"
#
#             parts.append(version)
#
#         elif self.is_lts:
#             parts.append("LTS")
#
#         if self.edition:
#             parts.append(self.edition.strip())
#
#         if self.build:
#             parts.append(f"build {self.build.strip()}")
#
#         if include_architecture and self.architecture and self.architecture != CPUArchitecture.UNKNOWN:
#             parts.append(f"({self.get_architecture_display()})")
#
#         return " ".join(parts)
#
#     def _normalize_text_fields(self) -> None:
#         """
#         Удаляет лишние пробелы по краям строковых полей.
#         """
#         for field_name in (
#                 "name",
#                 "codename",
#                 "version",
#                 "edition",
#                 "build",
#                 "kernel",
#         ):
#             value = getattr(self, field_name, "")
#
#             if isinstance(value, str):
#                 setattr(self, field_name, value.strip())
#
#     def clean(self) -> None:
#         """
#         Валидация и нормализация данных.
#         """
#         super().clean()
#         self._normalize_text_fields()
#
#     def save(self, *args, **kwargs) -> None:
#         """
#         Перед сохранением нормализуем текстовые поля.
#         Полная валидация через full_clean() выполняется только
#         при явной передаче validate=True.
#         Пример:
#             os.save(validate=True)
#         """
#         validate = kwargs.pop("validate", False)
#
#         self._normalize_text_fields()
#
#         if validate:
#             self.full_clean()
#
#         super().save(*args, **kwargs)
#
#     @property
#     def is_supported(self) -> bool | None:
#         """
#         Поддерживается ли ОС на текущую дату.
#
#         Возвращает:
#             True — если поддержка ещё активна;
#             False — если EOL уже наступил;
#             None — если дата EOL не указана.
#         """
#         if self.eol_date is None:
#             return None
#
#         return timezone.localdate() <= self.eol_date
#
#     def __str__(self) -> str:
#         return self.get_full_name(include_architecture=False)


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
