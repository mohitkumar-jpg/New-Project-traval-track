from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser ,JSONParser


from dashboards.super_admin.api.serializers.employee_serializer import EmployeeSerializer
from dashboards.super_admin.models.hr import Employee





class EmployeeAPI(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # ✅ LIST
    def get(self, request):
        qs = Employee.objects.select_related(
            "department", "designation", "branch"
        ).order_by("-id")

        serializer = EmployeeSerializer(qs, many=True)
        return Response({
            "status": True,
            "message": "",
            "data": serializer.data
        })

    # ✅ CREATE
    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": False,
                "message": "Validation error",
                "errors": serializer.errors
            }, status=400)
        
        emp = serializer.save()

        return Response({
            "status": True,
            "message": "Employee created successfully",
            "data": EmployeeSerializer(emp).data
        })

class EmployeeDetailAPI(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, pk):
        return Employee.objects.get(pk=pk)

    # ✅ DETAIL
    def get(self, request, pk):
        try:
            emp = self.get_object(pk)
        except Employee.DoesNotExist:
            return Response({
                "status": False,
                "message": "Employee not found",
                "data": []
            }, status=404)

        return Response({
            "status": True,
            "message": "",
            "data": EmployeeSerializer(emp).data
        })

    # ✅ UPDATE
    def put(self, request, pk):
        try:
            emp = self.get_object(pk)
        except Employee.DoesNotExist:
            return Response({
                "status": False,
                "message": "Employee not found",
                "data": []
            }, status=404)

        serializer = EmployeeSerializer(emp, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response({
                "status": False,
                "message": "Validation error",
                "errors": serializer.errors
            }, status=400)

        emp = serializer.save()

        return Response({
            "status": True,
            "message": "Employee updated successfully",
            "data": EmployeeSerializer(emp).data
        })

    # ✅ DELETE
    def delete(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
            employee.delete(user=request.user)
        except Employee.DoesNotExist:
            return Response({
                "status": False,
                "message": "Employee not found",
                "data": []
            }, status=404)

        return Response({
            "status": True,
            "message": "Employee deleted successfully",
            "data": []
        })
