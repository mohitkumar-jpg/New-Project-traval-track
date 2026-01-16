from rest_framework import serializers
from decimal import Decimal
from dashboards.super_admin.models.gst import Quotation, FollowUp, QuotationItem



class QuotationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationItem
        fields = ["id", "description", "quantity", "rate", "amount"]
        read_only_fields = ["amount"]


class QuotationFollowUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = FollowUp
        fields = "__all__"

    def validate_quotation(self, value):
        if not Quotation.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Invalid quotation ID")
        return value



class QuotationSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True)
    followups = QuotationFollowUpSerializer(many=True, read_only=True)

    class Meta:
        model = Quotation
        fields = "__all__"
        read_only_fields = ["quotation_no", "sub_total", "grand_total"]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])

        quotation = Quotation.objects.create(**validated_data)

        sub_total = Decimal("0.00")

        for item in items_data:
            qty = Decimal(item["quantity"])
            rate = Decimal(item["rate"])
            amount = qty * rate
            sub_total += amount

            QuotationItem.objects.create(
                quotation=quotation,
                amount=amount,
                **item
            )

        quotation.sub_total = sub_total
        quotation.grand_total = sub_total
        quotation.save()

        return quotation

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if items_data is not None:
            for item in instance.items.all():
                item.delete(user=self.context["request"].user)

            sub_total = Decimal("0.00")

            for item in items_data:
                qty = Decimal(item["quantity"])
                rate = Decimal(item["rate"])
                amount = qty * rate
                sub_total += amount

                QuotationItem.objects.create(
                    quotation=instance,
                    amount=amount,
                    **item
                )

            instance.sub_total = sub_total
            instance.grand_total = sub_total

        instance.save()
        return instance
