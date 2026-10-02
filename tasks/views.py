from rest_framework import serializers
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Task
from .serializers import TaskSerializer

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import viewsets
from .permissions import IsOwner

from rest_framework import status

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


####################################### APIView #########################

class TaskDetailAPIView(APIView):

    def get(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)

        except Task.DoesNotExist:
            return Response(
                {"error": "Task not found"},
                status=404
            )

        serializer = TaskSerializer(task)

        return Response(serializer.data)

    def put(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)

        except Task.DoesNotExist:
            return Response(
                {"error": "Task not found"},
                status=404
            )

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

    def patch(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)

        except Task.DoesNotExist:
            return Response(
                {"error": "Task not found"},
            status=404
        )

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

    def delete(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)

        except Task.DoesNotExist:
            return Response(
                {"error": "Task not found"},
                status=404
            )

        task.delete()

        return Response(status=204)


class TaskListAPIView(APIView):

    def get(self, request):
        tasks = Task.objects.all()

        serializer = TaskSerializer(tasks, many=True)

        return Response(serializer.data)

    def post(self, request):
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

################ generics ################
class TaskListGenericAPIView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class TaskDetailGenericAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

################### ViewSets ###############
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Task.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

######### REGISTRATION API ###############

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RegisterSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "User registered successfully!"},
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

################### LOGIN API #########################
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(
        request,
        username=username,
        password=password
    )

    if user is not None:
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            "message": "Login successful!",
            "token": token.key,
            "username": user.username
        }, status=status.HTTP_200_OK)

    return Response(
        {"error": "Invalid username or password"},
        status=status.HTTP_401_UNAUTHORIZED
    )

################# FILTERING, SEARCH, ORDERING #################


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsOwner]

    filterset_fields = ['completed']
    search_fields = ['title', 'description']
    ordering_fields = ['id', 'title', 'completed']
    ordering = ['id']

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)