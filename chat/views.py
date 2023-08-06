from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view()
@permission_classes([IsAuthenticated])
def index(request):
    contact_id = request.GET.get("contact_id")
    if contact_id is None:
        return Response({"detail": "Contact ID is not provided."})
    return render(request, "chat/index.html")
