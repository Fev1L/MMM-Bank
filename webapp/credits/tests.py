from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from credits.models import Credit
from credits.views import index
from main.models import Transaction


class CreditsFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alex", password="testpass123")
        self.user.account.balance = Decimal("5000.00")
        self.user.account.save()
        self.client.login(username="alex", password="testpass123")
        self.factory = RequestFactory()

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

    def test_available_loan_creates_credit_and_deposits_money(self):
        response = self.client.post(
            reverse("avaible_loans"),
            {"loan_type": "motorcycle"},
        )

        self.user.account.refresh_from_db()
        loan = Credit.objects.get(user=self.user, client_name="Motorcycle loan")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("avaible_loans"))
        self.assertEqual(loan.amount, Decimal("3000.00"))
        self.assertEqual(loan.interest_rate, 4.5)
        self.assertTrue(loan.is_active)
        self.assertEqual(self.user.account.balance, Decimal("8000.00"))
        self.assertTrue(
            Transaction.objects.filter(
                account=self.user.account,
                title="Loan approved: Motorcycle loan",
                amount=Decimal("3000.00"),
            ).exists()
        )

    def test_credits_page_shows_real_loan_activity(self):
        self.client.post(reverse("avaible_loans"), {"loan_type": "motorcycle"})
        loan = Credit.objects.get(user=self.user, client_name="Motorcycle loan")
        self.client.post(reverse("pay_extra"), {"loan": loan.id, "amount": "250.00"})

        request = self.factory.get(reverse("credits"))
        request.user = self.user

        with patch("credits.views.render") as mocked_render:
            mocked_render.return_value = HttpResponse("ok")
            index(request)

        context = mocked_render.call_args[0][2]
        activity_titles = [item.title for item in context["loan_activity"]]
        activity_categories = [item.category.name for item in context["loan_activity"]]

        self.assertIn("Loan approved: Motorcycle loan", activity_titles)
        self.assertIn("Extra payment for Motorcycle loan", activity_titles)
        self.assertIn("Loan payout", activity_categories)
        self.assertIn("Loan payment", activity_categories)

    def test_credits_page_limits_activity_until_more_is_enabled(self):
        for loan_type in ["bicycle", "motorcycle", "car", "apartment"]:
            self.client.post(reverse("avaible_loans"), {"loan_type": loan_type})
        self.client.post(reverse("mortgage"), {"amount": "20000.00", "years": "15"})

        loan = Credit.objects.get(user=self.user, client_name="Motorcycle loan")
        self.client.post(reverse("pay_extra"), {"loan": loan.id, "amount": "100.00"})

        request = self.factory.get(reverse("credits"))
        request.user = self.user

        with patch("credits.views.render") as mocked_render:
            mocked_render.return_value = HttpResponse("ok")
            index(request)

        default_context = mocked_render.call_args[0][2]
        self.assertFalse(default_context["show_all_activity"])
        self.assertEqual(len(default_context["loan_activity"]), 4)

        request_all = self.factory.get(f"{reverse('credits')}?activity=all")
        request_all.user = self.user

        with patch("credits.views.render") as mocked_render_all:
            mocked_render_all.return_value = HttpResponse("ok")
            index(request_all)

        full_context = mocked_render_all.call_args[0][2]
        self.assertTrue(full_context["show_all_activity"])
        self.assertEqual(len(full_context["loan_activity"]), 6)

    def test_credits_page_shows_active_credit_cards_from_database(self):
        self.client.post(reverse("avaible_loans"), {"loan_type": "car"})
        self.client.post(reverse("avaible_loans"), {"loan_type": "bicycle"})

        request = self.factory.get(reverse("credits"))
        request.user = self.user

        with patch("credits.views.render") as mocked_render:
            mocked_render.return_value = HttpResponse("ok")
            index(request)

        context = mocked_render.call_args[0][2]
        card_titles = [item["title"] for item in context["active_credit_cards"]]

        self.assertEqual(len(context["active_credit_cards"]), 2)
        self.assertIn("Car loan", card_titles)
        self.assertIn("Bicycle loan", card_titles)

    def test_credits_page_shows_two_placeholders_without_active_loans(self):
        request = self.factory.get(reverse("credits"))
        request.user = self.user

        with patch("credits.views.render") as mocked_render:
            mocked_render.return_value = HttpResponse("ok")
            index(request)

        context = mocked_render.call_args[0][2]

        self.assertEqual(len(context["active_credit_cards"]), 2)
        self.assertTrue(all(item["is_placeholder"] for item in context["active_credit_cards"]))
        self.assertFalse(context["has_more_credit_cards"])

    def test_credit_cards_show_more_reveals_all_active_loans(self):
        for loan_type in ["bicycle", "motorcycle", "car"]:
            self.client.post(reverse("avaible_loans"), {"loan_type": loan_type})

        request = self.factory.get(reverse("credits"))
        request.user = self.user

        with patch("credits.views.render") as mocked_render:
            mocked_render.return_value = HttpResponse("ok")
            index(request)

        default_context = mocked_render.call_args[0][2]
        self.assertEqual(len(default_context["active_credit_cards"]), 2)
        self.assertTrue(default_context["has_more_credit_cards"])
        self.assertFalse(default_context["show_all_cards"])

        request_all = self.factory.get(f"{reverse('credits')}?cards=all")
        request_all.user = self.user

        with patch("credits.views.render") as mocked_render_all:
            mocked_render_all.return_value = HttpResponse("ok")
            index(request_all)

        full_context = mocked_render_all.call_args[0][2]
        self.assertEqual(len(full_context["active_credit_cards"]), 3)
        self.assertTrue(full_context["show_all_cards"])

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
