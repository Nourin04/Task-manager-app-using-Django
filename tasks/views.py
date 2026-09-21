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



@api_view(['GET', 'POST'])
def task_list_api(request):
    if request.method == 'GET':
        tasks = Task.objects.all()

        serializer = TaskSerializer(tasks, many=True)

        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TaskSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=201
            )

        return Response(
            serializer.errors,
            status=400
        )



@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def task_detail_api(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response(
            {"error": "Task not found"},
            status=404
        )

    if request.method == 'GET':
        serializer = TaskSerializer(task)

        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = TaskSerializer(
            task,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=400
        )

    elif request.method == 'PATCH':
        serializer = TaskSerializer(
            task,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=400
        )

    elif request.method == 'DELETE':
        task.delete()

        return Response(status=204)