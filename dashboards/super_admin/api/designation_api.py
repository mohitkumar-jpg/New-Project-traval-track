from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from dashboards.super_admin.models.hr import Designation, Department
from django.db.models import F



class DesignationAPI(APIView):
    permission_classes = [AllowAny]

    # ✅ LIST
    def get(self, request):
        data = Designation.objects.select_related("department").annotate(
            department_name=F("department__name")   # ✅ alias
        ).values(
            "id",
            "designation_name",
            "department_id",
            "department_name",   # ✅ frontend friendly
            "status"
        )

        return Response({
            "status": True,
            "message": "",
            "data": list(data)
        })

    # ✅ CREATE
    def post(self, request):
        name = request.data.get("name")
        department_id = request.data.get("department_id")
        status = request.data.get("status", "active")

        if not name or not department_id:
            return Response({
                "status": False,
                "message": "Designation name and department are required",
                "data": []
            }, status=400)

        if not Department.objects.filter(id=department_id).exists():
            return Response({
                "status": False,
                "message": "Invalid department",
                "data": []
            }, status=400)

        if Designation.objects.filter(
            designation_name=name,
            department_id=department_id
        ).exists():
            return Response({
                "status": False,
                "message": "Designation already exists in this department",
                "data": []
            }, status=400)

        desig = Designation.objects.create(
            designation_name=name,
            department_id=department_id,
            status=status
        )

        return Response({
            "status": True,
            "message": "Designation created successfully",
            "data": {
                "id": desig.id,
                "designation_name": desig.designation_name,
                "department_id": desig.department_id,
                "status": desig.status
            }
        })


class DesignationDetailAPI(APIView):
    permission_classes = [AllowAny]

    # ✅ UPDATE
    def put(self, request, pk):
        try:
            desig = Designation.objects.get(pk=pk)
        except Designation.DoesNotExist:
            return Response({
                "status": False,
                "message": "Designation not found",
                "data": []
            }, status=404)

        department_id = request.data.get("department_id", desig.department_id)

        if not Department.objects.filter(id=department_id).exists():
            return Response({
                "status": False,
                "message": "Invalid department",
                "data": []
            }, status=400)

        desig.designation_name = request.data.get(
            "name", desig.designation_name
        )
        desig.department_id = department_id
        desig.status = request.data.get("status", desig.status)
        desig.save()

        return Response({
            "status": True,
            "message": "Designation updated successfully",
            "data": {
                "id": desig.id,
                "designation_name": desig.designation_name,
                "department_id": desig.department_id,
                "status": desig.status
            }
        })

    # ✅ DELETE
    def delete(self, request, pk):
        try:
            designation = Designation.objects.get(pk=pk)
            designation.delete(user=request.user)

        except Designation.DoesNotExist:
            return Response({
                "status": False,
                "message": "Designation not found",
                "data": []
            }, status=404)

        return Response({
            "status": True,
            "message": "Designation deleted successfully",
            "data": []
        })
