# dashboards/super_admin/api/deals_api.py
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from dashboards.super_admin.api.asset_api import api_response
from dashboards.super_admin.api.serializers.deal_serializer import DealSerializer
from dashboards.super_admin.models.agent import Deal





class DealListAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        deals = Deal.objects.select_related("agent", "client").all()
        serializer = DealSerializer(deals, many=True)

        return api_response(
            True,
            "Deal list fetched successfully",
            serializer.data
        )

    def post(self, request):
        serializer = DealSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return api_response(
                True,
                "Deal created successfully",
                serializer.data,
                201
            )

        return api_response(
            False,
            "Validation error",
            serializer.errors,
            400
        )


class DealDetailAPI(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        return Deal.objects.get(pk=pk)

    def get(self, request, pk):
        deal = self.get_object(pk)
        serializer = DealSerializer(deal)

        return api_response(
            True,
            "Deal detail fetched",
            serializer.data
        )

    def put(self, request, pk):
        deal = self.get_object(pk)

        serializer = DealSerializer(
            deal,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()  # 🔥 yahin status-flow + commission logic chalega
            return api_response(
                True,
                "Deal updated successfully",
                serializer.data
            )

        return api_response(
            False,
            "Update failed",
            serializer.errors,
            400
        )

    def delete(self, request, pk):
        deal = self.get_object(pk)
        deal.delete()

        return api_response(
            True,
            "Deal deleted successfully",
            {}
        )
