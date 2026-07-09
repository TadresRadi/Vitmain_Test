from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
from ..models.payment_order import PaymentOrder
from ..serializers.payment_order_serializer import PaymentOrderSerializer
import random
import re


class CreatePaymentOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):

        expected_sender_number = request.data.get('expected_sender_number')
        plan = request.data.get('plan', 'basic')

        if not expected_sender_number:
            return Response(
                {'error': 'expected_sender_number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate Egyptian mobile number
        clean_number = re.sub(r'\s+', '', expected_sender_number)

        if not re.match(r'^(010|011|012|015)\d{8}$', clean_number):
            return Response(
                {'error': 'Invalid Egyptian mobile number.'},
                status=status.HTTP_400_BAD_REQUEST
            )


        # Determine amount
        if plan == 'basic':
            expected_amount = 5.00  # Testing only
        else:
            expected_amount = getattr(
                settings,
                'VODAFONE_TESTING_PRICE',
                5.00
            )


        receiver_number = getattr(
            settings,
            'VODAFONE_RECEIVER_NUMBER',
            '01094064044'
        )


        # Check if user already has an unfinished payment
        existing_order = PaymentOrder.objects.filter(
            user=request.user,
            plan=plan,
            status__in=[
                PaymentOrder.Status.PENDING,
                PaymentOrder.Status.PARTIAL
            ]
        ).first()


        if existing_order:

            serializer = PaymentOrderSerializer(existing_order)

            response_data = serializer.data

            remaining_amount = (
                existing_order.expected_amount -
                existing_order.received_amount
            )

            response_data['receiver_number'] = receiver_number

            response_data['amount'] = float(
                remaining_amount
            )

            response_data['remaining_amount'] = float(
                remaining_amount
            )

            response_data['payment_instructions'] = (
                f"Send exactly {remaining_amount} EGP "
                f"to {receiver_number}."
            )

            return Response(
                response_data,
                status=status.HTTP_200_OK
            )


        # Generate unique reference code
        while True:

            ref_code = f"VFC{random.randint(100,999)}"

            if not PaymentOrder.objects.filter(
                reference_code=ref_code
            ).exists():
                break


        # Create new payment order
        payment_order = PaymentOrder.objects.create(
            user=request.user,
            plan=plan,
            expected_amount=expected_amount,
            expected_sender_number=clean_number,
            reference_code=ref_code
        )


        serializer = PaymentOrderSerializer(payment_order)

        response_data = serializer.data

        response_data['receiver_number'] = receiver_number

        response_data['amount'] = float(
            expected_amount
        )

        response_data['payment_instructions'] = (
            f"Send exactly {expected_amount} EGP "
            f"to {receiver_number}."
        )


        return Response(
            response_data,
            status=status.HTTP_201_CREATED
        )