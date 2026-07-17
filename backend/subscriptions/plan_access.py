from subscriptions.models import Subscription

CHAT_PLAN_SLUG = "basic"
SUPPORT_PLAN_SLUG = "pro"


def get_user_plan_slug(user):
    try:
        sub = Subscription.objects.select_related("plan").get(user=user)
        if sub.active and sub.plan:
            return sub.plan.slug
    except Subscription.DoesNotExist:
        pass
    return None
