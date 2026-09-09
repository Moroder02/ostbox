from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from apps.commons.models import (
    OperatingSystem,
    Protocol,
    DeviceKind,
    MIN_YEAR,
    CURRENT_YEAR,
    Vendor,
    PortPhysicalType,
    PortStatus
)


class DeviceModel(models.Model):
    kind = models.CharField(
        max_length=20,
        choices=DeviceKind,
        db_index=True,
        verbose_name=_("Тип устройства"),
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="device_models",
        verbose_name=_("Производитель"),
    )
    part_number = models.CharField(
        max_length=100,
        verbose_name=_("Парт-номер"),
        help_text=_("Уникален в рамках производителя"),
    )
    production_year = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(MIN_YEAR),
            MaxValueValidator(CURRENT_YEAR),
        ],
        verbose_name=_("Год производства"),
        help_text=_("Год производства модели"),
    )

    class Meta:
        ordering = ["kind", "vendor", "part_number"]
        verbose_name = _("Модель устройства")
        verbose_name_plural = _("Модели устройств")
        constraints = [
            models.UniqueConstraint(
                fields=["vendor", "part_number"],
                name="device_model_vendor_part_number_unique",
            ),
        ]
        indexes = [
            models.Index(
                fields=["part_number"],
                name="device_model_part_number_idx",
            ),
        ]

    def __str__(self):
        return f"{self.get_kind_display()} {self.vendor} {self.part_number}"


class Device(models.Model):
    device_model = models.ForeignKey(
        DeviceModel,
        on_delete=models.CASCADE,
        related_name="devices",
        verbose_name=_("Модель устройства"),
    )
    serial_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Серийный номер"),
        help_text=_("Уникален в рамках модели устройства"),
    )
    inventory_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Инвентарный номер"),
        help_text=_("Глобально уникален"),
    )
    operating_system = models.ForeignKey(
        OperatingSystem,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="devices",
        verbose_name=_("Операционная система"),
    )
    purchase_year = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(MIN_YEAR),
            MaxValueValidator(CURRENT_YEAR + 1),
        ],
        verbose_name=_("Год приобретения"),
        help_text=_("Год приобретения устройства"),
    )

    """
    далее должно ссылаться на модель ip адреса с помощью Many to many
    или будет модель интерфейс
    """
    management_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
    )

    management_protocols = models.ManyToManyField(
        Protocol,
        blank=True,
        related_name="devices",
        verbose_name=_("Протоколы управления"),
    )

    class Meta:
        verbose_name = _("Устройство")
        verbose_name_plural = _("Устройства")
        constraints = [
            models.UniqueConstraint(
                fields=["device_model", "serial_number"],
                condition=(
                        ~Q(serial_number=None)
                        & ~Q(serial_number="")
                ),
                name="device_serial_number_unique_per_model",
            ),
            models.UniqueConstraint(
                fields=["inventory_number"],
                condition=(
                        ~Q(inventory_number=None)
                        & ~Q(inventory_number="")
                ),
                name="device_inventory_number_unique",
            ),
        ]
        indexes = [
            models.Index(
                fields=["serial_number"],
                name="device_serial_number_idx",
            ),
            models.Index(
                fields=["management_ip"],
                name="device_management_ip_idx",
            ),
            models.Index(
                fields=["purchase_year"],
                name="device_purchase_year_idx",
            ),
        ]

    def __str__(self):
        identifier = (
                self.serial_number
                or self.inventory_number
                or f"id={self.pk}"
        )
        return f"{self.device_model} {identifier}"


class NetworkPortGroup(models.Model):
    device_model = models.ForeignKey(  # Связь с моделью устройства
        DeviceModel,
        on_delete=models.CASCADE,
        related_name="port_groups",
        verbose_name=_("Модель устройства"),
    )
    physical_type = models.CharField(
        max_length=20,
        choices=PortPhysicalType,
        default=PortPhysicalType.RJ45_GE,
        db_index=True,
        verbose_name=_("Физический тип портов"),
    )

    class Meta:
        ordering = ["device_model", "physical_type"]
        verbose_name = _("Группа портов")
        verbose_name_plural = _("Группы сетевых портов")
        constraints = [
            models.UniqueConstraint(
                fields=["device_model", "physical_type"],
                name="network_port_group_device_type_unique",
            )
        ]

    def __str__(self):
        return f"{self.device_model} - {self.get_physical_type_display()}"


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
        choices=PortStatus,
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
            port_device_model_id = (
                NetworkPortGroup.objects.filter(pk=self.network_port_group_id)
                .values_list("device_model_id", flat=True)
                .first()
            )

            if (
                    device_model_id is not None
                    and port_device_model_id is not None
                    and device_model_id != port_device_model_id
            ):
                raise ValidationError({
                    "network_port_model": _(
                        "Модель порта не относится к модели этого устройства."
                    ),
                })

    def __str__(self):
        return f"{self.device} - {self.name}"
