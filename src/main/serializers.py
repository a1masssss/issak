from rest_framework import serializers

class FlashcardSerializer(serializers.Serializer):
    question = serializers.CharField()
    answer = serializers.CharField()


class QuestionSerializer(serializers.Serializer):
    question = serializers.CharField()
    options = serializers.ListField(
        child=serializers.CharField(), min_length=3, max_length=3
    )
    answer = serializers.CharField()

class QuizSerializer(serializers.Serializer):
    questions = QuestionSerializer(many=True)

