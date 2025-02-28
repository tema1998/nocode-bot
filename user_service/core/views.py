from django.shortcuts import render
from django.views import View


class IndexView(View):
    """
    Handles GET requests for the registration form.
    """

    def get(self, request):
        """
        Handles GET requests.
        """
        return render(request, "core/index.html")
