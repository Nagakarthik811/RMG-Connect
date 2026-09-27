from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Associate, Interview, Project


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']


class AssociateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skills_list = serializers.SerializerMethodField()

    class Meta:
        model = Associate
        fields = [
            'id', 'employee_id', 'name', 'email', 'phone', 'experience', 'skills', 'skills_list',
            'location', 'availability_status', 'allocation_status', 'user', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'user']

    def get_skills_list(self, obj):
        return [skill.strip() for skill in obj.skills.split(',') if skill.strip()]


class ProjectSerializer(serializers.ModelSerializer):
    required_skills_list = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'project_name', 'client', 'required_skills', 'required_skills_list',
            'minimum_experience', 'location', 'description', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_required_skills_list(self, obj):
        return [skill.strip() for skill in obj.required_skills.split(',') if skill.strip()]


class InterviewSerializer(serializers.ModelSerializer):
    associate = AssociateSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    associate_id = serializers.PrimaryKeyRelatedField(source='associate', queryset=Associate.objects.all(), write_only=True)
    project_id = serializers.PrimaryKeyRelatedField(source='project', queryset=Project.objects.all(), write_only=True)

    class Meta:
        model = Interview
        fields = [
            'id', 'associate', 'project', 'associate_id', 'project_id',
            'interview_date', 'interview_time', 'interview_type', 'status', 'remarks', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                attrs['user'] = user
                return attrs
            raise serializers.ValidationError('Invalid username or password.')
        raise serializers.ValidationError('Username and password are required.')


class AssociateCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = Associate
        fields = [
            'id', 'employee_id', 'name', 'email', 'phone', 'experience', 'skills',
            'location', 'availability_status', 'allocation_status', 'password'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password', 'Welcome123!')
        username = validated_data['employee_id'].lower()
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'employee_id': 'A login with this employee ID already exists.'})
        user = User.objects.create_user(username=username, email=validated_data['email'], password=password)
        return Associate.objects.create(user=user, **validated_data)

    def validate_experience(self, value):
        if value < 0:
            raise serializers.ValidationError('Experience cannot be negative.')
        return value


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id', 'project_name', 'client', 'required_skills', 'minimum_experience', 'location', 'description', 'status'
        ]
        read_only_fields = ['id']

    def validate_minimum_experience(self, value):
        if value < 0:
            raise serializers.ValidationError('Minimum experience cannot be negative.')
        return value
