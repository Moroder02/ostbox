from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .abstractions import AbstractComponentModel, AbstractComponent
from apps.devices.models import Device
from ...core.models import DiskType


class DiskModel(AbstractComponentModel):
    disk_type = models.CharField(
        max_length=20,
        choices=DiskType,
        db_index=True,
        verbose_name=_("Тип диска"),
    )
    size_gb = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Объем"),
        help_text=_("ГБ"),
    )
    rpm = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        verbose_name=_("Скорость вращения"),
        help_text=_("об/мин; для SSD/NVME обычно не заполняется"),
    )

    class Meta:
        ordering = ["vendor", "part_number"]
        verbose_name = _("Модель диска")
        verbose_name_plural = _("Модели дисков")
        constraints = [
            models.CheckConstraint(
                condition=Q(size_gb__gte=1),
                name="disk_model_size_positive",
            ),
            models.CheckConstraint(
                condition=(
                        Q(rpm=None)
                        | Q(rpm__gte=1)
                ),
                name="disk_model_rpm_null_or_gte_1",
            ),
        ]

    def __str__(self):
        return (
            f"Disk {self.get_disk_type_display()} "
            f"{self.vendor} {self.part_number} "
            f"{self.size_gb}GB"
        )


class Disk(AbstractComponent):
    disk_model = models.ForeignKey(
        DiskModel,
        on_delete=models.CASCADE,
        related_name="disks",
        verbose_name=_("Модель диска"),
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        related_name="disks",
        blank=True,
        null=True,
    )
    serial_number = models.CharField(
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = _("Диск")
        verbose_name_plural = _("Диски")

    def __str__(self):
        return f"Disk {self.disk_model.disk_type} {self.disk_model.size_gb}"
