class BaseMixin:

    serializer_classes_by_action = {}
    permission_classes_by_action = {}
    throttle_classes_by_action = {}

    def get_serializer_class(self):
        serializer_class = self.serializer_classes_by_action.get(self.action)
        if serializer_class is not None:
            return serializer_class
        # self.action is None/unmapped for requests DRF doesn't route to one of
        # our configured actions (notably OPTIONS, whose metadata handler still
        # calls get_serializer() to introspect fields). Without this, such
        # requests crash with `TypeError: 'NoneType' object is not callable`
        # instead of a normal metadata response.
        return self.serializer_classes_by_action.get("list") or next(
            iter(self.serializer_classes_by_action.values()), None
        )

    def get_permissions(self):
        return [
            permission()
            for permission in self.permission_classes_by_action.get(self.action, [])
        ]

    def get_throttle_class(self):
        return self.throttle_classes_by_action.get(self.action)

    def get_throttles(self):
        throttle_class = self.get_throttle_class()
        if throttle_class is None:
            return super().get_throttles()
        return [throttle_class()]
