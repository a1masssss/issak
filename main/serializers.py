from rest_framework import serializers

class FlashcardSerializer(serializers.Serializer):
    question = serializers.CharField()
    answer = serializers.CharField()


