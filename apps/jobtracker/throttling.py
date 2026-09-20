from apps.base.throttling import CFUserRateThrottle


class BoardAPIRateThrottle(CFUserRateThrottle):
    scope = "board"
    rate = "120/min"


class ApplicationAPIRateThrottle(CFUserRateThrottle):
    scope = "application"
    rate = "120/min"