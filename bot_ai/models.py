# ruff: noqa: DJ001, DJ008
import os
from datetime import datetime

from django.db import models


class MensajeAiModel(models.Model):
    mensaje = models.CharField(max_length=255)
    respuesta = models.CharField(max_length=255)

    def __str__(self):
        return self.mensaje


def catalog_media_path(instance, filename):
    date_str = datetime.now().strftime("%Y%m%d")  # noqa: DTZ005
    file_name, file_extension = os.path.splitext(filename)  # noqa: PTH122
    new_filename = f"{file_name}_{date_str}{file_extension}"
    return f"catalogos/{instance.company.id}/{new_filename}"


class MediasForIATrainig(models.Model):
    """Save catalog of medias for IA training."""

    company = models.ForeignKey("users.CompanyModel", on_delete=models.CASCADE)
    media = models.FileField(upload_to=catalog_media_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} - {self.company}"


### Coleccion Empresa
class CompanyData(models.Model):
    """Modelo de empresa"""

    client_id = models.CharField(max_length=24, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class BrandDetails(models.Model):
    """Modelo de detalles de marca"""

    company = models.OneToOneField(CompanyData, on_delete=models.CASCADE)
    logo_url = models.URLField(max_length=500, blank=True, null=True)
    font_family = models.CharField(max_length=255, blank=True, null=True)
    tone_of_voice = models.CharField(max_length=255, blank=True, null=True)


class BrandColor(models.Model):
    """Modelo de color de marca"""

    brand_details = models.ForeignKey(BrandDetails, on_delete=models.CASCADE)
    color = models.CharField(max_length=50, blank=True, null=True)


class Contact(models.Model):
    """Modelo de contacto"""

    company = models.ForeignKey(CompanyData, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)


class AccountSettings(models.Model):
    """Modelo de configuración de cuenta"""

    company = models.OneToOneField(CompanyData, on_delete=models.CASCADE)
    account_status = models.CharField(max_length=50, blank=True, null=True)
    subscription_tier = models.CharField(max_length=50, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    renewal_date = models.DateField(blank=True, null=True)


class CustomFeature(models.Model):
    """Modelo de característica personalizada"""

    account_settings = models.ForeignKey(AccountSettings, on_delete=models.CASCADE)
    feature = models.CharField(max_length=255, blank=True, null=True)


class CatalogPreferences(models.Model):
    """Modelo de preferencias de catálogo"""

    company = models.OneToOneField(CompanyData, on_delete=models.CASCADE)
    default_currency = models.CharField(max_length=10, blank=True, null=True)
    catalog_size = models.CharField(max_length=50, blank=True, null=True)
    product_update_frequency = models.CharField(max_length=50, blank=True, null=True)


class ProductCategory(models.Model):
    """Modelo de categoría de producto"""

    catalog_preferences = models.ForeignKey(
        CatalogPreferences,
        on_delete=models.CASCADE,
    )
    category = models.CharField(max_length=255, blank=True, null=True)


class SupportPreferences(models.Model):
    """Modelo de preferencias de soporte"""

    company = models.OneToOneField(CompanyData, on_delete=models.CASCADE)
    support_hours_start_time = models.TimeField(blank=True, null=True)
    support_hours_end_time = models.TimeField(blank=True, null=True)
    timezone = models.CharField(max_length=100, blank=True, null=True)


class TroubleshootingPriority(models.Model):
    """Modelo de prioridad de resolución de problemas"""

    support_preferences = models.ForeignKey(
        SupportPreferences,
        on_delete=models.CASCADE,
    )
    topic = models.CharField(max_length=255, blank=True, null=True)


class IntegrationSettings(models.Model):
    """Modelo de configuración de integración"""

    company = models.OneToOneField(CompanyData, on_delete=models.CASCADE)
    crm_integration = models.CharField(max_length=255, blank=True, null=True)
    erp_integration = models.CharField(max_length=255, blank=True, null=True)
    data_transfer_protocol = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.crm_integration


class AnalyticsPreferences(models.Model):
    """Modelo de preferencias de análisis"""

    company = models.OneToOneField(CompanyData, on_delete=models.CASCADE)
    analytics_frequency = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.analytics_frequency


class MetricsOfInterest(models.Model):
    """Modelo de métricas de interés"""

    analytics_preferences = models.ForeignKey(
        AnalyticsPreferences,
        on_delete=models.CASCADE,
    )
    metric = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.metric


#### Coleccion Productos
class ClientData(models.Model):
    """Modelo de cliente"""

    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    cell_phone = models.CharField(max_length=40, blank=True, null=True)
    # Other fields as needed
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)


class Tag(models.Model):
    """Modelo de etiqueta"""

    name = models.CharField(max_length=50)


class ProductImage(models.Model):
    """Modelo de imagen de producto"""

    image_url = models.URLField(max_length=500)


class ProductData(models.Model):
    company = models.ForeignKey(
        CompanyData,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    client = models.ForeignKey(ClientData, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    price_currency = models.CharField(max_length=10, blank=True, null=True)
    SKU = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    images = models.ManyToManyField(ProductImage, blank=True)
    technical_specifications = models.TextField(blank=True, null=True)
    warranty_information = models.TextField(blank=True, null=True)
    usage_instructions = models.TextField(blank=True, null=True)
    troubleshooting_guides = models.TextField(blank=True, null=True)
    safety_information = models.TextField(blank=True, null=True)
    related_products = models.ManyToManyField("self", symmetrical=False, blank=True)
    product_manual_url = models.URLField(max_length=500, blank=True, null=True)
    promotional_info = models.TextField(blank=True, null=True)
    average_rating = models.FloatField(blank=True, null=True)
    review_count = models.IntegerField(blank=True, null=True)
    sample_reviews = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
