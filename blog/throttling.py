from rest_framework.throttling import UserRateThrottle


class SubscriptionUserRateThrottle(UserRateThrottle):
    rate = "100/hour"
