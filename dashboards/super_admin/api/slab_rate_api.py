from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


from dashboards.super_admin.api.serializers.slab_rate_serializer import SlabRateSerializer
from dashboards.super_admin.models.clients import SlabRate


class SlabRateAPI(APIView):
    permission_classes = [AllowAny]

    # ✅ LIST
    def get(self, request):
        qs = SlabRate.objects.all().order_by("-id")
        serializer = SlabRateSerializer(qs, many=True)

        return Response({
            "status": True,
            "message": "",
            "data": serializer.data
        })

    # ✅ CREATE
    def post(self, request):
        serializer = SlabRateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": False,
                "message": "Validation error",
                "errors": serializer.errors
            }, status=400)

        slab = serializer.save()

        return Response({
            "status": True,
            "message": "Slab rate created successfully",
            "data": SlabRateSerializer(slab).data
        })


class SlabRateDetailAPI(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        return SlabRate.objects.get(pk=pk)

    # ✅ DETAIL
    def get(self, request, pk):
        try:
            slab = self.get_object(pk)
        except SlabRate.DoesNotExist:
            return Response({
                "status": False,
                "message": "Slab rate not found",
                "data": []
            }, status=404)

        return Response({
            "status": True,
            "message": "",
            "data": SlabRateSerializer(slab).data
        })

    # ✅ UPDATE
    def put(self, request, pk):
        try:
            slab = self.get_object(pk)
        except SlabRate.DoesNotExist:
            return Response({
                "status": False,
                "message": "Slab rate not found",
                "data": []
            }, status=404)

        serializer = SlabRateSerializer(slab, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response({
                "status": False,
                "message": "Validation error",
                "errors": serializer.errors
            }, status=400)

        slab = serializer.save()

        return Response({
            "status": True,
            "message": "Slab rate updated successfully",
            "data": SlabRateSerializer(slab).data
        })

    # ✅ DELETE
    def delete(self, request, pk):
        try:
            slab = SlabRate.objects.get(pk=pk)
            slab.delete(user=request.user)
        except SlabRate.DoesNotExist:
            return Response({
                "status": False,
                "message": "Slab rate not found",
                "data": []
            }, status=404)

        return Response({
            "status": True,
            "message": "Slab rate deleted successfully",
            "data": []
        })
