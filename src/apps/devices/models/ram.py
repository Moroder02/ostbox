from django.db import models
from django.core.exceptions import ValidationError

from apps.commons.models import MemoryType
from apps.devices.models import Device


class RAMModel(models.Model):

    class FormFactor(models.TextChoices):
        DIMM = 'DIMM', 'DIMM (288-pin, настольные/серверные)'
        SO_DIMM = 'SO-DIMM', 'SO-DIMM (ноутбуки, компактные системы)'
        RDIMM = 'RDIMM', 'RDIMM (Registered DIMM, серверные)'
        LRDIMM = 'LRDIMM', 'LRDIMM (Load-Reduced DIMM, серверные)'
        MCRDIMM = 'MCRDIMM', 'MCRDIMM (Multiplexer Clocked, DDR5 серверные)'

    # class ECCType(models.TextChoices):
    #     NONE = 'NONE', 'Non-ECC'
    #     ECC = 'ECC', 'ECC (Unbuffered ECC)'
    #     ECC_REGISTERED = 'ECC_REG', 'ECC Registered (RDIMM)'
    #     ECC_LOAD_REDUCED = 'ECC_LR', 'ECC Load-Reduced (LRDIMM)'

    vendor = models.CharField(
        max_length=100,
        verbose_name="Производитель",
        help_text="Samsung, Micron, SK Hynix, Kingston и т.д.",
    )
    model_name = models.CharField(
        max_length=100,
        verbose_name="Модель",
        help_text="Например: M393A4K40DB3-CWE (Samsung DDR4-3200 RDIMM)",
    )
    part_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Part Number (P/N)",
    )

    memory_type = models.CharField(
        max_length=10,
        choices=MemoryType,
        verbose_name="Тип памяти",
    )
    memory_speed_mts = models.PositiveIntegerField(
        verbose_name="Скорость (MT/s)",
        help_text="Например: 3200, 4800, 5600",
    )
    capacity_gb = models.PositiveIntegerField(
        verbose_name="Объём (ГБ)",
    )
    form_factor = models.CharField(
        max_length=15,
        choices=FormFactor,
        verbose_name="Форм-фактор",
    )
    # ecc_type = models.CharField(
    #     max_length=15,
    #     choices=ECCType.choices,
    #     default=ECCType.NONE,
    #     verbose_name="Тип ECC",
    # )

    # Дополнительные характеристики
    # rank = models.CharField(
    #     max_length=10,
    #     blank=True,
    #     verbose_name="Ранговость",
    #     help_text="Например: 1Rx8, 2Rx8, 1Rx4, 2Rx4",
    # )
    # voltage_v = models.DecimalField(
    #     max_digits=3,
    #     decimal_places=2,
    #     null=True,
    #     blank=True,
    #     verbose_name="Напряжение (В)",
    #     help_text="Например: 1.20, 1.35, 1.10",
    # )
    latency_cl = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Латентность (CL)",
        help_text="CAS Latency, например: 22, 16, 40",
    )

    class Meta:
        verbose_name = "Модель памяти"
        verbose_name_plural = "Модели памяти"
        ordering = ['vendor', 'model_name']
        constraints = [
            # Уникальность: вендор + модель
            models.UniqueConstraint(
                fields=['vendor', 'model_name'],
                name='uniq_ram_vendor_model',
            ),
            # P/N уникален, если указан
            models.UniqueConstraint(
                fields=['part_number'],
                condition=~models.Q(part_number=''),
                name='uniq_ram_part_number',
            ),
            # Скорость > 0
            models.CheckConstraint(
                condition=models.Q(memory_speed_mts__gt=0),
                name='ram_speed_positive',
            ),
            # Объём > 0
            models.CheckConstraint(
                condition=models.Q(capacity_gb__gt=0),
                name='ram_capacity_positive',
            ),
            # # RDIMM/LRDIMM должны быть ECC
            # models.CheckConstraint(
            #     condition=(
            #             ~models.Q(form_factor__in=['RDIMM', 'LRDIMM', 'MCRDIMM'])
            #             | models.Q(ecc_type__in=['ECC_REG', 'ECC_LR'])
            #     ),
            #     name='ram_registered_must_be_ecc',
            # ),
        ]

    def clean(self):
        super().clean()

        # Нормализация
        if self.memory_type:
            self.memory_type = self.memory_type.strip().upper()
        # if self.rank:
        #     self.rank = self.rank.strip().upper()

        # Валидация скорости
        if self.memory_speed_mts is not None:
            if self.memory_speed_mts < 800:
                raise ValidationError({
                    'memory_speed_mts': "Скорость памяти должна быть не менее 800 MT/s."
                })
            if self.memory_speed_mts > 20000:
                raise ValidationError({
                    'memory_speed_mts': "Скорость памяти выглядит нереалистично высокой."
                })

        # # Валидация ECC для серверных форм-факторов
        # if self.form_factor in ['RDIMM', 'LRDIMM', 'MCRDIMM']:
        #     if self.ecc_type not in ['ECC_REG', 'ECC_LR']:
        #         raise ValidationError({
        #             'ecc_type': "Серверные модули (RDIMM/LRDIMM/MCRDIMM) должны быть ECC."
        #         })

    def __str__(self):
        parts = [
            self.vendor,
            self.model_name,
            f"{self.capacity_gb}GB",
            f"{self.memory_type}-{self.memory_speed_mts}",
        ]
        # if self.ecc_type != self.ECCType.NONE:
        #     parts.append(self.get_ecc_type_display())
        return " ".join(parts)


