from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dashboards.super_admin.models.hr import SalarySlip, Employee, Attendance

class SalaryAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Fetch salary details for all employees, including:
        - Employee Name
        - Base Salary
        - Present/Absent Days
        - OT Amount
        - Deductions
        - Net Pay
        - Status
        """

        # Fetch all salary slips with related employee data
        salary_slips = SalarySlip.objects.select_related("employee").all()

        # Prepare the response data
        data = []
        for slip in salary_slips:
            data.append({
                "employee_id": slip.employee.id,
                "employee_name": slip.employee.name,
                "basic_salary": slip.employee.basic_salary,  # Assuming Employee model has a basic_salary field
                "present_days": slip.total_earnings,  # Replace with actual logic for present days
                "other_salary": slip.total_earnings-slip.employee.basic_salary,  # Assuming SalarySlip has an overtime field
                "deductions": slip.total_deductions,
                "net_pay": slip.net_salary,
            })

        return Response({
            "status": True,
            "message": "Salary details fetched successfully",
            "data": data
        })
