import logging
from subscriptions.models import Subscription, Plan

logger = logging.getLogger(__name__)

class PaymentService:
    
    @staticmethod
    def activate_subscription(payment_order):
        """
        Activate subscription for the user based on the payment order.
        This is called when a payment is successfully verified and completed.
        """
        user = payment_order.user
        plan_slug = payment_order.plan
        
        try:
            # Get the plan from the database
            plan = Plan.objects.get(slug=plan_slug)
            
            # Create or update the subscription
            subscription, created = Subscription.objects.update_or_create(
                user=user,
                defaults={
                    "plan": plan,
                    "active": True
                }
            )
            
            logger.info(
                f"SUCCESS: Auto-activated {plan.name} (slug: {plan_slug}) "
                f"for user {user.email}. Payment order: {payment_order.reference_code}"
            )
            
            return subscription
            
        except Plan.DoesNotExist:
            logger.error(
                f"ERROR: Plan with slug '{plan_slug}' not found. "
                f"Cannot activate subscription for user {user.email}. "
                f"Payment order: {payment_order.reference_code}"
            )
            raise