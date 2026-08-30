from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import ProductionCountry, Countries, OSFamily, CPUArchitecture


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


class OperatingSystem(models.Model):
    vendor = models.ForeignKey(
        Vendor,
        verbose_name=_("Производитель"),
        on_delete=models.PROTECT,
        related_name="operating_systems",
    )

    name = models.CharField(
        verbose_name=_("Название"),
        max_length=120,
    )

    family = models.CharField(
        verbose_name=_("Семейство ОС"),
        max_length=20,
        choices=OSFamily,
        default=OSFamily.OTHER,
    )

    codename = models.CharField(
        verbose_name=_("Кодовое наименование"),
        max_length=80,
        blank=True,
        help_text=_("Например: Jammy Jellyfish, 22H2, VRP V200R019.")
    )

    version = models.CharField(
        verbose_name=_("Версия"),
        max_length=64,
        blank=True,
        help_text=_("Например: 22.04, 2022, 17.9.4, ESXi 8.0."),
    )

    edition = models.CharField(
        verbose_name="Редакция / вариант",
        max_length=100,
        blank=True,
        help_text=_(
            "Например: Standard, Datacenter, Enterprise, Community Edition."),
    )

    build = models.CharField(
        verbose_name="Сборка / прошивка",
        max_length=80,
        blank=True,
        help_text=_("Номер сборки, прошивки или ревизии, если применимо."),
    )

    architecture = models.CharField(
        verbose_name=_("Архитектура"),
        max_length=20,
        choices=CPUArchitecture,
        blank=True,
        help_text=_("Архитектура процессора, если применимо."),
    )

    kernel = models.CharField(
        verbose_name=_("Ядро"),
        max_length=80,
        blank=True,
        help_text=_(
            "Версия ядра или базовой платформы, если нужно детализировать."),
    )

    is_lts = models.BooleanField(
        verbose_name="LTS",
        default=False,
        help_text=_("Признак версии с длительной поддержкой."),
    )

    release_date = models.DateField(
        verbose_name=_("Дата выпуска"),
        null=True,
        blank=True,
    )

    eol_date = models.DateField(
        verbose_name=_("Дата окончания поддержки"),
        null=True,
        blank=True,
        help_text="EOL / End of Life / End of Support, если известно.",
    )

    class Meta:
        verbose_name = "Операционная система"
        verbose_name_plural = "Операционные системы"
        db_table = "devices_operating_system"
        ordering = ["name", "version"]

        constraints = [
            models.UniqueConstraint(
                fields=["vendor", "name", "version", "edition", "build"],
                name="uniq_devices_operating_system",
            ),
            models.CheckConstraint(
                condition=(
                        models.Q(release_date__isnull=True)
                        | models.Q(eol_date__isnull=True)
                        | models.Q(eol_date__gte=models.F("release_date"))
                ),
                name="devices_os_eol_not_before_release",
            ),
        ]

        indexes = [
            models.Index(
                fields=["family"],
                name="devices_os_family_idx",
            ),
            models.Index(
                fields=["eol_date"],
                name="devices_os_eol_date_idx",
            ),
        ]

    def get_full_name(self, include_architecture: bool = False) -> str:
        """
        Возвращает человекочитаемое полное название ОС.
        """
        parts = [self.name]

        if self.version:
            version = self.version.strip()

            if self.is_lts and "LTS" not in version.upper():
                version = f"{version} LTS"

            parts.append(version)

        elif self.is_lts:
            parts.append("LTS")

        if self.edition:
            parts.append(self.edition.strip())

        if self.build:
            parts.append(f"build {self.build.strip()}")

        if include_architecture and self.architecture and self.architecture != CPUArchitecture.UNKNOWN:
            parts.append(f"({self.get_architecture_display()})")

        return " ".join(parts)

    def _normalize_text_fields(self) -> None:
        """
        Удаляет лишние пробелы по краям строковых полей.
        """
        for field_name in (
                "name",
                "codename",
                "version",
                "edition",
                "build",
                "kernel",
        ):
            value = getattr(self, field_name, "")

            if isinstance(value, str):
                setattr(self, field_name, value.strip())

    def clean(self) -> None:
        """
        Валидация и нормализация данных.
        """
        super().clean()
        self._normalize_text_fields()

    def save(self, *args, **kwargs) -> None:
        """
        Перед сохранением нормализуем текстовые поля.
        Полная валидация через full_clean() выполняется только
        при явной передаче validate=True.
        Пример:
            os.save(validate=True)
        """
        validate = kwargs.pop("validate", False)

        self._normalize_text_fields()

        if validate:
            self.full_clean()

        super().save(*args, **kwargs)

    @property
    def is_supported(self) -> bool | None:
        """
        Поддерживается ли ОС на текущую дату.

        Возвращает:
            True — если поддержка ещё активна;
            False — если EOL уже наступил;
            None — если дата EOL не указана.
        """
        if self.eol_date is None:
            return None

        return timezone.localdate() <= self.eol_date

    def __str__(self) -> str:
        return self.get_full_name(include_architecture=False)


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
