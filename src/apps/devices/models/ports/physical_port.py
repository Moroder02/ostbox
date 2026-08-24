from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.devices.models.common import PortStatus
from apps.devices.models.ports import NetworkPortGroup
from apps.devices.models.device import Device


class PhysicalNetworkPort(models.Model):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="physical_ports",
        verbose_name=_("Устройство"),
    )
    network_port_group = models.ForeignKey(
        NetworkPortGroup,
        on_delete=models.CASCADE,
        related_name="physical_ports",
        verbose_name=_("Модель порта"),
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Имя порта"),
    )
    status = models.CharField(
        max_length=20,
        choices=PortStatus.choices,
        default=PortStatus.INACTIVE,
        db_index=True,
        verbose_name=_("Статус порта"),
    )

    class Meta:
        ordering = ["device", "name"]
        verbose_name = _("Физический сетевой порт")
        verbose_name_plural = _("Физические сетевые порты")
        constraints = [
            models.UniqueConstraint(
                fields=["device", "name"],
                name="physical_port_device_name_unique",
            ),
        ]

    def clean(self):
        super().clean()

        if self.device_id and self.network_port_group_id:
            device_model_id = (
                Device.objects.filter(pk=self.device_id)
                .values_list("device_model_id", flat=True)
                .first()
            )
            network_port_group_id = (
                NetworkPortGroup.objects.filter(pk=self.network_port_group_id)
                .values_list("device_model_id", flat=True)
                .first()
            )

            if (
                device_model_id is not None
                and network_port_group_id is not None
                and device_model_id != network_port_group_id
            ):
                raise ValidationError({
                    "network_port_group": _(
                        "Порт не относится к моделяи этого устройства."
                    ),
                })

    def __str__(self):
        return f"{self.device} - {self.name}"
