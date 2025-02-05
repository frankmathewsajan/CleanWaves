from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import SensorData
from .serializers import SensorDataSerializer


@api_view(['POST'])
def receive_sensor_data(request):
    """
    Receives JSON with sensor data, validates it, and saves it.
    """
    serializer = SensorDataSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_latest_sensor_data(request):
    """
    Retrieves the latest sensor data entry.
    """
    latest_data = SensorData.objects.order_by('-timestamp').first()
    if latest_data is None:
        return Response({"detail": "No sensor data available."}, status=status.HTTP_404_NOT_FOUND)
    serializer = SensorDataSerializer(latest_data)
    return Response(serializer.data, status=status.HTTP_200_OK)
