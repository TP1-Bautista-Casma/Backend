from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, ColorblindImageSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, ColorblindImage
from .algorithms import adapt_colors_for_anomalous_trichromat, adapt_colors_for_achromatic, adapt_colors_for_dichromatic

@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Crea un usuario usando el UserManager personalizado
        user = User.objects.create_user(email=email, password=password)
        refresh = RefreshToken.for_user(user)
        token = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        # Puedes personalizar el retorno del token según tus necesidades
        return Response ( {
            'message': 'Usuario registrado exitosamente.',
            'user': serializer.data,
            'token': token,
        })
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    user = authenticate(request, email=email, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        user_serializer = UserSerializer(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_serializer.data
        })
    else:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
""" @api_view(['POST'])
@permission_classes([IsAuthenticated]) # No se requiere autenticación
def upload_image(request):
    if request.method == 'POST':
        serializer = ColorblindImageSerializer(data=request.data)
        if serializer.is_valid():
            # Guarda la imagen asociándola al usuario actual si lo deseas
            image_instance = serializer.save(user=request.user)
            #user=request.user
            # Obtiene el tipo y subtipo de daltonismo del request
            type_ = request.data.get('type')
            subtype = request.data.get('subtype')

            # Aplica el algoritmo de recolorización según el tipo de daltonismo
            try:
                adapt_colors_for_anomalous_trichromat(image_instance.image.path, type_)
            except Exception as e:
                # Manejo de errores si falla el proceso de recolorización
                return Response({"error": f"Error al recolorizar la imagen: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Retorna la respuesta con los datos serializados de la imagen guardada
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Retorna los errores de validación si el serializer no es válido
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Retorna un error si la solicitud no es de tipo POST
    return Response({"error": "Se esperaba una solicitud POST"}, status=status.HTTP_405_METHOD_NOT_ALLOWED) """

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request):
    if request.method == 'POST':
        serializer = ColorblindImageSerializer(data=request.data)
        if serializer.is_valid():
            image_instance = serializer.save(user=request.user)
            type_ = request.data.get('type')
            subtype = request.data.get('subtype')

            try:
                if type_ == 'anomalous_trichromatic':
                    adapt_colors_for_anomalous_trichromat(image_instance.image.path, subtype)
                elif type_ == 'dichromatic':
                    adapt_colors_for_dichromatic(image_instance.image.path, subtype)
                elif type_ == 'achromatic':
                    adapt_colors_for_achromatic(image_instance.image.path)
                else:
                    return Response({"error": "Tipo de daltonismo no reconocido"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": f"Error al recolorizar la imagen: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"error": "Se esperaba una solicitud POST"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)