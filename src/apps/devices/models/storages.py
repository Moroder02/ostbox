from django.db import models
from django.core.exceptions import ValidationError

from apps.commons.models import Vendor
from .models import Device


class DiskModel(models.Model):
    """
    Справочник моделей дисков.
    """
    class MediaType(models.TextChoices):
        HDD = 'HDD', 'HDD'
        SSD = 'SSD', 'SSD (SATA/SAS)'
        NVME = 'NVME', 'SSD (NVMe)'

    class InterfaceType(models.TextChoices):
        SATA = 'SATA', 'SATA'
        SAS = 'SAS', 'SAS'
        PCIE = 'PCIE', 'NVMe'

    class FormFactor(models.TextChoices):
        LFF_35 = '3.5_LFF', '3.5" LFF'
        SFF_25 = '2.5_SFF', '2.5" SFF'
        M2 = 'M.2', 'M.2'
        U2_U3 = 'U.2_U3', 'U.2 / U.3'
        EDSFF = 'EDSFF', 'EDSFF'

    class DeviceClass(models.TextChoices):
        ENTERPRISE = 'ENTERPRISE', 'Серверный / Enterprise'
        CONSUMER = 'CONSUMER', 'Потребительский'
        NAS = 'NAS', 'NAS'
        SURVEILLANCE = 'SURVEILLANCE', 'Для видеонаблюдения'
        UNKNOWN = 'UNKNOWN', 'Не определен'

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.PROTECT,
        verbose_name="Производитель",
    )
    model_name = models.CharField(
        max_length=100,
        verbose_name="Модель",
        help_text="Название модели по спецификации вендора",
    )
    capacity_gb = models.PositiveIntegerField(
        verbose_name="Емкость (ГБ)",
    )
    media_type = models.CharField(
        max_length=10,
        choices=MediaType,
        verbose_name="Тип носителя",
    )
    interface = models.CharField(
        max_length=10,
        choices=InterfaceType,
        verbose_name="Интерфейс",
    )
    form_factor = models.CharField(
        max_length=15,
        choices=FormFactor,
        verbose_name="Форм-фактор",
    )
    # rotation_rpm = models.PositiveIntegerField(
    #     null=True,
    #     blank=True,
    #     verbose_name="Скорость вращения (об/мин)",
    #     help_text="Заполняется только для HDD",
    # )
    device_class = models.CharField(
        max_length=20,
        choices=DeviceClass,
        default=DeviceClass.UNKNOWN,
        verbose_name="Класс диска",
        help_text="Серверный / потребительский класс устройства",
    )

    class Meta:
        verbose_name = "Модель диска"
        verbose_name_plural = "Модели дисков"
        ordering = ['vendor', 'model_name']
        indexes = [
            models.Index(fields=['device_class']),
        ]
        constraints = [
            # Вендор + модель должны быть уникальны
            models.UniqueConstraint(
                fields=['vendor', 'model_name'],
                name='uniq_vendor_model_name',
            ),
            # Правила совместимости типов носителей / интерфейсов / форм-факторов
            models.CheckConstraint(
                condition=~models.Q(media_type='NVME') | models.Q(interface='PCIE'),
                name='diskmodel_nvme_must_use_pcie',
            ),
            models.CheckConstraint(
                condition=~models.Q(media_type='NVME') | models.Q(form_factor__in=['U.2_U3', 'M.2', 'EDSFF']),
                name='diskmodel_nvme_valid_form_factors',
            ),
            models.CheckConstraint(
                condition=~models.Q(media_type='HDD') | models.Q(interface__in=['SATA', 'SAS']),
                name='diskmodel_hdd_must_use_sata_sas',
            ),
            models.CheckConstraint(
                condition=~models.Q(media_type='HDD') | models.Q(form_factor__in=['3.5_LFF', '2.5_SFF']),
                name='diskmodel_hdd_valid_form_factors',
            ),
            models.CheckConstraint(
                condition=~models.Q(media_type='SSD') | models.Q(interface__in=['SATA', 'SAS']),
                name='diskmodel_ssd_must_use_sata_sas',
            ),
            models.CheckConstraint(
                condition=~models.Q(media_type='SSD') | models.Q(form_factor__in=['2.5_SFF', 'M.2', 'U.2_U3', 'EDSFF']),
                name='diskmodel_ssd_valid_form_factors',
            ),
            # Скорость вращения имеет смысл только для HDD
            # models.CheckConstraint(
            #     condition=~models.Q(rotation_rpm__isnull=False) | models.Q(media_type='HDD'),
            #     name='diskmodel_rpm_only_for_hdd',
            # ),
        ]

    def clean(self):
        super().clean()

        if self.media_type == self.MediaType.NVME:
            if self.interface != self.InterfaceType.PCIE:
                raise ValidationError({'interface': "Для NVMe дисков возможен только интерфейс PCIe."})
            if self.form_factor not in [self.FormFactor.U2_U3, self.FormFactor.M2, self.FormFactor.EDSFF]:
                raise ValidationError({'form_factor': "Для NVMe дисков недоступен данный форм-фактор."})

        if self.media_type in [self.MediaType.HDD, self.MediaType.SSD]:
            if self.interface == self.InterfaceType.PCIE:
                raise ValidationError({'interface': "Интерфейс PCIe зарезервирован только для NVMe накопителей."})

        if self.media_type == self.MediaType.HDD:
            if self.form_factor not in [self.FormFactor.LFF_35, self.FormFactor.SFF_25]:
                raise ValidationError({'form_factor': "Магнитные диски (HDD) бывают только форматов 3.5\" или 2.5\"."})
            # if self.rotation_rpm is None:
            #     raise ValidationError({'rotation_rpm': "Для HDD необходимо указать скорость вращения."})

        if self.media_type == self.MediaType.SSD:
            if self.form_factor not in [self.FormFactor.SFF_25, self.FormFactor.M2, self.FormFactor.U2_U3, self.FormFactor.EDSFF]:
                raise ValidationError({'form_factor': "SSD накопители не бывают в форм-факторе 3.5\"."})

        # if self.rotation_rpm is not None and self.media_type != self.MediaType.HDD:
        #     raise ValidationError({'rotation_rpm': "Скорость вращения указывается только для HDD."})

    def __str__(self):
        return f"{self.vendor} {self.model_name} ({self.capacity_gb} GB)"


