from django.core.management.base import BaseCommand
from registers.models import ProductOrder, UserProfile

class Command(BaseCommand):
    help = 'Update ProductOrder objects to set default user if none exists'

    def handle(self, *args, **kwargs):
        default_user = UserProfile.objects.first()

        if not default_user:
            self.stdout.write(self.style.ERROR('Default user not found. Please add a UserProfile to the database.'))
            return

        orders_updated = 0
        for order in ProductOrder.objects.all():
            if order.user is None:
                order.user = default_user
                order.save()
                orders_updated += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {orders_updated} orders.'))
