from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _

from .abstractions import AbstractComponentModel, AbstractComponent


class CPUModel(AbstractComponentModel):
    base_clock_mhz = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Базовая частота"),
        help_text=_("МГц"),
    )
    cores = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Ядра"),
        help_text=_("Количество ядер"),
    )
    threads = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Потоки"),
        help_text=_("Количество потоков"),
    )

    class Meta:
        ordering = ["vendor", "part_number"]
        verbose_name = _("Модель CPU")
        verbose_name_plural = _("Модели CPU")
        constraints = [
            models.CheckConstraint(
                condition=(Q(cores__gte=1) & Q(threads__gte=1)),
                name="cpu_model_cores_threads_positive",
            ),
            models.CheckConstraint(
                condition=Q(threads__gte=F("cores")),
                name="cpu_model_threads_gte_cores",
            ),
        ]

    def __str__(self):
        return f"CPU {self.vendor} {self.part_number}"


class CPU(AbstractComponent):
    cpu_model = models.ForeignKey(
        CPUModel,
        on_delete=models.CASCADE,
        related_name="cpus",
        verbose_name=_("Модель CPU"),
    )

    class Meta:
        verbose_name = _("CPU")
        verbose_name_plural = _("CPU")

    def __str__(self):
        identifier = self.serial_number or f"id={self.pk}"
        return f"CPU {self.cpu_model.part_number} {identifier}"
