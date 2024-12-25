from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class meta:
        model = User
        fields = ["username", "password", "email"]
        extra_kwargs = {"password": {"write_only": True}}


class PatientSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    gender = serializers.ChoiceField(choices=["male", "female", "other", "unknown"])
    birth_date = serializers.CharField()
    city = serializers.CharField(max_length=200, required=True)
    state = serializers.CharField(max_length=200, required=True)
    country = serializers.CharField(max_length=200, required=True)
    postalcode = serializers.CharField(max_length=20, required=True)
    phone_number = serializers.CharField(max_length=20, required=True)
    phone_number_use = serializers.ChoiceField(
        choices=["home", "work", "mobile", "other"], required=True
    )
