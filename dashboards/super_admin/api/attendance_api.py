from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from dashboards.super_admin.models.hr import Attendance, Employee


class AttendanceAPI(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        """
        Expected JSON:
        {
          "employee_id": 10,
          "date": "2026-01-08",
          "status": "present",
          "check_in": "09:00:00",
          "check_out": "17:00:00",
          "note": "On time"
        }
        """

        employee_id = request.data.get("employee_id")
        date = request.data.get("date")
        status = request.data.get("status")
        check_in = request.data.get("check_in") or None
        check_out = request.data.get("check_out") or None
        note = request.data.get("note", "")

        # Validate required fields
        if not employee_id or not date or not status:
            return Response({
                "status": False,
                "message": "employee_id, date, and status are required",
                "data": []
            }, status=400)

        # Check if the employee exists
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({
                "status": False,
                "message": "Invalid employee",
                "data": []
            }, status=400)

        # Create or update attendance record
        attendance, created = Attendance.objects.update_or_create(
            employee=employee,
            date=date,
            defaults={
                "status": status,
                "check_in": check_in,
                "check_out": check_out,
                "note": note
            }
        )

        return Response({
            "status": True,
            "message": "Attendance saved successfully",
            "data": {
                "attendance_id": attendance.id,
                "created": created
            }
        })

    def get(self, request, date):
        """
        Get all employees who have not been marked for attendance on a specific date
        Query Parameters:
        - date: Date of the attendance in YYYY-MM-DD format
        """

        # Validate the date parameter
        if not date:
            return Response({
                "status": False,
                "message": "Date is required",
                "data": []
            }, status=400)

        # Retrieve all employees
        employees = Employee.objects.all()

        # Get employees who have attendance marked for the given date
        marked_employees = Attendance.objects.filter(date=date).values_list('employee_id', flat=True)

        # Filter employees who are not in the marked_employees list
        unmarked_employees = employees.exclude(id__in=marked_employees)

        # Prepare the response data
        data = []
        for employee in unmarked_employees:
            data.append({
                "employee_id": employee.id,
                "employee_name": employee.name,
                "department_name": employee.department.name
            })

        return Response({
            "status": True,
            "message": "Employees without attendance for the given date",
            "data": data
        })

    def get(self, request, pk):
        """
        Query Parameters:
        - employee_id: ID of the employee
        - date: Date of the attendance in YYYY-MM-DD format
        """

        employee_id = request.GET.get("employee_id")
        date = request.GET.get("date")

        # Validate required fields
        if not employee_id or not date:
            return Response({
                "status": False,
                "message": "employee_id and date are required",
                "data": []
            }, status=400)

        # Check if the employee exists
        try:
            employee = Employee.objects.select_related('department').get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({
                "status": False,
                "message": "Invalid employee",
                "data": []
            }, status=400)

        # Retrieve attendance record
        try:
            attendance = Attendance.objects.get(employee=employee, date=date)
        except Attendance.DoesNotExist:
            return Response({
                "status": True,
                "message": "No attendance found",
                "data": []
            })

        return Response({
            "status": True,
            "message": "",
            "data": {
                "attendance_id": attendance.id,
                "employee_id": attendance.employee.id,
                "employee_name": attendance.employee.name,
                "department_name": attendance.employee.department.name,  # Include department name
                "date": attendance.date,
                "status": attendance.status,
                "check_in": attendance.check_in,
                "check_out": attendance.check_out,
                "note": attendance.note
            }
        })

    def get(self, request):
        """
        Get details for all attendance records
        Query Parameters (Optional):
        - date: Filter attendance records by a specific date (YYYY-MM-DD)
        """

        date = request.GET.get("date")

        # Filter attendance records by date if provided
        if date:
            attendances = Attendance.objects.filter(date=date).select_related('employee', 'employee__department')
        else:
            attendances = Attendance.objects.all().select_related('employee', 'employee__department')

        # Prepare the response data
        data = []
        for attendance in attendances:
            data.append({
                "attendance_id": attendance.id,
                "employee_id": attendance.employee.id,
                "employee_name": attendance.employee.name,
                "department_name": attendance.employee.department.name,
                "date": attendance.date,
                "status": attendance.status,
                "check_in": attendance.check_in,
                "check_out": attendance.check_out,
                "note": attendance.note
            })

        return Response({
            "status": True,
            "message": "Attendance records retrieved successfully",
            "data": data
        })

    def put(self, request, pk):
        """
        Update attendance record by ID
        Expected JSON:
        {
          "status": "present",
          "check_in": "09:00:00",
          "check_out": "17:00:00",
          "note": "On time"
        }
        """

        status = request.data.get("status")
        check_in = request.data.get("check_in") or None
        check_out = request.data.get("check_out") or None
        note = request.data.get("note", "")

        # Retrieve attendance record
        try:
            attendance = Attendance.objects.get(id=pk)
        except Attendance.DoesNotExist:
            return Response({
                "status": False,
                "message": "Attendance record not found",
                "data": []
            }, status=404)

        # Update fields
        if status:
            attendance.status = status
        if check_in:
            attendance.check_in = check_in
        if check_out:
            attendance.check_out = check_out
        attendance.note = note
        attendance.save()

        return Response({
            "status": True,
            "message": "Attendance updated successfully",
            "data": {
                "attendance_id": attendance.id
            }
        })