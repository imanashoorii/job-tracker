from apps.base.throttling import CFAnonRateThrottle


class AuthAPIRateThrottle(CFAnonRateThrottle):
    scope = "auth"
    rate = "20/min"
