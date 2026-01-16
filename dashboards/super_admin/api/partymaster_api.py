from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dashboards.super_admin.models.base import PartyMaster, Location, Category
import logging
from django.shortcuts import get_object_or_404


class PartyMasterAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        party_masters = PartyMaster.objects.select_related("location", "category").all().values(
            "id",
            "vendor_type",
            "name",
            "contact_person",
            "category__name",
            "status",
        )
        return Response({
            "status": True,
            "data": list(party_masters)
        })

    def post(self, request):
        data = request.data
        party_master = PartyMaster.objects.create(
            vendor_type=data.get("vendor_type"),
            name=data.get("name"),
            contact_person=data.get("contact_person"),
            phone=data.get("phone"),
            email=data.get("email"),
            gst_number=data.get("gst_number"),
            pan_number=data.get("pan_number"),
            payment_terms=data.get("payment_terms"),
            status=data.get("status"),
        )
        location = Location.objects.create(
            parent=party_master,
            country=data.get("country"),
            state=data.get("state"),
            city=data.get("city"),
            address=data.get("address"),
            zip_code=data.get("zip_code"),
        )
        party_master.save()

        category_id = data.get("category_id")
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            party_master.category = category
            party_master.save()

        return Response({
            "status": True,
            "message": "Party Master created successfully",
            "data": {
                "id": party_master.id,
                "name": party_master.name
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