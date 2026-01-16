# api/agents_api.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from dashboards.super_admin.api.serializers.agent_serializer import AgentSerializer
from dashboards.super_admin.models.agent import Agent


class AgentListAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        agents = Agent.objects.all()
        serializer = AgentSerializer(agents, many=True)
        return Response({
            "status": True,
            "data": serializer.data
        })

    def post(self, request):
        serializer = AgentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": True,
                "message": "Agent created",
                "data": serializer.data
            }, status=201)

        return Response({
            "status": False,
            "errors": serializer.errors
        }, status=400)



class AgentDetailAPI(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        return Agent.objects.get(pk=pk)

    def get(self, request, pk):
        agent = self.get_object(pk)
        serializer = AgentSerializer(agent)
        return Response({"status": True, "data": serializer.data})

    def put(self, request, pk):
        agent = self.get_object(pk)
        serializer = AgentSerializer(agent, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "data": serializer.data})
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        agent = self.get_object(pk)
        agent.delete()
        return Response({"status": True, "message": "Deleted"})
