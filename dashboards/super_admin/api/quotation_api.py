from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


from dashboards.super_admin.api.serializers.quotation_serializer import (
    QuotationSerializer,
    QuotationFollowUpSerializer
)
from dashboards.super_admin.models.gst import Quotation



class QuotationAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Quotation.objects.prefetch_related("items", "followups").order_by("-id")
        serializer = QuotationSerializer(qs, many=True)

        return Response({
            "status": True,
            "message": "",
            "data": serializer.data
        })

    def post(self, request):
        serializer = QuotationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": False,
                "message": "Validation error",
                "errors": serializer.errors
            }, status=400)

        quotation = serializer.save()

        return Response({
            "status": True,
            "message": "Quotation created successfully",
            "data": QuotationSerializer(quotation).data
        })


class QuotationDetailAPI(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        return Quotation.objects.get(pk=pk)

    def get(self, request, pk):
        try:
            quotation = self.get_object(pk)
        except Quotation.DoesNotExist:
            return Response({
                "status": False,
                "message": "Quotation not found",
                "data": []
            }, status=404)

        return Response({
            "status": True,
            "message": "",
            "data": QuotationSerializer(quotation).data
        })

    def put(self, request, pk):
        try:
            quotation = self.get_object(pk)
        except Quotation.DoesNotExist:
            return Response({
                "status": False,
                "message": "Quotation not found",
                "data": []
            }, status=404)

        serializer = QuotationSerializer(quotation, data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": False,
                "message": "Validation error",
                "errors": serializer.errors
            }, status=400)

        quotation = serializer.save()

        return Response({
            "status": True,
            "message": "Quotation updated successfully",
            "data": QuotationSerializer(quotation).data
        })

    def delete(self, request, pk):
        try:
            quotation = Quotation.objects.get(pk=pk)
            quotation.delete(user=request.user)
        except Quotation.DoesNotExist:
            return Response({
                "status": False,
                "message": "Quotation not found",
                "data": []
            }, status=404)

        return Response({
            "status": True,
            "message": "Quotation deleted successfully",
            "data": []
        })



class QuotationFollowUpAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = QuotationFollowUpSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": False,
                "message": "Validation error",
                "errors": serializer.errors
            }, status=400)

        followup = serializer.save()

        return Response({
            "status": True,
            "message": "Follow-up added successfully",
            "data": QuotationFollowUpSerializer(followup).data
        })

