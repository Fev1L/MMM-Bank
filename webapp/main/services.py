from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction

from .models import Category, Transaction

def make_transfer(sender, recipient, amount):
    sender_account = sender.account
    recipient_account = recipient.account

    if recipient == sender:
        raise ValidationError("You cannot send money to yourself")

    if sender_account.balance < amount:
        raise ValidationError("Not enough balance")

    transfer_category, _ = Category.objects.get_or_create(
        name="Transfer",
        type=Category.WITHDRAW
    )

    deposit_category, _ = Category.objects.get_or_create(
        name="Deposit",
        type=Category.DEPOSIT
    )

    with db_transaction.atomic():
        Transaction.objects.create(
            account=sender_account,
            amount=amount,
            category=transfer_category,
            title=f"Transfer to {recipient.username}"
        )

        Transaction.objects.create(
            account=recipient_account,
            amount=amount,
            category=deposit_category,
            title=f"Transfer from {sender.username}"
        )