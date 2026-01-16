# dashboards/super_admin/api/asset_api.py

from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dashboards.super_admin.models.hr import Employee
from dashboards.super_admin.models.inventory import Asset, AssetDisposal, Category
from django.db.models import F
from datetime import datetime
import logging
from django.shortcuts import get_object_or_404



# =====================================================
# 🔹 Helpers
# =====================================================

def api_response(status=True, message="", data=None, code=200):
    return Response(
        {
            "status": status,
            "message": message,
            "data": data if data is not None else [],
        },
        status=code,
    )


def parse_date(value):
    """
    Convert string date (YYYY-MM-DD) to python date object
    """
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None
    return value


# =====================================================
# 🔹 CATEGORY APIs
# =====================================================

class CategoryAPI(APIView):
    permission_classes = [IsAuthenticated]

    # ---------- LIST ----------
    def get(self, request):
        cattype = request.query_params.get("type")
        data = Category.objects.filter(cat_type=cattype).values(
            "id", "name", "description", "status", "created_at"
        )
        return api_response(True, "Category list", list(data))

    # ---------- CREATE ----------
    def post(self, request):
        name = request.data.get("name")

        if not name:
            return api_response(False, "Category name is required", code=400)

        if Category.objects.filter(name__iexact=name).exists():
            return api_response(False, "Category already exists", code=400)

        cat = Category.objects.create(
            name=name,
            cat_type=request.data.get("type"),
            description=request.data.get("description"),
            status=request.data.get("status", "active"),
        )

        logging.info(f"Category created by {request.user.username}: {cat.name} (ID: {cat.id})")

        return api_response(
            True, "Category created successfully", {"id": cat.id}
        )
    
    def delete(self, request, pk):
        #write code to delete the entire category
        category = get_object_or_404(Category, pk=pk)
        category.delete(user=request.user)
        logging.info(f"Category deleted by {request.user.username}: {category.name} (ID: {category.id})")
        return api_response(True, "Category deleted successfully")

    def put(self, request, pk):
        category = get_object_or_404(Category, pk=pk)

        name = request.data.get("name")
        description = request.data.get("description")
        status = request.data.get("status")

        # Validate status if provided
        if status and status not in dict(Category.STATUS_CHOICES):
            return api_response(False, "Invalid status value", code=400)

        # Check duplicate name (excluding current category)
        if name:
            if Category.objects.filter(name__iexact=name).exclude(id=pk).exists():
                return api_response(False, "Category name already exists", code=400)
            category.name = name

        if description is not None:
            category.description = description

        if status:
            category.status = status

        category.save()

        logging.info(
            f"Category updated by {request.user.username}: {category.name} (ID: {category.id})"
        )

        return api_response(
            True,
            "Category updated successfully",
            {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "status": category.status,
            },
        )

# =====================================================
# 🔹 ASSET APIs (LIST + CREATE)
# =====================================================

class AssetAPI(APIView):
    permission_classes = [IsAuthenticated]

    # ---------- LIST ----------
    def get(self, request):
        category_id = request.query_params.get("category_id")

        qs = Asset.objects.select_related("category").filter(
            status__in=["active", "maintenance"]
        )

        if category_id:
            qs = qs.filter(category_id=category_id)

        data = qs.annotate(
            book_value=F("current_value")        
        ).values(
            "id",
            "code",
            "name",
            "description",
            "category__id",
            "category__name",
            "purchase_value",
            "book_value",
            "status",
        )

        return api_response(True, "Asset list", list(data))

    # ---------- CREATE ----------
    def post(self, request):
        asset = Asset.objects.create(
            code=request.data.get("code"),
            name=request.data.get("name"),
            description=request.data.get("description"),
            vendor=request.data.get("vendor"),
            useful_life_years=request.data.get("useful_life_years", 0),
            category_id=request.data.get("category_id"),
            invoice_id=request.data.get("invoice_id"),
            assigned_to_id=request.data.get("assigned_to_id"),
            purchase_date=request.data.get("purchase_date"),
            purchase_value=float(request.data.get("purchase_value", 0)),
            residual_value=float(request.data.get("residual_value") or 0),
            depreciation_method=request.data.get("depreciation_method", "slm"),
            location=request.data.get("location"),
            depreciation_start_date=request.data.get("depreciation_start_date"),
            status=request.data.get("status", "active"),
            serial_number=request.data.get("serial_number"),
            capitalization_status=request.data.get("capitalization_status", True),
            vintage=request.data.get("vintage"),
            warranty_expiry_date=request.data.get("warranty_expiry_date"),
            insurance_policy_number=request.data.get("insurance_policy_number"),
            current_value=float(request.data.get("purchase_value", 0)),  # initial value
        )

        return Response(
            {
                "message": "Asset created successfully",
                "asset_id": asset.id,
                "status": 200,
            },
        )


