from django.db import models
from django.core.exceptions import ValidationError
import uuid

from apps.commons.models import Vendor


class ProcessorModel(models.Model):
    class MemoryType(models.TextChoices):
        DDR3 = 'DDR3', 'DDR3'
        DDR4 = 'DDR4', 'DDR4'
        DDR5 = 'DDR5', 'DDR5'
        LPDDR4 = 'LPDDR4', 'LPDDR4/4X'
        LPDDR5 = 'LPDDR5', 'LPDDR5/5X'
        OTHER = 'OTHER', 'Другой'

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.PROTECT,
        verbose_name="Производитель",
    )
    series = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name="Серия",
        help_text=(
            "Линейка процессора. Примеры: "
            "Xeon Scalable, Xeon D, Xeon E, EPYC, Ryzen 9, "
            "Ryzen 7, Core i9, Core i7, Pentium, Celeron, "
            "Graviton, Ampere Altra"
        ),
    )
    model_name = models.CharField(
        max_length=100,
        verbose_name="Модель",
        help_text="Полное наименование (например, Xeon Gold 6438Y+ или Ryzen 9 7950X)",
    )
    part_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Part Number (P/N)",
    )
    socket = models.CharField(
        max_length=20,
        verbose_name="Сокет",
    )
    cores = models.PositiveIntegerField(verbose_name="Ядра")
    threads = models.PositiveIntegerField(verbose_name="Потоки")
    base_frequency_mhz = models.PositiveIntegerField(verbose_name="Базовая частота (МГц)")
    max_frequency_mhz = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Макс. частота Turbo (МГц)"
    )
    l3_cache_mb = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Кэш L3 (МБ)"
    )
    tdp_watts = models.PositiveIntegerField(verbose_name="TDP (Вт)")
    pcie_lanes = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Линии PCIe"
    )
    pcie_version = models.CharField(
        max_length=10, blank=True, verbose_name="Версия PCIe"
    )
    memory_type = models.CharField(
        max_length=50, blank=True, verbose_name="Тип памяти",
        help_text="Например: DDR5-4800, DDR4-3200"
    )
    max_memory_gb = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Макс. объем памяти (ГБ)"
    )
    segment = models.CharField(
        max_length=20,
        choices=[
            ('SERVER', 'Серверный'),
            ('DESKTOP', 'Настольный'),
            ('WORKSTATION', 'Рабочая станция'),
            ('EMBEDDED', 'Встраиваемый'),
        ],
        blank=True,
        db_index=True,
        verbose_name="Сегмент",
        help_text="К какой категории относится процессор",
    )
    description = models.TextField(blank=True, verbose_name="Описание")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Модель процессора"
        verbose_name_plural = "Модели процессоров"
        ordering = ['vendor', 'model_name']
        constraints = [
            models.UniqueConstraint(
                fields=['vendor', 'model_name'],
                name='uniq_proc_vendor_model',
            ),
            models.UniqueConstraint(
                fields=['part_number'],
                condition=~models.Q(part_number=''),
                name='uniq_proc_part_number',
            ),
            models.CheckConstraint(
                condition=models.Q(threads__gte=models.F('cores')),
                name='proc_threads_gte_cores',
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(max_frequency_mhz__isnull=True)
                    | models.Q(max_frequency_mhz__gte=models.F('base_frequency_mhz'))
                ),
                name='proc_turbo_gte_base',
            ),
            models.CheckConstraint(
                condition=models.Q(tdp_watts__gt=0),
                name='proc_tdp_positive',
            ),
            models.CheckConstraint(
                condition=models.Q(cores__gt=0),
                name='proc_cores_positive',
            ),
            models.CheckConstraint(
                condition=models.Q(base_frequency_mhz__gt=0),
                name='proc_base_freq_positive',
            ),
        ]

    def clean(self):
        super().clean()

        # Нормализация текстовых полей
        if self.series:
            self.series = self.series.strip()
        if self.memory_type:
            self.memory_type = self.memory_type.strip()
        if self.generation:
            self.generation = self.generation.strip()

        # Валидация числовых полей (дублирует CheckConstraint для красивых ошибок)
        if self.cores is not None and self.cores <= 0:
            raise ValidationError({'cores': "Количество ядер должно быть больше нуля."})
        if self.threads is not None and self.cores is not None and self.threads < self.cores:
            raise ValidationError({'threads': "Количество потоков не может быть меньше количества ядер."})
        if self.base_frequency_mhz is not None and self.base_frequency_mhz <= 0:
            raise ValidationError({'base_frequency_mhz': "Базовая частота должна быть больше нуля."})
        if (
            self.max_frequency_mhz is not None
            and self.base_frequency_mhz is not None
            and self.max_frequency_mhz < self.base_frequency_mhz
        ):
            raise ValidationError({
                'max_frequency_mhz': "Максимальная частота не может быть ниже базовой."
            })
        if self.tdp_watts is not None and self.tdp_watts <= 0:
            raise ValidationError({'tdp_watts': "TDP должен быть больше нуля."})

    def __str__(self):
        parts = [self.vendor, self.model_name]
        if self.series:
            parts.insert(1, f"[{self.series}]")
        if self.cores:
            parts.append(f"{self.cores}C/{self.threads}T")
        return " ".join(parts)