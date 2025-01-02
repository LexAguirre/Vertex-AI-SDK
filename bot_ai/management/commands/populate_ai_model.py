from django.core.management.base import BaseCommand

from app.bot_ai.factories import clean_all_models
from app.bot_ai.factories import create_company_with_related_data
from app.bot_ai.factories import create_product_data

PERMITTED_NUMBER_COMPANIES = 100
PERMITTED_NUMBER_PRODUCTS = 100


class Command(BaseCommand):
    help = "Populate the database with dummy data"

    def handle(self, *args, **kwargs):
        # Remove all instances of all models
        if self.ask_yes_no(
            "Are you sure you want to remove all instances of all models? (yes/no): ",
        ):
            # Remove all instances of all models
            self.stdout.write(
                self.style.WARNING("Removing all instances of all models"),
            )
            clean_all_models()
        else:
            self.stdout.write(self.style.ERROR("Operation cancelled."))

        if self.ask_yes_no(
            "Do you want to populate the database with dummy data? (yes/no): ",
        ):
            # Create companys
            number_of_companies = self.ask_number(
                "How many companies do you want to create? ",
            )
            if number_of_companies > PERMITTED_NUMBER_COMPANIES:
                self.stdout.write(
                    self.style.ERROR("You can't create more than 100 companies."),
                )

            # Create products
            number_products = self.ask_number(
                "How many products for company do you want to create? ",
            )
            if number_products > PERMITTED_NUMBER_PRODUCTS:
                self.stdout.write(
                    self.style.ERROR("You can't create more than 100 products."),
                )

            self.stdout.write(
                self.style.WARNING("Populating the database with dummy data"),
            )
            for _ in range(number_of_companies):
                company = create_company_with_related_data()

                for _ in range(number_products):
                    create_product_data(company)

            self.stdout.write(
                self.style.SUCCESS(
                    "Successfully populated the database with dummy data",
                ),
            )
        else:
            self.stdout.write(self.style.ERROR("Operation cancelled."))

    def ask_yes_no(self, question):
        while True:
            response = input(question).strip().lower()
            if response in ["yes", "no"]:
                return response == "yes"
            self.stdout.write(self.style.ERROR("Please respond with 'yes' or 'no'."))

    def ask_number(self, question):
        while True:
            response = input(question).strip()
            if response.isdigit():
                return int(response)
            self.stdout.write(self.style.ERROR("Please enter a valid number."))
