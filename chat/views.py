from django.shortcuts import render


def index(request):
    contact_id = request.GET.get("contact_id", "Anonymous")
    print(request.user)
    return render(
        request,
        "chat/index.html",
        {"contact_id": contact_id, "current_user": request.user},
    )
