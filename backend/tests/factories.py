"""
Test factories using factory_boy.

These factories create realistic test data with minimal boilerplate.
Each factory generates a valid model instance with sensible defaults
that can be overridden per-test.

Usage:
    from tests.factories import UserFactory, PlanFactory

    user = UserFactory()                          # random email
    admin = UserFactory(role='super_admin')       # override default
    plan = PlanFactory(slug='basic', price=Decimal('200.00'))
"""
from decimal import Decimal

import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

from payments.models import PaymentOrder, PaymentTransaction
from subscriptions.models import Plan, Subscription
from chat.models import AIPostGeneration
from onboarding.models import OnboardingResponse

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Standard user with random unique email."""
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@test.example")
    full_name = factory.Faker("name")
    language = "en"
    is_active = True
    role = "user"

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Set password via set_password so it's properly hashed."""
        raw = extracted or "TestPassword123!"
        obj.set_password(raw)
        if create:
            obj.save()


class AdminUserFactory(UserFactory):
    """Super admin user with is_staff and is_superuser."""
    role = "super_admin"
    is_staff = True
    is_superuser = True


class PlanFactory(DjangoModelFactory):
    """Subscription plan."""
    class Meta:
        model = Plan

    name = factory.Sequence(lambda n: f"Plan {n}")
    slug = factory.Sequence(lambda n: f"plan-{n}")
    price = Decimal("200.00")
    description = "Test plan"
    features = "feature1,feature2"
    max_images = 10


class SubscriptionFactory(DjangoModelFactory):
    """Active subscription for a user."""
    class Meta:
        model = Subscription

    user = factory.SubFactory(UserFactory)
    plan = factory.SubFactory(PlanFactory)
    active = True


class PaymentOrderFactory(DjangoModelFactory):
    """Pending payment order."""
    class Meta:
        model = PaymentOrder

    user = factory.SubFactory(UserFactory)
    plan = "basic"
    expected_amount = Decimal("200.00")
    expected_sender_number = "01012345678"
    reference_code = factory.Sequence(lambda n: f"VFC{n:06d}")
    status = PaymentOrder.Status.PENDING


class PaymentTransactionFactory(DjangoModelFactory):
    """Payment transaction record."""
    class Meta:
        model = PaymentTransaction

    id = factory.Sequence(lambda n: f"VFTX{n}")
    order = factory.SubFactory(PaymentOrderFactory)
    amount = Decimal("200.00")
    sender_number = "01012345678"
    raw_sms = "Test SMS body"


class OnboardingResponseFactory(DjangoModelFactory):
    """Completed onboarding response."""
    class Meta:
        model = OnboardingResponse

    user = factory.SubFactory(UserFactory)
    business_name = "Test Business"
    business_type = "restaurant"
    marketing_goals = ["increase_sales"]
    target_audience = "young adults"
    tone_of_voice = "friendly"
    is_active = True


class AIPostGenerationFactory(DjangoModelFactory):
    """AI post generation with 5 default posts."""
    class Meta:
        model = AIPostGeneration

    user = factory.SubFactory(UserFactory)
    posts = ["Post 1", "Post 2", "Post 3", "Post 4", "Post 5"]
    edit_count = 0
    posts_review_complete = False