# =====================================================
# 🔹 ASSET DETAIL APIs (GET / UPDATE / DELETE)
# =====================================================

class AssetDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    # ---------- GET ----------
    def get(self, request, pk):
        asset = (
            Asset.objects
            .select_related("category", "assigned_to")
            .filter(pk=pk)
            .values(
                "id",
                "code",
                "name",
                "description",
                "vendor",
                "useful_life_years",
                "category_id",
                "invoice_id",
                "assigned_to_id",
                "purchase_date",
                "purchase_value",
                "residual_value",
                "depreciation_method",
                "location",
                "depreciation_start_date",
                "capitalization_status",
                "status",
                "serial_number",
                "vintage",
                "warranty_expiry_date",
                "insurance_policy_number",
                "current_value",
            )
            .first()
        )

        if not asset:
            return Response(
                {"message": "Asset not found"},
            )

        return Response(
            {
                "data": asset,
                "status": 200,
            }
        )

    # ---------- PUT ----------
    def put(self, request, pk):
        asset = get_object_or_404(Asset, pk=pk)

        asset.code = request.data.get("code", asset.code)
        asset.name = request.data.get("name", asset.name)
        asset.description = request.data.get("description", asset.description)
        asset.vendor = request.data.get("vendor", asset.vendor)
        asset.useful_life_years = request.data.get(
            "useful_life_years", asset.useful_life_years
        )
        asset.category_id = request.data.get("category_id", asset.category_id)
        asset.invoice_id = request.data.get("invoice_id", asset.invoice_id)
        asset.assigned_to_id = request.data.get(
            "assigned_to_id", asset.assigned_to_id
        )
        asset.purchase_date = request.data.get(
            "purchase_date", asset.purchase_date
        )
        asset.purchase_value = float(
            request.data.get("purchase_value", asset.purchase_value)
        )
        asset.residual_value = float(
            request.data.get("residual_value", asset.residual_value)
        )
        asset.depreciation_method = request.data.get(
            "depreciation_method", asset.depreciation_method
        )
        asset.location = request.data.get("location", asset.location)
        asset.depreciation_start_date = request.data.get(
            "depreciation_start_date", asset.depreciation_start_date
        )
        asset.status = request.data.get("status", asset.status)
        asset.serial_number = request.data.get(
            "serial_number", asset.serial_number
        )
        asset.vintage = request.data.get("vintage", asset.vintage)
        asset.warranty_expiry_date = request.data.get(
            "warranty_expiry_date", asset.warranty_expiry_date
        )
        asset.insurance_policy_number = request.data.get(
            "insurance_policy_number", asset.insurance_policy_number
        )

        # 🔹 Update current value if purchase value changes
        if "purchase_value" in request.data:
            asset.current_value = asset.purchase_value

        asset.save()

        return Response(
            {
                "message": "Asset updated successfully",
                "status": 200
            }
        )

    # ---------- DELETE ----------
    def delete(self, request, pk):
        asset = get_object_or_404(Asset, pk=pk)
        asset.delete(user=request.user)

        return Response(
            {
                "message": "Asset deleted successfully",
                "status": 200
            }
        )


# ---------- DISPOSAL RECORDS ----------
class AssetDisposalAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        disposals = AssetDisposal.objects.select_related("asset").all().values(
            "id",
            "asset_id",
            "asset__name",
            "disposal_date",
            "disposal_mode",
            "sale_price",
            "buyer_details",
            "notes",
        )
        return Response(
            {
                "data": list(disposals),
                "status": 200
            }
        )

    def post(self, request, asset_id):
        asset = get_object_or_404(Asset, pk=asset_id)

        disposal = AssetDisposal.objects.create(
            asset=asset,
            disposal_date=request.data.get("disposal_date"),
            disposal_mode=request.data.get("disposal_mode"),
            sale_price=Decimal(request.data.get("sale_price", 0)),
            buyer_details=request.data.get("buyer_details"),
            notes=request.data.get("notes"),
        )

        # Update asset status to 'disposed'
        asset.status = "retired"
        asset.save()

        return Response(
            {
                "message": "Asset disposal recorded successfully",
                "disposal_id": disposal.id,
                "status": 200
            }
        )

class DepreciationSchedulerAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        assets = Asset.objects.filter(status__in=["active", "maintenance"])
        for asset in assets:
            asset.calculate_depreciation()
            asset.save()

        return Response(
            {
                "message": "Depreciation calculation completed for all assets",
                "status": 200
            }
        )