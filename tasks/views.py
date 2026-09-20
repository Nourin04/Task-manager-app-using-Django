from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Task
from .serializers import TaskSerializer

def hello(request):
    return JsonResponse({
        "message": "Hello from Django!",
        "method": request.method
    })


def task_list(request):
    tasks = Task.objects.all()

    data = []

    for task in tasks:
        data.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed
        })

    return JsonResponse(data, safe=False)

@api_view(['GET'])
def task_list_api(request):
    tasks = Task.objects.all()

    serializer = TaskSerializer(tasks, many=True)

    return Response(serializer.data)