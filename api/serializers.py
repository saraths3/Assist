from rest_framework import serializers

class FileProcessSerializer(serializers.Serializer):
    file_path = serializers.CharField(max_length=500, required=False, default="unknown.py")
    content = serializers.CharField()
    flag = serializers.CharField(max_length=50, required=False, default="fix")