from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .common import DeviceKind, MIN_YEAR, CURRENT_YEAR, Vendor


class DeviceModel(models.Model):
    kind = models.CharField(
        max_length=20,
        choices=DeviceKind.choices,
        db_index=True,
        verbose_name=_("Тип устройства"),
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="device_models",
        verbose_name=_("Производитель"),
    )
    part_number = models.CharField(
        max_length=100,
        verbose_name=_("Парт-номер"),
        help_text=_("Уникален в рамках производителя"),
    )
    production_year = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(MIN_YEAR),
            MaxValueValidator(CURRENT_YEAR),
        ],
        verbose_name=_("Год производства"),
        help_text=_("Год производства модели"),
    )

    class Meta:
        ordering = ["kind", "vendor", "part_number"]
        verbose_name = _("Модель устройства")
        verbose_name_plural = _("Модели устройств")
        constraints = [
            models.UniqueConstraint(
                fields=["vendor", "part_number"],
                name="device_model_vendor_part_number_unique",
            ),
        ]
        indexes = [
            models.Index(
                fields=["part_number"],
                name="device_model_part_number_idx",
            ),
        ]

    def __str__(self):
        return f"{self.get_kind_display()} {self.vendor} {self.part_number}"
