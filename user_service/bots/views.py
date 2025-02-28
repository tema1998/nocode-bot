from django.shortcuts import render
from django.views import View


class BotView(View):

    def get(self, request):
        """
        Handles GET requests.
        """
        return render(request, "bots/index.html")
