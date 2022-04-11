from rest_framework import serializers
from .models import Post,Profile

class Postserializer(serializers.ModelSerializer):
    class Meta:
        model =Post
        fields =('title','description','url','photo','upload_date','technologies_used','user')

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model =Profile
        fields =('user','bio','name','profile_pic','phone_number')        