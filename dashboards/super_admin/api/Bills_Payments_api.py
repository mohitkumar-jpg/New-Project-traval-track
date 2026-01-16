from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dashboards.super_admin.models.base import PartyMaster
from dashboards.super_admin.models.finance import BillDetails, BillDetailsItem
import logging
from django.shortcuts import get_object_or_404


class BillsPaymentsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bills = BillDetails.objects.select_related("party_master").all().values(
            "id",
            "bill_number",
            "bill_date",
            "party_master__name",
            "total_quantity",
            "total_amount",
            "status",
        )
        return Response({
            "status": True,
            "data": list(bills)
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
            bill = BillDetails.objects.create(
                party_master=party_master,
                bill_number=data.get("bill_number"),
                bill_date=data.get("bill_date"),
                total_quantity=0,  # will be updated after items creation
                total_amount=0,    # will be updated after items creation
                status=data.get("status", "draft"),
            )

            total_quantity = 0
            total_amount = 0

            for item in items_data:
                bill_item = BillDetailsItem.objects.create(
                    bill=bill,
                    description=item.get("description"),
                    quantity=item.get("quantity", 1),
                    unit_price=item.get("unit_price", 0),
                )
                total_quantity += bill_item.quantity
                total_amount += bill_item.quantity * bill_item.unit_price

            bill.total_quantity = total_quantity
            bill.total_amount = total_amount
            bill.save()

        return Response({
            "status": True,
            "message": "Bill created successfully",
            "data": {
                "id": bill.id,
                "bill_number": bill.bill_number
            }
        })

class PartyMasterDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        party = (
            PartyMaster.objects
            .select_related("location", "category")
            .filter(pk=pk)
            .values(
                "id",
                "vendor_type",
                "name",
                "contact_person",
                "phone",
                "email",
                "gst_number",
                "pan_number",
                "payment_terms",
                "status",
                "category_id",

                # Location fields (flat)
                "location__id",
                "location__country",
                "location__state",
                "location__city",
                "location__address",
                "location__zip_code",
            )
            .first()
        )

        if not party:
            return Response(
                {
                    "status": False,
                    "message": "Party Master not found"
                },
                status=404
            )

        # 🔹 Flatten response (NO nested object)
        response_data = {
            "id": party["id"],
            "vendor_type": party["vendor_type"],
            "name": party["name"],
            "contact_person": party["contact_person"],
            "phone": party["phone"],
            "email": party["email"],
            "gst_number": party["gst_number"],
            "pan_number": party["pan_number"],
            "payment_terms": party["payment_terms"],
            "status": party["status"],
            "category_id": party["category_id"],

            # Location fields at same level
            "location_id": party["location__id"],
            "country": party["location__country"],
            "state": party["location__state"],
            "city": party["location__city"],
            "address": party["location__address"],
            "zip_code": party["location__zip_code"],
        }

        return Response(
            {
                "status": True,
                "data": response_data
            },
            status=200
        )


    def put(self, request, pk):
        data = request.data
        party_master = get_object_or_404(PartyMaster, pk=pk)

        party_master.vendor_type = data.get("vendor_type", party_master.vendor_type)
        party_master.name = data.get("name", party_master.name)
        party_master.contact_person = data.get("contact_person", party_master.contact_person)
        party_master.phone = data.get("phone", party_master.phone)
        party_master.email = data.get("email", party_master.email)
        party_master.gst_number = data.get("gst_number", party_master.gst_number)
        party_master.pan_number = data.get("pan_number", party_master.pan_number)
        party_master.payment_terms = data.get("payment_terms", party_master.payment_terms)
        party_master.status = data.get("status", party_master.status)

        location_data = data.get("location")
        if location_data:
            location = party_master.location.first()
            if location:
                location.country = location_data.get("country", location.country)
                location.state = location_data.get("state", location.state)
                location.city = location_data.get("city", location.city)
                location.address = location_data.get("address", location.address)
                location.zip_code = location_data.get("zip_code", location.zip_code)
                location.save()
            else:
                location = Location.objects.create(
                    parent=party_master,
                    country=location_data.get("country"),
                    state=location_data.get("state"),
                    city=location_data.get("city"),
                    address=location_data.get("address"),
                    zip_code=location_data.get("zip_code"),
                )

        category_id = data.get("category_id")
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            party_master.category = category

        party_master.save()

        return Response({
            "status": True,
            "message": "Party Master updated successfully",
            "data": {
                "id": party_master.id,
                "name": party_master.name
            }
        })
    def delete(self, request, pk):
        party_master = get_object_or_404(PartyMaster, pk=pk)
        party_master.delete(user=request.user)
        return Response({
            "status": True,
            "message": "Party Master deleted successfully"
        })