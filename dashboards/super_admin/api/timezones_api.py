from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from dashboards.utils.timezones import get_gmt_timezones



class TimezonesAPI(APIView):
    permission_classes = [AllowAny]  # Or IsAuthenticated if needed

    def get(self, request):
        timezones = get_gmt_timezones()
        data = [{"value": tz[0], "label": tz[1]} for tz in timezones]
        return Response({"status": True, "data": data})