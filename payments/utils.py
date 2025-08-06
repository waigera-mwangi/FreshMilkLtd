import uuid
from decimal import Decimal
from deliveries.models import MilkCollection
from payments.models import Payment, MilkPrice

def calculate_and_create_payment(farmer, start_date, end_date):
    # Fetch unpaid milk collections for the farmer
    milk_collections = MilkCollection.objects.filter(
        farmer=farmer,
        collection_date__range=(start_date, end_date),
        is_paid=False
    )

    if not milk_collections.exists():
        return None  # No unpaid deliveries

    # Get active milk price
    active_price = MilkPrice.objects.filter(is_active=True).order_by('-effective_date').first()
    if not active_price:
        raise ValueError("No active milk price set.")

    # Calculate total liters
    total_liters = milk_collections.aggregate(total=models.Sum('quantity_liters'))['total'] or Decimal('0.00')
    amount = total_liters * active_price.price_per_liter

    # Create payment
    payment = Payment.objects.create(
        farmer=farmer,
        start_date=start_date,
        end_date=end_date,
        amount=amount,
        reference=str(uuid.uuid4())
    )
    payment.milk_collections.set(milk_collections)

    # Mark collections as paid
    milk_collections.update(is_paid=True)

    return payment
