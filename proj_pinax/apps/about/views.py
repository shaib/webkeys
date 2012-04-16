# Create your views here.
from django.contrib.auth.models import User
from layouteditor.models import Layout
from django.shortcuts import render
from django.template.context import RequestContext

# Home page shows some users and layouts
def homepage(request):
    context = RequestContext(request, dict(
        users = User.objects.order_by("?")[:10],
        layouts = Layout.objects.order_by("?")[:10],
        stdlayouts = Layout.objects.filter(owner__isnull=True)))
    return render(request, "homepage.html", context_instance=context)