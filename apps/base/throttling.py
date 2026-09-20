from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from general.utils import get_cf_ident


class CFUserRateThrottle(UserRateThrottle):
    def get_ident(self, request):
        return get_cf_ident(request)


class CFAnonRateThrottle(AnonRateThrottle):
    def get_ident(self, request):
        return get_cf_ident(request)
