from rest_framework.parsers import MultiPartParser, FormParser
from .models import Message, FileUpload
from .serializers import MessageSerializer, FileUploadSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        files = FileUpload.objects.all()
        serializer = FileUploadSerializer(files, many=True)
        return Response(serializer.data)

class FileDeleteView(APIView):
    def delete(self, request, file_id, *args, **kwargs):
        try:
            file_obj = FileUpload.objects.get(id=file_id)
            file_obj.delete()
            return Response({"message": "File deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except FileUpload.DoesNotExist:
            raise Http404("File not found")

class MessageListCreateView(generics.ListCreateAPIView):
    queryset = Message.objects.all().order_by('-timestamp')
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

