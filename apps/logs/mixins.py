from itertools import chain

from django.contrib.contenttypes.models import ContentType

from apps.logs.models import ActivityLog, RequestLog


class LoggingMethodMixin:
    """
    Adds methods that log changes made to users' data.
    To use this, subclass it and ModelViewSet, and override _get_logging_user(). Ensure
    that the viewset you're mixing this into has `self.model` and `self.serializer_class`
    attributes.
    """

    ADDITION = 1
    CHANGE = 2
    DELETION = 3

    def _get_logging_user(self):
        """Return the user of this logged item. Needs overriding in any subclass."""
        raise NotImplementedError

    def extra_data(self, data):
        """Hook to append more data."""
        return {}

    def log(self, operation, instance, change_message=""):
        ActivityLog.objects.create(
            user_id=self.request.user.id,
            content_type_id=ContentType.objects.get_for_model(instance).pk,
            object_id=instance.pk,
            object_repr=str(instance),
            action_flag=operation,
            change_message=change_message,
        )

    def _log_on_create(self, serializer):
        """Log the up-to-date serializer.data."""
        self.log(operation=self.ADDITION, instance=serializer.instance)

    def _log_on_update(self, instance, change_message):
        """Log data from the updated serializer instance."""
        self.log(
            operation=self.CHANGE,
            instance=instance,
            change_message=change_message,
        )

    def _log_on_destroy(self, instance):
        """Log data from the instance before it gets deleted."""
        self.log(operation=self.DELETION, instance=instance)

    def _generate_log_text_from_old_obj(self, old_obj, obj):
        text = "{"
        for key in obj.keys():
            if key == "modified_at":
                continue
            try:
                attr = old_obj.get(key)
                new_attr = obj.get(key)
                if attr != new_attr:
                    text += (
                        str(key)
                        + ": { old: "
                        + str(attr)
                        + " , new: "
                        + str(new_attr)
                        + "}, "
                    )
            except Exception:
                pass
        text += "}"
        return text

    def _to_dict(self, instance):
        opts = instance._meta
        data = {}
        for f in chain(opts.concrete_fields, opts.private_fields):
            data[f.name] = f.value_from_object(instance)
        for f in opts.many_to_many:
            data[f.name] = [i.id for i in f.value_from_object(instance)]
        return data


class LoggingViewSetMixin(LoggingMethodMixin):
    """
    A viewset that logs changes made to users' data.
    To use this, subclass it and ModelViewSet, and override _get_logging_user(). Ensure
    that the viewset you're mixing this into has `self.model` and `self.serializer_class`
    attributes.
    If you modify any of the following methods, be sure to call super() or the
    corresponding _log_on_X method:
    - perform_create
    - perform_update
    - perform_destroy
    """

    def perform_create(self, serializer):
        """Create an object and log its data."""
        super().perform_create(serializer)
        self._log_on_create(serializer)

    def perform_update(self, serializer):
        old_obj = self._to_dict(serializer.instance)
        """Update the instance and log the updated data."""
        super().perform_update(serializer)
        instance = serializer.instance
        new_obj = self._to_dict(instance)
        change_message = self._generate_log_text_from_old_obj(old_obj, new_obj)
        self._log_on_update(instance, change_message)

    def perform_destroy(self, instance):
        """Delete the instance and log the deletion."""
        instance.soft_delete()
        self._log_on_destroy(instance)


class RequestLoggingMixin:
    """
    Mixin to log request metadata (method, path, IP, user agent, data).
    """

    def log(self, request, *args, **kwargs):
        RequestLog.log(request)


class RequestLoggingViewSetMixin(RequestLoggingMixin):
    """
    A viewset that logs request metadata (method, path, IP, user agent, data).
    RequestLoggingViewSetMixin must be used before LoggingViewSetMixin.
    """

    def initial(self, request, *args, **kwargs):
        self.log(request)
        return super().initial(request, *args, **kwargs)
