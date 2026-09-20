from rest_framework import serializers

from apps.jobtracker.models import Application, Board


class BoardSerializer(serializers.ModelSerializer):
    applications_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Board
        fields = ("id", "name", "order", "applications_count", "created_at")
        read_only_fields = ("id", "order", "applications_count", "created_at")


class BoardCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Board
        fields = ("id", "name")
        read_only_fields = ("id",)
        extra_kwargs = {"name": {"required": False, "allow_blank": True}}


class BoardRenameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ("id", "name")
        read_only_fields = ("id",)


class ApplicationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    round_display = serializers.CharField(source="get_round_display", read_only=True)

    class Meta:
        model = Application
        fields = (
            "id",
            "board",
            "company",
            "position",
            "status",
            "status_display",
            "salary",
            "round",
            "round_display",
            "notes",
            "order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "board", "order", "created_at", "updated_at")


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ("id", "board", "company", "position", "status", "salary", "round", "notes")
        read_only_fields = ("id",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request is not None:
            self.fields["board"].queryset = Board.objects.filter(user=request.user)