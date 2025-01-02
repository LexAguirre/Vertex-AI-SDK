from django.contrib import admin

from .models import AccountSettings
from .models import AnalyticsPreferences
from .models import BrandColor
from .models import BrandDetails
from .models import CatalogPreferences
from .models import ClientData
from .models import CompanyData
from .models import Contact
from .models import CustomFeature
from .models import IntegrationSettings
from .models import MediasForIATrainig
from .models import MensajeAiModel
from .models import MetricsOfInterest
from .models import ProductCategory
from .models import ProductData
from .models import ProductImage
from .models import SupportPreferences
from .models import Tag
from .models import TroubleshootingPriority


@admin.register(MensajeAiModel)
class MensajeAiModelAdmin(admin.ModelAdmin):
    list_display = ("id", "mensaje", "respuesta")


@admin.register(MediasForIATrainig)
class MediasForIATrainigAdmin(admin.ModelAdmin):
    list_display = ("id", "company", "media", "created_at")
    search_fields = ("company",)
    list_filter = ("company",)


@admin.register(CompanyData)
class CompanyDataAdmin(admin.ModelAdmin):
    list_display = ("client_id", "name", "created_at", "updated_at")
    search_fields = ("client_id", "name")


@admin.register(BrandDetails)
class BrandDetailsAdmin(admin.ModelAdmin):
    list_display = ("company", "logo_url", "font_family", "tone_of_voice")
    search_fields = ("company__name",)


@admin.register(BrandColor)
class BrandColorAdmin(admin.ModelAdmin):
    list_display = ("brand_details", "color")
    search_fields = ("brand_details__company__name",)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "is_primary",
        "name",
        "position",
        "email",
        "phone_number",
    )
    search_fields = ("company__name", "name", "email")


@admin.register(AccountSettings)
class AccountSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "account_status",
        "subscription_tier",
        "start_date",
        "renewal_date",
    )
    search_fields = ("company__name", "account_status", "subscription_tier")


@admin.register(CustomFeature)
class CustomFeatureAdmin(admin.ModelAdmin):
    list_display = ("account_settings", "feature")
    search_fields = ("account_settings__company__name", "feature")


@admin.register(CatalogPreferences)
class CatalogPreferencesAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "default_currency",
        "catalog_size",
        "product_update_frequency",
    )
    search_fields = ("company__name",)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("catalog_preferences", "category")
    search_fields = ("catalog_preferences__company__name", "category")


@admin.register(SupportPreferences)
class SupportPreferencesAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "support_hours_start_time",
        "support_hours_end_time",
        "timezone",
    )
    search_fields = ("company__name", "timezone")


@admin.register(TroubleshootingPriority)
class TroubleshootingPriorityAdmin(admin.ModelAdmin):
    list_display = ("support_preferences", "topic")
    search_fields = ("support_preferences__company__name", "topic")


@admin.register(IntegrationSettings)
class IntegrationSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "crm_integration",
        "erp_integration",
        "data_transfer_protocol",
    )
    search_fields = ("company__name", "crm_integration", "erp_integration")


@admin.register(AnalyticsPreferences)
class AnalyticsPreferencesAdmin(admin.ModelAdmin):
    list_display = ("company", "analytics_frequency")
    search_fields = ("company__name", "analytics_frequency")


@admin.register(MetricsOfInterest)
class MetricsOfInterestAdmin(admin.ModelAdmin):
    list_display = ("analytics_preferences", "metric")
    search_fields = ("analytics_preferences__company__name", "metric")


@admin.register(ClientData)
class ClientDataAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "cell_phone", "created_at", "updated_at")
    search_fields = ("first_name", "last_name", "cell_phone")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("image_url",)
    search_fields = ("image_url",)


@admin.register(ProductData)
class ProductDataAdmin(admin.ModelAdmin):
    list_display = (
        "client",
        "name",
        "price",
        "price_currency",
        "SKU",
        "category",
        "average_rating",
        "review_count",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "client__first_name",
        "client__last_name",
        "name",
        "SKU",
        "category",
    )
