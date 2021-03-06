from django.contrib.auth.models import AnonymousUser
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from course.models import Course, Category, UserCourse, Question, QuestionOption, Lecture, QuestionAnswer
from course.services import can_user_join_course
from utils.constants import ANSWER_CHOICES, ANSWER_TEXT_CHOICES


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ['id', 'name', 'is_active', 'priority']


class CategorySerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = Category
        fields = ['id', 'name', 'level', 'grade', 'course']


class JoinCourseSerializer(serializers.Serializer):
    category_id = serializers.IntegerField(required=True)
    anonymous_user = serializers.CharField(required=False, max_length=500)

    def validate(self, attrs):
        category_id = attrs['category_id']
        user = self.context['request'].user
        anonymous_user_string = attrs.get('anonymous_user', None)
        category = Category.objects.filter(id=category_id).first()

        if isinstance(user, AnonymousUser):
            if not anonymous_user_string:
                raise ValidationError('User not found')
            user = None
        attrs['user'] = user
        if not category:
            raise ValidationError('Выбранная категория не существует')

        can_user_join_course(user, category_id, anonymous_user_string)
        return attrs


class UserCourseSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = UserCourse
        fields = ('category', 'is_finished', 'score', 'note')


class QuestionSerializer(serializers.ModelSerializer):

    class QuestionOptionSerializer(serializers.ModelSerializer):
        class Meta:
            model = QuestionOption
            fields = ('id', 'option_text', 'priority')

    options = QuestionOptionSerializer(many=True)
    category = serializers.CharField(source='category.name')

    class Meta:
        model = Question
        fields = ('id', 'title', 'category', 'description', 'images', 'options')


class AnswerSubmitSerializer(serializers.Serializer):
    question = serializers.IntegerField(required=True)
    answer_option = serializers.IntegerField(required=True)
    answer_type = serializers.HiddenField(default=QuestionAnswer.TEST)

    def validate(self, attrs):
        question = attrs['question']
        answer_option = attrs['answer_option']
        category_id = self.context['category_id']

        if not Category.objects.filter(id=category_id).exists():
            raise ValidationError('Выбранный курс не существует!')

        if not Question.objects.filter(id=question).exists():
            raise ValidationError('Такой вопрос не существует!')
        elif not QuestionOption.objects.filter(question_id=question, id=answer_option).exists():
            raise ValidationError('Ответ на вопрос не существует!')

        return attrs


class MultitestAnswerSubmitSerializer(AnswerSubmitSerializer):
    answer_type = serializers.HiddenField(default=QuestionAnswer.MULTITEST)


class AnswerResultSerializer(serializers.Serializer):
    result = serializers.ChoiceField(choices=ANSWER_CHOICES)
    text = serializers.ChoiceField(choices=ANSWER_TEXT_CHOICES)


class NoteSerializer(serializers.Serializer):
    note = serializers.CharField(required=True)
    anonymous_user = serializers.CharField(required=False, max_length=500)

    def validate(self, attrs):
        category_id = self.context.get('kwargs')['category_id']
        anonymous_user = attrs.get('anonymous_user', None)
        user = self.context['request'].user
        if not user.is_authenticated and not anonymous_user:
            raise ValidationError('Вам нет доступа к лекционным материалам!')
        if user.is_authenticated and not UserCourse.objects.filter(user_id=user.id, category_id=category_id).first():
            raise ValidationError('Вы не проходите выбранную категорию!')
        elif anonymous_user and not UserCourse.objects.filter(anonymous_user=anonymous_user, category_id=category_id).first():
            raise ValidationError('Вы не проходите выбранную категорию!')
        return attrs


class LectureNoteSerializer(serializers.Serializer):
    body = serializers.CharField()


class LectureSerializer(serializers.ModelSerializer):
    note = serializers.SerializerMethodField()

    class Meta:
        model = Lecture
        fields = ('title', 'context', 'note')

    @extend_schema_field(LectureNoteSerializer)
    def get_note(self, obj):
        user_course = UserCourse.objects.filter(category_id=obj.category_id).first()
        return LectureNoteSerializer({'body': user_course.note}).data


class FinishedCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    answered_correct = serializers.SerializerMethodField('get_answered_question_number')

    class Meta:
        model = UserCourse
        fields = ('score', 'category', 'answered_correct')

    def get_answered_question_number(self, obj):
        from course.services import get_answered_question_number
        return get_answered_question_number(obj)
