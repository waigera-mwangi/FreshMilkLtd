from datetime import date
from django.db.models import Sum, F
from deliveries.models import MilkCollection
from .models import Payment
from decimal import Decimal
import uuid


def calculate_and_create_payment(farmer, start_date, end_date):
    """
    Calculate total payment for a farmer within a given date range.
    Automatically creates a Payment record.
    """

    # Get all milk collections for the farmer in the date range
    collections = MilkCollection.objects.filter(
        farmer=farmer,
        collection_date__range=(start_date, end_date)
    )

    if not collections.exists():
        return None  # No milk collected in this range

    # Calculate total liters and amount
    total_amount = collections.aggregate(
        total=Sum(F('quantity_liters') * F('price_per_liter'))
    )['total'] or Decimal('0.00')

    # Create unique reference for this payment
    reference = f"PAY-{uuid.uuid4().hex[:8].upper()}"

    # Create payment record
    payment = Payment.objects.create(
        farmer=farmer,
        start_date=start_date,
        end_date=end_date,
        amount=total_amount,
        reference=reference
    )

    return payment
