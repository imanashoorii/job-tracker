from django.views.generic import TemplateView


class TrackerPageView(TemplateView):
    template_name = "jobtracker/index.html"


class LoginPageView(TemplateView):
    template_name = "jobtracker/login.html"


class RegisterPageView(TemplateView):
    template_name = "jobtracker/register.html"