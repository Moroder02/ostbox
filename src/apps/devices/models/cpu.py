from django.db import models
from django.core.exceptions import ValidationError

from apps.commons.models import Vendor, Socket, MemoryType
from apps.devices.models import Device


class ProcessorModel(models.Model):

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.PROTECT,
        verbose_name="Производитель",
    )
    # series = models.CharField(
    #     max_length=50,
    #     blank=True,
    #     db_index=True,
    #     verbose_name="Серия",
    #     help_text=(
    #         "Линейка процессора. Примеры: "
    #         "Xeon Scalable, Xeon D, Xeon E, EPYC, Ryzen 9, "
    #         "Ryzen 7, Core i9, Core i7, Pentium, Celeron, "
    #         "Graviton, Ampere Altra"
    #     ),
    # )
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
    # tdp_watts = models.PositiveIntegerField(verbose_name="TDP (Вт)")
    # pcie_lanes = models.PositiveIntegerField(
    #     null=True, blank=True, verbose_name="Линии PCIe"
    # )
    # pcie_version = models.CharField(
    #     max_length=10, blank=True, verbose_name="Версия PCIe"
    # )
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
    # max_memory_gb = models.PositiveIntegerField(
    #     null=True, blank=True, verbose_name="Макс. объем памяти (ГБ)"
    # )
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
            # models.CheckConstraint(
            #     condition=models.Q(tdp_watts__gt=0),
            #     name='proc_tdp_positive',
            # ),
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
        # if self.series:
        #     self.series = self.series.strip()
        if self.memory_type:
            self.memory_type = self.memory_type.strip()
        # if self.generation:
        #     self.generation = self.generation.strip()

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
        # if self.tdp_watts is not None and self.tdp_watts <= 0:
        #     raise ValidationError({'tdp_watts': "TDP должен быть больше нуля."})

    def __str__(self):
        parts = [self.vendor, self.model_name]
        # if self.series:
        #     parts.insert(1, f"[{self.series}]")
        if self.cores:
            parts.append(f"{self.cores}C/{self.threads}T")
        return " ".join(parts)


class Processor(models.Model):
    """
    Физический экземпляр процессора
    """
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

    # # Физический сокет на материнской плате (CPU1, CPU2, ...)
    # socket_position = models.CharField(
    #     max_length=20,
    #     blank=True,
    #     verbose_name="Позиция сокета",
    #     help_text="Например: CPU1, CPU2 (если в сервере несколько процессоров)",
    # )

    stepping = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Степпинг / ревизия",
        help_text="Ревизия кристалла (например: M1, B1)",
    )

    # microcode = models.CharField(
    #     max_length=50,
    #     blank=True,
    #     verbose_name="Версия микрокода",
    #     help_text="Актуальная версия микрокода BIOS/UEFI",
    # )

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
            # # Уникальность позиции сокета в рамках одного сервера
            # models.UniqueConstraint(
            #     fields=['server', 'socket_position'],
            #     condition=(
            #         ~models.Q(server__isnull=True)
            #         & ~models.Q(socket_position='')
            #     ),
            #     name='uniq_proc_socket_per_server',
            # ),
        ]

    def clean(self):
        super().clean()

        if self.serial_number:
            self.serial_number = self.serial_number.upper().strip()

        if self.inventory_number:
            self.inventory_number = self.inventory_number.upper().strip()

        # Бизнес-правило: списанный процессор не может быть в сервере
        if self.status == self.ProcessorStatus.RETIRED and self.device:
            raise ValidationError({
                'device': "Списанный процессор не может быть привязан к устройству."
            })

        # Активный процессор должен стоять в сервере (опционально, зависит от процессов)
        # if self.status == self.ProcessorStatus.ACTIVE and not self.server:
        #     raise ValidationError({
        #         'server': "Процессор в статусе 'В эксплуатации' должен быть привязан к серверу."
        #     })

    def save(self, *args, **kwargs):
        if self.serial_number:
            self.serial_number = self.serial_number.upper().strip()
        if self.inventory_number:
            self.inventory_number = self.inventory_number.upper().strip()

        self.full_clean()
        super().save(*args, **kwargs)

    # Прокси-свойства для удобства отображения
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