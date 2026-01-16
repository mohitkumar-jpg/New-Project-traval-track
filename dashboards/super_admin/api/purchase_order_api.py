from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dashboards.super_admin.models.finance import PurchaseOrder, PurchaseOrderItem
from dashboards.super_admin.models.base import PartyMaster
import logging
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils.timezone import now
from django.db.models import Max


logger = logging.getLogger(__name__)

def generate_po_number():
    year = now().year

    last_po = (
        PurchaseOrder.objects
        .filter(po_number__startswith=f"PO-{year}-")
        .aggregate(Max("po_number"))
        .get("po_number__max")
    )

    if last_po:
        last_number = int(last_po.split("-")[-1])
        new_number = last_number + 1
    else:
        new_number = 1

    return f"PO-{year}-{new_number:05d}"

class PurchaseOrderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        order = PurchaseOrder.objects.select_related("party_master").order_by("-id").values(
            "id",
            "po_number",
            "po_date",
            "party_master__name",
            "amount",
            "delivery_date",
            "status",
            "payment_terms",
        )
        return Response({
            "status": True,
            "data": list(order)
        })

    def post(self, request):
        data = request.data

        party_master = get_object_or_404(
            PartyMaster, id=data.get("party_master_id")
        )

        items_data = data.get("items", [])

        if not items_data:
            return Response(
                {"status": False, "message": "At least one item is required"},
            )

        with transaction.atomic():
            po_number = generate_po_number()
            purchase_order = PurchaseOrder.objects.create(
                party_master=party_master,
                po_number=po_number,
                po_date=data.get("po_date"),
                delivery_date=data.get("delivery_date"),
                payment_terms=data.get("payment_terms"),
                status=data.get("status", "draft"),
                amount=0  # will be updated after items creation
            )

            total_amount = 0

            for item in items_data:
                po_item = PurchaseOrderItem.objects.create(
                    purchase_order=purchase_order,
                    description=item.get("description"),
                    quantity=item.get("quantity", 1),
                    rate=item.get("rate"),
                    tax=item.get("tax", 0)
                )
                total_amount += po_item.amount

            purchase_order.amount = total_amount
            purchase_order.save()

        return Response(
            {
                "status": True,
                "message": "Purchase Order created successfully",
                "data": {
                    "id": purchase_order.id,
                    "po_number": purchase_order.po_number,
                    "party_master": {
                        "id": party_master.id,
                        "name": party_master.name
                    },
                    "amount": purchase_order.amount
                }
            },
        )

class PurchaseOrderActionAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        purchase_order = (
            PurchaseOrder.objects
            .select_related("party_master")
            .prefetch_related("items")
            .filter(pk=pk)
            .first()
        )

        if not purchase_order:
            return Response(
                {
                    "status": False,
                    "message": "Purchase Order not found"
                },
            )

        items = [
            {
                "id": item.id,
                "description": item.description,
                "quantity": item.quantity,
                "rate": item.rate,
                "tax": item.tax,
                "amount": item.amount
            }
            for item in purchase_order.items.all()
        ]

        response_data = {
            "id": purchase_order.id,
            "po_number": purchase_order.po_number,
            "po_date": purchase_order.po_date,
            "party_master_id": purchase_order.party_master.id,
            "party_master_name": purchase_order.party_master.name,
            "amount": purchase_order.amount,
            "delivery_date": purchase_order.delivery_date,
            "status": purchase_order.status,
            "payment_terms": purchase_order.payment_terms,
            "items": items
        }

        return Response(
            {
                "status": True,
                "data": response_data
            },
        )

    def delete(self, request, pk):
        order = get_object_or_404(PurchaseOrder, pk=pk)
        if order.status=="draft":
            order.hard_delete()
            return Response({
                "status": True,
                "message": "Purchase Order deleted successfully"
            })
        else:
            return Response({
                "status": False,
                "message": "Method not allowed. Only draft orders can be deleted."
            }, status=405)

    def put(self, request, pk):
        order = get_object_or_404(PurchaseOrder, pk=pk)
        data = request.data

        if order.status != "draft":
            return Response(
                {
                    "status": False,
                    "message": "Only draft orders can be updated."
                },
            )

        items_data = data.get("items", [])

        with transaction.atomic():
            # 🔹 Update Purchase Order fields
            order.po_number = data.get("po_number", order.po_number)
            order.po_date = data.get("po_date", order.po_date)
            order.delivery_date = data.get("delivery_date", order.delivery_date)
            order.payment_terms = data.get("payment_terms", order.payment_terms)
            order.status = data.get("status", order.status)
            order.save()

            existing_items = {item.id: item for item in order.items.all()}
            received_item_ids = []

            total_amount = 0

            for item in items_data:
                item_id = item.get("id")

                if item_id and item_id in existing_items:
                    # 🔁 Update existing item
                    po_item = existing_items[item_id]
                    po_item.description = item.get("description", po_item.description)
                    po_item.quantity = item.get("quantity", po_item.quantity)
                    po_item.rate = item.get("rate", po_item.rate)
                    po_item.tax = item.get("tax", po_item.tax)
                    po_item.save()

                else:
                    # ➕ Create new item
                    po_item = PurchaseOrderItem.objects.create(
                        purchase_order=order,
                        description=item.get("description"),
                        quantity=item.get("quantity", 1),
                        rate=item.get("rate"),
                        tax=item.get("tax", 0)
                    )

                received_item_ids.append(po_item.id)
                total_amount += po_item.amount

            # 🗑️ Delete removed items
            for item_id, item in existing_items.items():
                if item_id not in received_item_ids:
                    item.delete()

            # 🔢 Update total amount
            order.amount = total_amount
            order.save()

        return Response(
            {
                "status": True,
                "message": "Purchase Order updated successfully",
                "data": {
                    "id": order.id,
                    "amount": order.amount
                }
            },
        )
    
class PurchaseOrderUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        logger.info(
            "PurchaseOrder status update requested | order_id=%s | user=%s",
            pk,
            request.user
        )

        order = get_object_or_404(PurchaseOrder, pk=pk)
        logger.debug(
            "Current status of PurchaseOrder | order_id=%s | status=%s",
            order.id,
            order.status
        )

        if order.status == "draft":
            order.status = "sent"
            order.save()
            logger.info(
                "PurchaseOrder sent | order_id=%s | new_status=sent",
                order.id
            )
            return Response({
                "status": True,
                "message": "Purchase Order sent successfully"
            })

        elif order.status == "sent":
            order.status = "accepted"
            order.save()
            logger.info(
                "PurchaseOrder accepted | order_id=%s | new_status=accepted",
                order.id
            )
            return Response({
                "status": True,
                "message": "Purchase Order accepted successfully"
            })

        # elif order.status == "accepted":
        #     order.status = "received"
        #     order.save()
        #     logger.info(
        #         "PurchaseOrder received | order_id=%s | new_status=received",
        #         order.id
        #     )
        #     return Response({
        #         "status": True,
        #         "message": "Purchase Order received successfully"
        #     })

        else:
            logger.warning(
                "Invalid status transition attempted | order_id=%s | status=%s",
                order.id,
                order.status
            )
            return Response({
                "status": False,
                "message": "Method not allowed"
            }, status=405)
