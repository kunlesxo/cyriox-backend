from django.http import JsonResponse

def notification_view(request):
    return JsonResponse({"message": "Notification API is working!"})
