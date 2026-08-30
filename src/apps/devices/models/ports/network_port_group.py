from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.devices.models.device_model import DeviceModel
from apps.core.models import PortPhysicalType


class NetworkPortGroup(models.Model):
    device_model = models.ForeignKey(  # Связь с моделью устройства
        DeviceModel,
        on_delete=models.CASCADE,
        related_name="port_groups",
        verbose_name=_("Модель устройства"),
    )
    physical_type = models.CharField(
        max_length=20,
        choices=PortPhysicalType.choices,
        default=PortPhysicalType.RJ45_GE,
        db_index=True,
        verbose_name=_("Физический тип портов"),
    )

    class Meta:
        ordering = ["device_model", "physical_type"]
        verbose_name = _("Группа портов")
        verbose_name_plural = _("Группы сетевых портов")
        constraints = [
            models.UniqueConstraint(
                fields=["device_model", "physical_type"],
                name="network_port_group_device_type_unique",
            )
        ]

    def __str__(self):
        return f"{self.device_model} - {self.get_physical_type_display()}"
