from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.devices.models import MemoryType
from .abstractions import AbstractComponentModel, AbstractComponent


class RAMModel(AbstractComponentModel):
    memory_type = models.CharField(
        max_length=20,
        choices=MemoryType.choices,
        verbose_name=_("Тип памяти"),
    )
    memory_size_gb = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Объем памяти"),
        help_text=_("ГБ"),
    )
    base_frequency_mhz = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Базовая частота"),
        help_text=_("МГц"),
    )

    class Meta:
        ordering = ["vendor", "part_number"]
        verbose_name = _("Модель RAM")
        verbose_name_plural = _("Модели RAM")
        constraints = [
            models.CheckConstraint(
                condition=(
                        Q(memory_size_gb__gte=1)
                        & Q(base_frequency_mhz__gte=1)
                ),
                name="ram_model_size_frequency_positive",
            ),
        ]

    def __str__(self):
        return f"RAM {self.vendor} {self.part_number}"


class RAM(AbstractComponent):
    ram_model = models.ForeignKey(
        RAMModel,
        on_delete=models.CASCADE,
        related_name="rams",
        verbose_name=_("Модель RAM"),
    )

    class Meta:
        verbose_name = _("RAM")
        verbose_name_plural = _("RAM")

    def __str__(self):
        identifier = self.serial_number or f"id={self.pk}"
        return f"RAM {self.ram_model.part_number} {identifier}"
