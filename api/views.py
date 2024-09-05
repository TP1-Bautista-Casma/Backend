from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import ColorblindImageSerializer
from .algorithms import adapt_colors_for_anomalous_trichromat, adapt_colors_for_achromatic, adapt_colors_for_dichromatic
from rest_framework.parsers import MultiPartParser, FormParser

@api_view(['POST'])
@permission_classes([AllowAny])  # Permitir acceso sin autenticación
def upload_image(request):
    if request.method == 'POST':
        serializer = ColorblindImageSerializer(data=request.data)
        if serializer.is_valid():
            image_instance = serializer.save()  # Guardar la imagen sin necesidad de un usuario
            type_ = request.data.get('type')
            subtype = request.data.get('subtype')

            try:
                if type_ == 'anomalous_trichromatic':
                    adapt_colors_for_anomalous_trichromat(image_instance.image.path, subtype)
                    # return Response({"error": "Tipo de daltonismo y algoritmo aplicado"});
                elif type_ == 'dichromatic':
                    adapt_colors_for_dichromatic(image_instance.image.path, subtype)
                elif type_ == 'achromatic':
                    adapt_colors_for_achromatic(image_instance.image.path)
                else:
                    return Response({"error": "Tipo de daltonismo no reconocido"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": f"Error al recolorizar la imagen: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Devolver la URL de la imagen procesada
            return Response({
                'id': image_instance.id,
                'image': request.build_absolute_uri(image_instance.image.url),
                'type': image_instance.type,
                'subtype': image_instance.subtype,
                'uploaded_at': image_instance.uploaded_at,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"error": "Se esperaba una solicitud POST"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)