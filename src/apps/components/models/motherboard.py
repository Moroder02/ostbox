from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.devices.models import SocketType, MemoryType
from .abstractions import AbstractComponentModel, AbstractComponent


class MotherboardModel(AbstractComponentModel):
    socket_type = models.CharField(
        max_length=20,
        choices=SocketType.choices,
        verbose_name=_("Сокет"),
    )
    chipset = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Чипсет"),
    )
    max_memory_gb = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Максимальный объем памяти"),
        help_text=_("ГБ"),
    )
    max_memory_type = models.CharField(
        max_length=20,
        choices=MemoryType.choices,
        blank=True,
        verbose_name=_("Тип максимальной памяти"),
    )

    class Meta:
        ordering = ["vendor", "part_number"]
        verbose_name = _("Модель материнской платы")
        verbose_name_plural = _("Модели материнских плат")
        constraints = [
            models.CheckConstraint(
                condition=Q(max_memory_gb__gte=1),
                name="motherboard_model_max_memory_positive",
            ),
        ]

    def __str__(self):
        return f"Motherboard {self.vendor} {self.part_number}"


class Motherboard(AbstractComponent):
    motherboard_model = models.ForeignKey(
        MotherboardModel,
        on_delete=models.CASCADE,
        related_name="motherboards",
        verbose_name=_("Модель материнской платы"),
    )

    class Meta:
        verbose_name = _("Материнская плата")
        verbose_name_plural = _("Материнские платы")

    def __str__(self):
        identifier = self.serial_number or f"id={self.pk}"
        return f"Motherboard {self.motherboard_model.part_number} {identifier}"
