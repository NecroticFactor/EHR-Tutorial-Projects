import requests
import json
from datetime import date
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import *
from .external_api import FHIR_END_POINT_API
from .formatter import ConvertToFHIR


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class PatientListCreate(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        response = requests.get(FHIR_END_POINT_API)

        if response.status_code == 200:
            return Response(response.json())
        else:
            return Response(
                {"error": "Failed to fetch patient resource"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def perform_create(self, serializer):
        converter = ConvertToFHIR()
        fhir_patient_data = converter.patient_resource(serializer.validated_data)

        # Convert date fields to string (ISO format)
        for key, value in fhir_patient_data.items():
            if isinstance(value, date):
                fhir_patient_data[key] = value.isoformat()

        response = requests.post(FHIR_END_POINT_API, json=fhir_patient_data)

        if response.status_code == 201:
            return Response(response.json(), status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"error": "Failed to create resource"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            fhir_response = self.perform_create(serializer)
            return fhir_response
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientDetailView(APIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        patient_id = kwargs.get("id")

        response = requests.get(f"{FHIR_END_POINT_API}/{patient_id}")

        if response.status_code == 200:
            return Response(response.json())
        else:
            return Response(
                {"error": "Patient not found in FHIR API"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request, *args, **kwargs):

        patient_id = kwargs.get("id")
        converter = ConvertToFHIR()
        fhir_patient_data = converter.patient_resource(request.data)

        # Convert date fields to string (ISO format)
        for key, value in fhir_patient_data.items():
            if isinstance(value, date):
                fhir_patient_data[key] = value.isoformat()

        response = requests.put(
            f"{FHIR_END_POINT_API}/{patient_id}", json=fhir_patient_data
        )

        if response.status_code == 200:
            return Response(response.json())
        else:
            return Response(
                {"error": "Failed to update patient on FHIR API"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, *args, **kwargs):
        patient_id = kwargs.get("id")
        if not patient_id:
            return Response(
                {"error": "Patient ID is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        response = requests.delete(f"{FHIR_END_POINT_API}/{patient_id}")

        if response.status_code == 204:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"error": "Failed to delete patient from FHIR API"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PatientSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query_name = request.query_params.get("name", "")
        query_telecom = request.query_params.get("telecom", "")
        fhir_search = f"{FHIR_END_POINT_API}?name:contains={query_name}"
        if query_telecom:
            fhir_search += f"&telecom:contains={query_telecom}"
        response = requests.get(fhir_search)

        if response.status_code == 200:
            fhir_data = response.json()

            return Response(fhir_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Error fetching data from FHIR server"},
                status=status.HTTP_400_BAD_REQUEST,
            )
