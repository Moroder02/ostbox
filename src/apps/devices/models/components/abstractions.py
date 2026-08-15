from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.devices.models.common import Vendor
from apps.devices.models.device import Device


class AbstractComponentModel(models.Model):
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="%(class)s_set",
        verbose_name=_("Производитель"),
    )
    part_number = models.CharField(
        max_length=100,
        verbose_name=_("Парт-номер"),
        help_text=_("Уникален в рамках производителя"),
    )

    class Meta:
        abstract = True
        ordering = ["vendor", "part_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["vendor", "part_number"],
                name="%(class)s_vendor_part_number_unique",
            ),
        ]

    def __str__(self):
        return f"{self.vendor} {self.part_number}"


class AbstractComponent(models.Model):
    serial_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Серийный номер"),
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="%(class)s_components",
        verbose_name=_("Устройство"),
    )

    class Meta:
        abstract = True

    def __str__(self):
        identifier = self.serial_number or f"id={self.pk}"
        return f"{self.device} {identifier}"
