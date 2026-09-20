from django.urls import path

from apps.jobtracker.pages import LoginPageView, RegisterPageView, TrackerPageView

app_name = "jobtracker"

urlpatterns = [
    path("", TrackerPageView.as_view(), name="index"),
    path("login/", LoginPageView.as_view(), name="login"),
    path("register/", RegisterPageView.as_view(), name="register"),
]