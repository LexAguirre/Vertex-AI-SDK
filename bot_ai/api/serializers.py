from rest_framework import serializers

from app.bot_ai.models import AccountSettings
from app.bot_ai.models import AnalyticsPreferences
from app.bot_ai.models import BrandColor
from app.bot_ai.models import BrandDetails
from app.bot_ai.models import CatalogPreferences
from app.bot_ai.models import ClientData
from app.bot_ai.models import CompanyData
from app.bot_ai.models import Contact
from app.bot_ai.models import CustomFeature
from app.bot_ai.models import IntegrationSettings
from app.bot_ai.models import MetricsOfInterest
from app.bot_ai.models import ProductCategory
from app.bot_ai.models import ProductData
from app.bot_ai.models import ProductImage
from app.bot_ai.models import SupportPreferences
from app.bot_ai.models import Tag
from app.bot_ai.models import TroubleshootingPriority


class BrandColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandColor
        fields = ["color"]


class BrandDetailsSerializer(serializers.ModelSerializer):
    brand_colors = BrandColorSerializer(many=True, source="brandcolor_set")

    class Meta:
        model = BrandDetails
        fields = ["brand_colors", "logo_url", "font_family", "tone_of_voice"]


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ["name", "position", "email", "phone_number"]


class ContactInformationSerializer(serializers.Serializer):
    primary_contact = serializers.SerializerMethodField()
    secondary_contact = serializers.SerializerMethodField()

    def get_primary_contact(self, obj):
        primary_contact = obj.filter(is_primary=True).first()
        if primary_contact:
            return ContactSerializer(primary_contact).data
        return None

    def get_secondary_contact(self, obj):
        secondary_contact = obj.filter(is_primary=False).first()
        if secondary_contact:
            return ContactSerializer(secondary_contact).data
        return None


class CustomFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomFeature
        fields = ["feature"]


class AccountSettingsSerializer(serializers.ModelSerializer):
    custom_features = CustomFeatureSerializer(many=True, source="customfeature_set")

    class Meta:
        model = AccountSettings
        fields = [
            "account_status",
            "subscription_tier",
            "start_date",
            "renewal_date",
            "custom_features",
        ]


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["category"]


class CatalogPreferencesSerializer(serializers.ModelSerializer):
    product_categories = ProductCategorySerializer(
        many=True,
        source="productcategory_set",
    )

    class Meta:
        model = CatalogPreferences
        fields = [
            "default_currency",
            "catalog_size",
            "product_update_frequency",
            "product_categories",
        ]


class TroubleshootingPrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = TroubleshootingPriority
        fields = ["topic"]


class SupportPreferencesSerializer(serializers.ModelSerializer):
    support_hours = serializers.SerializerMethodField()
    troubleshooting_priority = TroubleshootingPrioritySerializer(
        many=True,
        source="troubleshootingpriority_set",
    )

    class Meta:
        model = SupportPreferences
        fields = [
            "support_hours",
            "timezone",
            "troubleshooting_priority",
        ]

    def get_support_hours(self, obj):
        return {
            "start_time": obj.support_hours_start_time,
            "end_time": obj.support_hours_end_time,
        }


class IntegrationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationSettings
        fields = ["crm_integration", "erp_integration", "data_transfer_protocol"]


class MetricsOfInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricsOfInterest
        fields = ["metric"]


class AnalyticsPreferencesSerializer(serializers.ModelSerializer):
    metrics_of_interest = MetricsOfInterestSerializer(
        many=True,
        source="metricsofinterest_set",
    )

    class Meta:
        model = AnalyticsPreferences
        fields = ["analytics_frequency", "metrics_of_interest"]


class CompanyDataSerializer(serializers.ModelSerializer):
    brand_details = BrandDetailsSerializer(
        source="branddetails_set",
        many=True,
        read_only=True,
    )
    contact_information = serializers.SerializerMethodField()
    account_settings = AccountSettingsSerializer(
        source="accountsettings_set",
        many=True,
        read_only=True,
    )
    catalog_preferences = CatalogPreferencesSerializer(
        source="catalogpreferences_set",
        many=True,
        read_only=True,
    )
    support_preferences = SupportPreferencesSerializer(
        source="supportpreferences_set",
        many=True,
        read_only=True,
    )
    integration_settings = IntegrationSettingsSerializer(
        source="integrationsettings_set",
        many=True,
        read_only=True,
    )
    analytics_preferences = AnalyticsPreferencesSerializer(
        source="analyticspreferences_set",
        many=True,
        read_only=True,
    )

    class Meta:
        model = CompanyData
        fields = [
            "client_id",
            "name",
            "brand_details",
            "contact_information",
            "account_settings",
            "catalog_preferences",
            "support_preferences",
            "integration_settings",
            "analytics_preferences",
            "created_at",
            "updated_at",
        ]

    def get_contact_information(self, obj):
        contacts = obj.contact_set.all()
        serializer = ContactInformationSerializer(contacts)
        return serializer.data


class ClientDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientData
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"


class ProductDataSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    related_products = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = ProductData
        fields = "__all__"
