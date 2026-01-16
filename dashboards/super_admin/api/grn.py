from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dashboards.super_admin.models.finance import PurchaseOrder, GoodsReceiptNote
from dashboards.super_admin.models.base import PartyMaster
import logging
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Max
from django.utils.timezone import now


def generate_grn_number():
    year = now().year

    last_grn = (
        GoodsReceiptNote.objects
        .filter(grn_number__startswith=f"GRN-{year}-")
        .aggregate(Max("grn_number"))
        .get("grn_number__max")
    )

    if last_grn:
        last_number = int(last_grn.split("-")[-1])
        new_number = last_number + 1
    else:
        new_number = 1

    return f"GRN-{year}-{new_number:05d}"

class GRNAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        grn = GoodsReceiptNote.objects.select_related("purchase_order").order_by("-id").values(
            "id",
            "grn_number",
            "received_date",
            "received_by",
            "purchase_order__po_number",
            "related_vehicle",
            "status",
            "grn_status",
        )
        return Response({
            "status": True,
            "data": list(grn)
        })

    def post(self, request):
        data = request.data
        po_id = data.get("purchase_order_id")
        purchase_order = get_object_or_404(PurchaseOrder, pk=po_id)

        if purchase_order.status != "accepted":
            return Response(
                {
                    "status": False,
                    "message": "Only accepted Purchase Orders can have GRN created."
                },
                status=400
            )

        with transaction.atomic():
            grn_number = generate_grn_number()
            grn = GoodsReceiptNote.objects.create(
                purchase_order=purchase_order,
                grn_number=grn_number,   # ✅ backend generated
                received_date=data.get("received_date"),
                received_by=data.get("received_by"),
                related_vehicle=data.get("related_vehicle"),
                status=data.get("status"),
            )
            purchase_order.status = "received"
            purchase_order.save()

        return Response(
            {
                "status": True,
                "message": "Good Receive Note created successfully",
                "data": {
                    "id": grn.id,
                    "grn_number": grn.grn_number
                }
            },
            status=201
        )

class GRNDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        grn = (
            GoodsReceiptNote.objects
            .select_related("purchase_order", "purchase_order__party_master")
            .filter(pk=pk)
            .first()
        )

        if not grn:
            return Response(
                {
                    "status": False,
                    "message": "Good Receive Note not found"
                },
            )

        data = {
            "id": grn.id,
            "grn_number": grn.grn_number,
            "received_date": grn.received_date,
            "received_by": grn.received_by,
            "related_vehicle": grn.related_vehicle,
            "status": grn.status,

            # 🔹 Purchase Order info (flattened)
            "purchase_order_id": grn.purchase_order.id,
            "po_number": grn.purchase_order.po_number,
            "party_master_name": grn.purchase_order.party_master.name,
            "po_date": grn.purchase_order.po_date,
            "po_amount": grn.purchase_order.amount,
        }

        return Response(
            {
                "status": True,
                "data": data
            },
        )

    def put(self, request, pk):
        grn = get_object_or_404(GoodsReceiptNote, pk=pk)
        data = request.data

        # 🔒 Prevent updates if GRN is finalized (optional rule)
        if grn.grn_status == "sent":
            return Response(
                {
                    "status": False,
                    "message": "Sent GRN cannot be updated"
                },
            )

        # 🔹 Update allowed fields only
        grn.received_date = data.get("received_date", grn.received_date)
        grn.received_by = data.get("received_by", grn.received_by)
        grn.related_vehicle = data.get("related_vehicle", grn.related_vehicle)

        # Optional: controlled status update
        if "status" in data:
            grn.status = data.get("status")

        grn.save()

        return Response(
            {
                "status": True,
                "message": "Good Receive Note updated successfully",
                "data": {
                    "id": grn.id,
                    "grn_number": grn.grn_number,
                    "status": grn.status
                }
            },
        )

class GRNActionAPI(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, pk):
        grn = get_object_or_404(GoodsReceiptNote, pk=pk)
        if grn.grn_status == "sent":
            return Response(
                {
                    "status": False,
                    "message": "GRN is already sent"
                },
            )
        grn.grn_status = "sent"
        grn.save()
        return Response(
            {
                "status": True,
                "message": "GRN sent successfully"
            }
        )

class PurchaseOrderFetchAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        purchase_orders = PurchaseOrder.objects.filter(grn__isnull=True)
        return Response({
            "status": True,
            "data": list(purchase_orders)
        })