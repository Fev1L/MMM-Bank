from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from credits.models import Credit
from main.models import Transaction


class CreditsFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alex", password="testpass123")
        self.user.account.balance = Decimal("5000.00")
        self.user.account.save()
        self.client.login(username="alex", password="testpass123")

    def test_pay_extra_reduces_credit_balance_and_account_balance(self):
        credit = Credit.objects.create(
            user=self.user,
            client_name="Car loan",
            amount=Decimal("1000.00"),
            interest_rate=3,
            is_active=True,
        )

        response = self.client.post(
            reverse("pay_extra"),
            {"loan": credit.id, "amount": "250.00"},
        )

        credit.refresh_from_db()
        self.user.account.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("pay_extra"))
        self.assertEqual(credit.amount, Decimal("750.00"))
        self.assertTrue(credit.is_active)
        self.assertEqual(self.user.account.balance, Decimal("4750.00"))
        self.assertTrue(
            Transaction.objects.filter(
                account=self.user.account,
                title="Extra payment for Car loan",
                amount=Decimal("250.00"),
            ).exists()
        )

    def test_mortgage_creates_credit_and_deposits_money(self):
        response = self.client.post(
            reverse("mortgage"),
            {"amount": "20000.00", "years": "15"},
        )

        self.user.account.refresh_from_db()
        mortgage = Credit.objects.get(user=self.user, client_name="Mortgage")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("mortgage"))
        self.assertEqual(mortgage.client_name, "Mortgage")
        self.assertEqual(mortgage.amount, Decimal("20000.00"))
        self.assertTrue(mortgage.is_active)
        self.assertEqual(self.user.account.balance, Decimal("25000.00"))
        self.assertTrue(
            Transaction.objects.filter(
                account=self.user.account,
                title="Mortgage approved: Mortgage",
                amount=Decimal("20000.00"),
            ).exists()
        )
