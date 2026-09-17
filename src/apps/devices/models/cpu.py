from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.commons.models import Vendor, Socket, MemoryType
from apps.devices.models import Device


class ProcessorModel(models.Model):
    class Segments(models.TextChoices):
        SERVER = 'SERVER', _('Серверный'),
        DESKTOP = 'DESKTOP', _('Настольный'),
        WORKSTATION = 'WORKSTATION', _('Рабочая станция'),
        EMBEDDED = 'EMBEDDED', _('Встраиваемый')

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.PROTECT,
        verbose_name="Производитель",
    )
    model_name = models.CharField(
        max_length=100,
        verbose_name="Модель",
    )
    part_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Part Number (P/N)",
    )
    socket = models.ForeignKey(
        Socket,
        on_delete=models.PROTECT,
        related_name='processor_models',
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
    memory_type = models.CharField(
        max_length=10,
        choices=MemoryType,
        verbose_name="Тип памяти",
    )
    memory_speed_mts = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Скорость памяти (MT/s)",
        help_text="Например: 4800, 5600, 3200",
    )
    segment = models.CharField(
        max_length=20,
        choices=Segments,
        blank=True,
        db_index=True,
        verbose_name="Сегмент",
        help_text="К какой категории относится процессор",
    )

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

        if self.memory_type:
            self.memory_type = self.memory_type.strip()
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

    def __str__(self):
        parts = [self.vendor, self.model_name]
        if self.cores:
            parts.append(f"{self.cores}C/{self.threads}T")
        return " ".join(parts)


class Processor(models.Model):

    class ProcessorStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'В эксплуатации'
        SPARE = 'SPARE', 'В резерве (ЗИП)'
        FAULTY = 'FAULTY', 'Неисправен'
        RETIRED = 'RETIRED', 'Списан'

    processor_model = models.ForeignKey(
        ProcessorModel,
        on_delete=models.PROTECT,
        related_name='physical_processors',
        verbose_name="Модель процессора",
    )
    serial_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Серийный номер",
        help_text="FPO / S/N на крышке процессора",
    )
    inventory_number = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="Инвентарный номер",
    )
    status = models.CharField(
        max_length=16,
        choices=ProcessorStatus,
        default=ProcessorStatus.SPARE,
        verbose_name="Статус",
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processors',
        verbose_name="Устройство",
    )
    stepping = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Степпинг / ревизия",
        help_text="Ревизия кристалла (например: M1, B1)",
    )

    class Meta:
        verbose_name = "Физический процессор"
        verbose_name_plural = "Физические процессоры"
        ordering = ['processor_model__vendor', 'processor_model__model_name', 'serial_number']
        indexes = [
            models.Index(fields=['status', 'processor_model']),
            models.Index(fields=['serial_number']),
        ]
        constraints = [
            # Инвентарный номер уникален, если задан
            models.UniqueConstraint(
                fields=['inventory_number'],
                condition=~models.Q(inventory_number__isnull=True),
                name='uniq_proc_inventory_number',
            ),
        ]

    def clean(self):
        super().clean()
        if self.serial_number:
            self.serial_number = self.serial_number.upper().strip()
        if self.inventory_number:
            self.inventory_number = self.inventory_number.upper().strip()
        if self.status == self.ProcessorStatus.RETIRED and self.device:
            raise ValidationError({
                'device': "Списанный процессор не может быть привязан к устройству."
            })

    def save(self, *args, **kwargs):
        if self.serial_number:
            self.serial_number = self.serial_number.upper().strip()
        if self.inventory_number:
            self.inventory_number = self.inventory_number.upper().strip()

        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def vendor(self):
        return self.processor_model.vendor

    @property
    def model_name(self):
        return self.processor_model.model_name

    @property
    def cores(self):
        return self.processor_model.cores

    @property
    def threads(self):
        return self.processor_model.threads

    def __str__(self):
        return (
            f"{self.processor_model.vendor} {self.processor_model.model_name} "
            f"({self.processor_model.cores}C/{self.processor_model.threads}T) - "
        )