class RAM(models.Model):

    class RAMStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'В эксплуатации'
        SPARE = 'SPARE', 'В резерве (ЗИП)'
        FAULTY = 'FAULTY', 'Неисправна'
        RETIRED = 'RETIRED', 'Списана'

    ram_model = models.ForeignKey(
        RAMModel,
        on_delete=models.PROTECT,
        related_name='physical_ram_modules',
        verbose_name="Модель памяти",
    )

    serial_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Серийный номер",
        help_text="SPD серийный номер",
    )

    inventory_number = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="Инвентарный номер",
    )

    status = models.CharField(
        max_length=16,
        choices=RAMStatus,
        default=RAMStatus.SPARE,
        verbose_name="Статус",
    )

    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ram_modules',
        verbose_name="Устройство",
    )

    class Meta:
        verbose_name = "Физическая память"
        verbose_name_plural = "Физическая память"
        ordering = ['ram_model__vendor', 'ram_model__model_name', 'serial_number']
        indexes = [
            models.Index(fields=['status', 'ram_model']),
            models.Index(fields=['serial_number']),
        ]
        constraints = [
            # Инвентарный номер уникален, если задан
            models.UniqueConstraint(
                fields=['inventory_number'],
                condition=~models.Q(inventory_number__isnull=True),
                name='uniq_ram_inventory_number',
            ),
            # # Уникальность позиции слота в рамках одного сервера
            # models.UniqueConstraint(
            #     fields=['device', 'slot_position'],
            #     condition=(
            #             ~models.Q(device__isnull=True)
            #             & ~models.Q(slot_position='')
            #     ),
            #     name='uniq_ram_slot_per_device',
            # ),
        ]

    def clean(self):
        super().clean()

        if self.serial_number:
            self.serial_number = self.serial_number.upper().strip()

        if self.inventory_number:
            self.inventory_number = self.inventory_number.upper().strip()

        # Бизнес-правило: списанная память не может быть в сервере
        if self.status == self.RAMStatus.RETIRED and self.device:
            raise ValidationError({
                'server': "Списанная память не может быть привязана к устройству."
            })

    def save(self, *args, **kwargs):
        if self.serial_number:
            self.serial_number = self.serial_number.upper().strip()
        if self.inventory_number:
            self.inventory_number = self.inventory_number.upper().strip()

        self.full_clean()
        super().save(*args, **kwargs)

    # Прокси-свойства для удобства
    @property
    def vendor(self):
        return self.ram_model.vendor

    @property
    def model_name(self):
        return self.ram_model.model_name

    @property
    def capacity_gb(self):
        return self.ram_model.capacity_gb

    @property
    def memory_type(self):
        return self.ram_model.memory_type

    # ДОБАВИТЬ эти свойства:
    @property
    def memory_speed_mts(self):
        return self.ram_model.memory_speed_mts

    @property
    def latency_cl(self):
        return self.ram_model.latency_cl

    @property
    def form_factor(self):
        return self.ram_model.form_factor


    def __str__(self):
        return (
            f"{self.ram_model.vendor} {self.ram_model.model_name} "
            f"({self.ram_model.capacity_gb}GB {self.ram_model.memory_type}-"
            f"{self.ram_model.memory_speed_mts}) - SN: {self.serial_number}"
        )
