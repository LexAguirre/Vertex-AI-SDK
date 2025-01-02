import factory
from faker import Faker

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
from .models import MetricsOfInterest
from .models import ProductCategory
from .models import ProductData
from .models import ProductImage
from .models import SupportPreferences
from .models import Tag
from .models import TroubleshootingPriority

fake = Faker("es_MX")


class CompanyDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CompanyData

    client_id = factory.Sequence(lambda n: f"cliente_{n}")
    name = factory.Faker("company", locale="es_MX")
    created_at = factory.Faker("date_time", locale="es_MX")
    updated_at = factory.Faker("date_time", locale="es_MX")


class BrandDetailsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BrandDetails

    logo_url = factory.Faker("url", locale="es_MX")
    font_family = factory.Faker("word", locale="es_MX")
    tone_of_voice = factory.Faker("sentence", locale="es_MX")


class BrandColorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BrandColor

    brand_details = factory.SubFactory(BrandDetailsFactory)
    color = factory.Faker("color_name", locale="es_MX")


class ContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contact

    is_primary = factory.Faker("boolean", locale="es_MX")
    name = factory.Faker("name", locale="es_MX")
    position = factory.Faker("job", locale="es_MX")
    email = factory.Faker("email", locale="es_MX")
    phone_number = factory.Faker("phone_number", locale="es_MX")


class AccountSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AccountSettings

    company = factory.SubFactory(CompanyDataFactory)
    account_status = factory.Faker("word", locale="es_MX")
    subscription_tier = factory.Faker("word", locale="es_MX")
    start_date = factory.Faker("date", locale="es_MX")
    renewal_date = factory.Faker("date", locale="es_MX")


class CustomFeatureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomFeature

    account_settings = factory.SubFactory(AccountSettingsFactory)
    feature = factory.Faker("word", locale="es_MX")


class CatalogPreferencesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CatalogPreferences

    company = factory.SubFactory(CompanyDataFactory)
    default_currency = factory.Faker("currency_code", locale="es_MX")
    catalog_size = factory.Faker("random_int", locale="es_MX")
    product_update_frequency = factory.Faker("word", locale="es_MX")


class ProductCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductCategory

    catalog_preferences = factory.SubFactory(CatalogPreferencesFactory)
    category = factory.Faker("word", locale="es_MX")


class SupportPreferencesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SupportPreferences

    company = factory.SubFactory(CompanyDataFactory)
    support_hours_start_time = factory.Faker("time", locale="es_MX")
    support_hours_end_time = factory.Faker("time", locale="es_MX")
    timezone = factory.Faker("timezone", locale="es_MX")


class TroubleshootingPriorityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TroubleshootingPriority

    support_preferences = factory.SubFactory(SupportPreferencesFactory)
    topic = factory.Faker("word", locale="es_MX")


class IntegrationSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IntegrationSettings

    company = factory.SubFactory(CompanyDataFactory)
    crm_integration = factory.Faker("word", locale="es_MX")
    erp_integration = factory.Faker("word", locale="es_MX")
    data_transfer_protocol = factory.Faker("word", locale="es_MX")


class AnalyticsPreferencesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AnalyticsPreferences

    company = factory.SubFactory(CompanyDataFactory)
    analytics_frequency = factory.Faker("word", locale="es_MX")


class MetricsOfInterestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MetricsOfInterest

    analytics_preferences = factory.SubFactory(AnalyticsPreferencesFactory)
    metric = factory.Faker("word", locale="es_MX")


class ClientDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClientData

    first_name = factory.Faker("first_name", locale="es_MX")
    last_name = factory.Faker("last_name", locale="es_MX")
    cell_phone = factory.Faker("phone_number", locale="es_MX")
    created_at = factory.Faker("date_time", locale="es_MX")
    updated_at = factory.Faker("date_time", locale="es_MX")


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Faker("word", locale="es_MX")


class ProductImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductImage

    image_url = factory.Faker("url", locale="es_MX")


class ProductDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductData

    client = factory.SubFactory(ClientDataFactory)
    company = factory.SubFactory(CompanyDataFactory)
    name = factory.Faker("word", locale="es_MX")
    description = factory.Faker("text", locale="es_MX")
    price = factory.Faker(
        "pydecimal",
        left_digits=10,
        right_digits=2,
        positive=True,
        locale="es_MX",
    )
    price_currency = factory.Faker("currency_code", locale="es_MX")
    SKU = factory.Faker("ean13", locale="es_MX")
    category = factory.Faker("word", locale="es_MX")
    technical_specifications = factory.Faker("paragraph", locale="es_MX")
    warranty_information = factory.Faker("paragraph", locale="es_MX")
    usage_instructions = factory.Faker("paragraph", locale="es_MX")
    troubleshooting_guides = factory.Faker("text", locale="es_MX")
    safety_information = factory.Faker("text", locale="es_MX")
    product_manual_url = factory.Faker("url", locale="es_MX")
    promotional_info = factory.Faker("text", locale="es_MX")
    average_rating = factory.Faker(
        "pyfloat",
        positive=True,
        max_value=5,
        locale="es_MX",
    )
    review_count = factory.Faker("random_int", min=0, max=1000, locale="es_MX")
    sample_reviews = factory.Faker("text", locale="es_MX")
    created_at = factory.Faker("date_time", locale="es_MX")
    updated_at = factory.Faker("date_time", locale="es_MX")

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of tags were passed in, use them
            for tag in extracted:
                self.tags.add(tag)
        else:
            # Create at least three tags
            for _ in range(3):
                self.tags.add(TagFactory())

    @factory.post_generation
    def images(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for image in extracted:
                self.images.add(image)
        else:
            for _ in range(3):
                self.images.add(ProductImageFactory())


def create_company_with_related_data():
    company = CompanyDataFactory()
    brand_details = BrandDetailsFactory(company=company)
    BrandColorFactory(brand_details=brand_details)
    ContactFactory(company=company)
    account_settings = AccountSettingsFactory(company=company)
    CustomFeatureFactory(account_settings=account_settings)
    catalog_preferences = CatalogPreferencesFactory(company=company)
    ProductCategoryFactory(catalog_preferences=catalog_preferences)
    support_preferences = SupportPreferencesFactory(company=company)
    TroubleshootingPriorityFactory(support_preferences=support_preferences)
    IntegrationSettingsFactory(company=company)
    analytics_preferences = AnalyticsPreferencesFactory(company=company)
    MetricsOfInterestFactory(analytics_preferences=analytics_preferences)
    return company


def create_product_data(company):
    client = ClientDataFactory()
    product = ProductDataFactory(client=client, company=company)
    TagFactory()
    ProductImageFactory()
    return product


def clean_all_models():
    """Remove all instances of all models"""
    CompanyData.objects.all().delete()
    BrandDetails.objects.all().delete()
    BrandColor.objects.all().delete()
    Contact.objects.all().delete()
    AccountSettings.objects.all().delete()
    CustomFeature.objects.all().delete()
    CatalogPreferences.objects.all().delete()
    ProductCategory.objects.all().delete()
    SupportPreferences.objects.all().delete()
    TroubleshootingPriority.objects.all().delete()
    IntegrationSettings.objects.all().delete()
    AnalyticsPreferences.objects.all().delete()
    MetricsOfInterest.objects.all().delete()
    ClientData.objects.all().delete()
    ProductData.objects.all().delete()
    Tag.objects.all().delete()
    ProductImage.objects.all().delete()
    return True
