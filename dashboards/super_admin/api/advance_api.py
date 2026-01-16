from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from dashboards.branch.models.branch import Branch
from dashboards.super_admin.models.hr import AdvanceRequest, AdvanceInstallment
from dashboards.super_admin.models.hr import Employee  # Adjust import path as needed

from datetime import datetime
from rest_framework import status
import csv
from io import StringIO
from django.http import HttpResponse

class AdvanceAPI(APIView):
    permission_classes = [AllowAny]

    # GET: Retrieve all advance requests or a specific one by ID
    def get(self, request, pk=None):
        if pk:
            # Retrieve a specific advance request by its ID
            try:
                adv = AdvanceRequest.objects.select_related("employee").get(pk=pk)
            except AdvanceRequest.DoesNotExist:
                return Response({
                    "status": False,
                    "message": "Advance request not found."
                }, status=status.HTTP_404_NOT_FOUND)

            repayment_schedule = [
                {
                    "due_date": inst.due_date,
                    "amount": inst.amount,
                    "payslip_deduction": inst.payslip_deduction,
                }
                for inst in adv.installments.all()
            ]

            data = {
                "id": adv.id,
                "employee": adv.employee_id,
                "employee_name": adv.employee.name,
                "date": adv.date,
                "branch": adv.branch_id,
                "amount": adv.amount,
                "purpose": adv.purpose,
                "repayment_terms": adv.repayment_terms,
                "approver": adv.approver,
                "installments": repayment_schedule,
            }

            return Response({
                "status": True,
                "data": data
            })

        # Retrieve all advance requests
        advances = AdvanceRequest.objects.all().select_related("employee", "branch")
        data = []
        for adv in advances:
            # Build repayment schedule array from related installments
            repayment_schedule = [
                {
                    "due_date": inst.due_date,
                    "amount": inst.amount,
                    "payslip_deduction": inst.payslip_deduction,
                }
                for inst in adv.installments.all()
            ]
            # Append advance data with repayment schedule
            data.append({
                "id": adv.id,
                "employee": adv.employee_id,
                "employee_name": adv.employee.name,
                "date": adv.date,
                "branch": adv.branch_id,
                "amount": adv.amount,
                "purpose": adv.purpose,
                "repayment_terms": adv.repayment_terms,
                "approver": adv.approver,
                "installments": repayment_schedule,
            })
        return Response({
            "status": True,
            "data": data
        })

    # POST: Create a new advance request and its repayment schedule
    def post(self, request):
        # Validate and parse date
        date_str = request.data.get("date")
        if not date_str:
            return Response({"status": False, "message": "Date is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"status": False, "message": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Get employee and branch IDs from request
        employee_id = request.data.get("employee")
        branch_id = request.data.get("branch")

        # Validate employee
        if not employee_id:
            return Response({"status": False, "message": "Employee is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            employee = Employee.objects.get(pk=employee_id)
        except (Employee.DoesNotExist, ValueError):
            return Response({"status": False, "message": "Invalid employee."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate branch (optional)
        branch = None
        if branch_id:
            try:
                branch = Branch.objects.get(pk=branch_id)
            except (Branch.DoesNotExist, ValueError):
                return Response({"status": False, "message": "Invalid branch."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the advance request
        advance = AdvanceRequest.objects.create(
            employee=employee,
            date=date_obj,
            branch=branch,
            amount=request.data.get("amount"),
            purpose=request.data.get("purpose"),
            repayment_terms=request.data.get("repayment_terms"),
            approver=request.data.get("approver")
        )

        # Create related installments from the array
        installments = request.data.get("installments", [])
        for idx, inst in enumerate(installments, start=1):
            AdvanceInstallment.objects.create(
                advance=advance,
                installment_no=idx,
                due_date=inst.get("due_date"),
                amount=inst.get("amount"),
                payslip_deduction=inst.get("payslip_deduction", True)
            )
        return Response({"status": True})

    def put(self, request, pk):
        """
        Update an existing advance request and its repayment schedule.
        """
        try:
            adv = AdvanceRequest.objects.get(pk=pk)
        except AdvanceRequest.DoesNotExist:
            return Response({
                "status": False,
                "message": "Advance request not found."
            })

        # Update fields
        adv.date = request.data.get("date", adv.date)
        adv.amount = request.data.get("amount", adv.amount)
        adv.purpose = request.data.get("purpose", adv.purpose)
        adv.repayment_terms = request.data.get("repayment_terms", adv.repayment_terms)
        adv.approver = request.data.get("approver", adv.approver)
        adv.save()

        # Update installments
        installments = request.data.get("installments", [])
        adv.installments.all().delete()  # Clear existing installments
        for idx, inst in enumerate(installments, start=1):
            AdvanceInstallment.objects.create(
                advance=adv,
                installment_no=idx,
                due_date=inst.get("due_date"),
                amount=inst.get("amount"),
                payslip_deduction=inst.get("payslip_deduction", True)
            )

        return Response({"status": True, "message": "Advance request updated successfully."})

class AdvanceCSVAPI(APIView):
    permission_classes = [AllowAny]

    # GET: Retrieve all advance requests formatted for CSV export
    def get(self, request):
        advances = AdvanceRequest.objects.all().select_related("employee", "branch")

        # Create in-memory buffer
        buffer = StringIO()
        writer = csv.writer(buffer)

        # Write header
        writer.writerow([
            "Employee ID", "Employee Name", "Date", "Branch",
            "Amount", "Purpose", "Repayment Terms", "Approver"
        ])

        # Write data rows
        for adv in advances:
            writer.writerow([
                adv.employee_id,
                adv.employee.name,
                adv.date,
                adv.branch.name if adv.branch else "",
                adv.amount,
                adv.purpose,
                adv.repayment_terms,
                adv.approver,
            ])

        # Prepare response
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="advance_requests.csv"'
        return response