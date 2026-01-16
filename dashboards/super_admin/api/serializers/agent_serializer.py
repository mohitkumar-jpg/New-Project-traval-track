# serializers/agent_serializer.py
from rest_framework import serializers

from dashboards.super_admin.models.agent import Agent


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = "__all__"
