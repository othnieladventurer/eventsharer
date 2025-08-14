# subscriptions/decorators.py
from django.shortcuts import redirect
from .models import UserSubscription, SubscriptionSession
from users.models import Trial








def subscription_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('users:custom_login')  # Custom login

        # 1️⃣ Allow if trial is active
        try:
            if hasattr(user, 'trial') and user.trial.is_active:
                return view_func(request, *args, **kwargs)
        except Trial.DoesNotExist:
            pass  # No trial record, check subscription

        # 2️⃣ Allow if subscription is active
        try:
            subscription = user.usersubscription
            session = user.subscription_session
            if subscription.active and session.active:
                return view_func(request, *args, **kwargs)
        except (UserSubscription.DoesNotExist, SubscriptionSession.DoesNotExist):
            pass  # No subscription/session

        # 3️⃣ Otherwise, redirect to plans page
        return redirect('eventadm:plan_list')

    return _wrapped_view






