from django.shortcuts import render
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from .models import ChatPage
from .serializers import ChatPageSerializer


class ChatPageViewSet(
    ListModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet
):
    queryset = ChatPage.objects.select_related("contact").all()
    serializer_class = ChatPageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


def chat_page(request):
    contact_id = request.GET.get("contact_id", "Anonymous")

    return render(
        request,
        "chat/chat_page.html",
        {"contact_id": contact_id, "current_user": request.user},
    )
