import traceback

from django.db import connection
from django.http import JsonResponse
from django.core.cache import cache

from rest_framework import status

from general.utils import generate_trace_id
from apps.logs.models import ErrorLog


class JSONMiddleware:
    """
    Process application/json requests data from GET and POST requests.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        response = self.get_response(request)
        return response

    def process_request(self, request):
        import json

        if (
            "CONTENT_TYPE" in request.META
            and "application/json" in request.META["CONTENT_TYPE"]
        ):
            body_unicode = request.body.decode("utf-8")
            try:
                data = json.loads(body_unicode)
            except:
                data = body_unicode

            if request.method == "POST":
                request.POST = data

        return None


class CustomExceptionHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as exception:
            return self.process_exception(request, exception)

    def process_exception(self, request, exception):
        log = ErrorLog.objects.create(
            place=request.path,
            data=f"{request}\n{request.user.username}\n{request.body.decode('utf-8')}",
            error=traceback.format_exc(),
            trace_id=str(generate_trace_id()),
        )
        return JsonResponse(
            {
                "detail": "Internal server error.",
                "traceId": log.trace_id,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class HealthCheckMiddleware:
    """
    This middleware checks the health status of the server (Readiness Probe)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/health/live/":
            return JsonResponse({"status": "alive"}, status=200)

        if request.path == "/health/ready/":
            try:
                connection.ensure_connection()
                cache.set("healthcheck_redis", "ok", timeout=5)
                if cache.get("healthcheck_redis") != "ok":
                    raise Exception("Redis error")
                return JsonResponse({"status": "ready"}, status=200)
            except Exception as e:
                return JsonResponse({"status": "unready", "error": str(e)}, status=503)

        return self.get_response(request)
