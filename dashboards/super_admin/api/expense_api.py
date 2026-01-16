from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dashboards.super_admin.models.inventory import Expense, Category


class ExpenseAPI(APIView):
    permission_classes = [IsAuthenticated]

    # 🔹 LIST
    def get(self, request):
        data = Expense.objects.select_related("category").values(
            "id",
            "expense_date",
            "amount",
            "category__id",
            "category__name",
            "status"
        )

        return Response({
            "status": True,
            "message": "",
            "data": list(data)
        })

    # 🔹 CREATE
    def post(self, request):
        expense_date = request.data.get("expense_date")
        amount = request.data.get("amount")
        category_id = request.data.get("category_id")
        status = request.data.get("status", "paid")

        # ✅ VALIDATION
        if not expense_date or not amount or not category_id:
            return Response({
                "status": False,
                "message": "expense_date, amount and category are required",
                "data": []
            }, status=400)

        if not Category.objects.filter(id=category_id).exists():
            return Response({
                "status": False,
                "message": "Invalid expense category",
                "data": []
            }, status=400)

        expense = Expense.objects.create(
            expense_date=expense_date,
            amount=amount,
            category_id=category_id,
            status=status
        )

        return Response({
            "status": True,
            "message": "Expense added successfully",
            "data": {
                "id": expense.id,
                "expense_date": expense.expense_date,
                "amount": expense.amount,
                "category_id": expense.category_id,
                "status": expense.status
            }
        })
