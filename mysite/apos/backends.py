from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class PhoneNumberBackend(ModelBackend):
   def authenticate(self, request, username=None, password=None, phone_number=None, **kwargs):
      UserModel = get_user_model()

      try:
         user = UserModel.objects.get(username=username, phone_number=phone_number)
         if user.check_password(password):
            return user
      except UserModel.DoesNotExist:
         return None
