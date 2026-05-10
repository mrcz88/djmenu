from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
user = User.objects.get(username = "Mark")
token = Token.objects.get(user=user)
print(token.key)