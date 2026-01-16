from rest_framework import serializers
from dashboards.super_admin.models.clients import SlabRate
class SlabRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SlabRate
        fields = "__all__"

    def validate(self, data):
        billing_mode = data.get("billing_mode")
        price_type = data.get("price_type")
        min_qty = data.get("min_qty")
        max_qty = data.get("max_qty")
        months = data.get("months")

        if billing_mode == "per_duty_slip":
            if not price_type:
                raise serializers.ValidationError({
                    "price_type": "Price type is required for per duty slip"
                })
            if min_qty is None or max_qty is None:
                raise serializers.ValidationError({
                    "min_qty": "Min & Max quantity required for per duty slip"
                })

        elif billing_mode == "flat":
            if not months:
                raise serializers.ValidationError({
                    "months": "Months are required for flat billing"
                })

        else:
            if not price_type:
                raise serializers.ValidationError({
                    "price_type": "Price type is required"
                })

        return data
