from rest_framework import serializers
from dashboards.super_admin.models.hr import Employee
import base64

class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    designation_name = serializers.CharField(source='designation.designation_name', read_only=True)
    upload_photo_binary = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = "__all__"
        extra_fields = ['department_name', 'designation_name', 'upload_photo_binary']

    def validate_email(self, value):
        qs = Employee.objects.filter(email=value)

        # UPDATE case me current record ignore karo
        if self.instance:
            qs = qs.exclude(id=self.instance.id)

        if qs.exists():
            raise serializers.ValidationError(
                "Employee with this email already exists"
            )

        return value

    def validate(self, data):
        required_fields = [
            "name",
            "email",
            "department",
            "designation",
            "dob",
            "joining_date",
            "gender",
            "basic_salary",
        ]

        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError({
                    field: f"{field} is required"
                })

        return data

    def get_upload_photo_binary(self, obj):
        if obj.upload_photo and hasattr(obj.upload_photo, 'path'):
            try:
                with open(obj.upload_photo.path, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            except Exception:
                return None
        return None