class Disk(models.Model):
    """
    Физический экземпляр диска в инфраструктуре.
    """

    class DiskStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'В эксплуатации'
        SPARE = 'SPARE', 'В резерве (ЗИП)'
        FAULTY = 'FAULTY', 'Неисправен'
        RETIRED = 'RETIRED', 'Списан'

    disk_model = models.ForeignKey(
        DiskModel,
        on_delete=models.PROTECT,
        related_name='physical_disks',
        verbose_name="Модель диска",
    )

    serial_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Серийный номер",
    )

    inventory_number = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="Инвентарный номер",
        help_text="Внутренний номер учета организации",
    )

    status = models.CharField(
        max_length=16,
        choices=DiskStatus,
        default=DiskStatus.SPARE,
        verbose_name="Статус",
    )

    server = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disks',
        verbose_name="Устройство",
    )

    # firmware = models.CharField(
    #     max_length=64,
    #     blank=True,
    #     verbose_name="Версия прошивки",
    # )

    class Meta:
        verbose_name = "Физический диск"
        verbose_name_plural = "Физические диски"
        ordering = ['disk_model__vendor', 'disk_model__model_name', 'serial_number']
        indexes = [
            models.Index(fields=['status', 'disk_model']),
            models.Index(fields=['serial_number']),
        ]
        constraints = [
            # Инвентарный номер должен быть уникальным, но может быть пустым
            models.UniqueConstraint(
                fields=['inventory_number'],
                condition=~models.Q(inventory_number__isnull=True),
                name='uniq_inventory_number',
            ),
        ]

    def clean(self):
        super().clean()

        if self.serial_number:
            self.serial_number = self.serial_number.upper().strip()

        if self.inventory_number:
            self.inventory_number = self.inventory_number.upper().strip()

        # Пример бизнес-правила. Можно убрать, если процесс позволяет.
        if self.status == self.DiskStatus.RETIRED and self.server:
            raise ValidationError({
                'server': "Списанный диск не может быть привязан к серверу."
            })

    def save(self, *args, **kwargs):
        if self.serial_number:
            self.serial_number = self.serial_number.upper().strip()
        if self.inventory_number:
            self.inventory_number = self.inventory_number.upper().strip()

        # full_clean() не вызывается при bulk_create()/update(). Учитывайте это.
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def vendor(self):
        return self.disk_model.vendor

    @property
    def model_name(self):
        return self.disk_model.model_name

    def __str__(self):
        return (
            f"{self.disk_model.vendor} {self.disk_model.model_name} "
            f"({self.disk_model.capacity_gb} GB) - SN: {self.serial_number}"
        )