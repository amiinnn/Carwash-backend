from django.core.management.base import BaseCommand
from registers.models import Product,ProductOrderItem, Color, Size

class Command(BaseCommand):
    help = 'Update ProductOrderItem objects to set default color, size, and product'

    def handle(self, *args, **kwargs):
        default_color = Color.objects.first()
        default_size = Size.objects.first()
        default_product = Product.objects.first()

        if not default_color or not default_size or not default_product:
            self.stdout.write(self.style.ERROR('Default color, size, or product not found. Please add them to the database.'))
            return

        items_updated = 0
        for item in ProductOrderItem.objects.all():
            updated = False
            if item.color_id is None:
                item.color = default_color
                updated = True
            if item.size_id is None:
                item.size = default_size
                updated = True
            if item.product_id is None:
                item.product = default_product
                updated = True
            if updated:
                item.save()
                items_updated += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {items_updated} items.'))