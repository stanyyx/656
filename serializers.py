from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from advertisements.models import Advertisement


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', )
        read_only_fields = ['creator']

    def update(self, instance, validated_data):

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)

        instance.save()
        return instance

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        print(data.get('status', None))

        if data.get('status') == 'OPEN' and self.context['request'].method == 'POST':
            if Advertisement.objects.filter(status='OPEN', creator=self.context["request"].user).count() >= 10:
                raise ValidationError('Count adv status=OPEN 10')

        if data.get('status') == 'OPEN' and self.context['request'].method == 'PATCH':
            if Advertisement.objects.filter(status='OPEN', creator=self.context["request"].user).count() >= 10:
                raise ValidationError('Count adv status=OPEN 10')

        # if data.get('status', None) == 'OPEN':
        #     if Advertisement.objects.filter(status='OPEN', creator=self.context["request"].user).count() >= 10:
        #         raise ValidationError('Count adv status=OPEN 10')
        # elif not data.get('status', None):
        #     if Advertisement.objects.filter(status='OPEN', creator=self.context["request"].user).count() >= 10:
        #         raise ValidationError('Count adv status=OPEN 10')

        return data
