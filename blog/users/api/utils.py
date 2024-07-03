from users.models import Token


def delete_token(user):
    user_token = Token.objects.filter(user_id=user)
    if user_token:
        user_token.first()
        user_token.delete()
