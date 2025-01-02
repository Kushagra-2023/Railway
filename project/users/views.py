from django.shortcuts import render
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Token
from .serializers import *
from django.conf import settings
from datetime import datetime, timedelta
import hashlib
import uuid
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


SALT = "8b4f6b2cc1868d75ef79e5cfb8779c11b6a374bf0fce05b485581bf4e1e25b96c8c2855015de8449"
URL = "http://localhost:3000"


# def mail_template(content, button_url, button_text):
#     return f"""<!DOCTYPE html>
#             <html>
#             <body style="text-align: center; font-family: "Verdana", serif; color: #000;">
#                 <div style="max-width: 600px; margin: 10px; background-color: #fafafa; padding: 25px; border-radius: 20px;">
#                 <p style="text-align: left;">{content}</p>
#                 <a href="{button_url}" target="_blank">
#                     <button style="background-color: #444394; border: 0; width: 200px; height: 30px; border-radius: 6px; color: #fff;">{button_text}</button>
#                 </a>
#                 <p style="text-align: left;">
#                     If you are unable to click the above button, copy paste the below URL into your address bar
#                 </p>
#                 <a href="{button_url}" target="_blank">
#                     <p style="margin: 0px; text-align: left; font-size: 10px; text-decoration: none;">{button_url}</p>
#                 </a>
#                 </div>
#             </body>
#             </html>"""


class RegistrationView(APIView):
    def post(self, request, format=None):
        request.data["password"] = make_password(
            password=request.data["password"], salt=SALT
        )
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "You are now registered on our website!"},
                status=status.HTTP_200_OK,
            )
        else:
            error_msg = ""
            for key in serializer.errors:
                error_msg += serializer.errors[key][0]
            return Response(
                {"success": False, "message": error_msg},
                status=status.HTTP_200_OK,
            )
        
from rest_framework_simplejwt.tokens import RefreshToken

class LoginView(APIView):
    def post(self, request, format=None):
        username = request.data["username"]
        password = request.data["password"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "User not found!",
                },
                status=status.HTTP_404_NOT_FOUND,  
            )

        if not check_password(password, user.password):
            return Response(
                {
                    "success": False,
                    "message": "Invalid login credentials!",
                },
                status=status.HTTP_401_UNAUTHORIZED,  
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response(
            {
                "success": True,
                "message": "You are now logged in!",
                "access_token": access_token,
                "refresh_token": refresh_token,  # Return both tokens
                "user_id": user.id,
            },
            status=status.HTTP_200_OK,
        )



# class LoginView(APIView):
#     def post(self, request, format=None):
#         username = request.data["username"]
#         password = request.data["password"]
        
#         try:
#             # Retrieve the user object by username (id)
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             return Response(
#                 {
#                     "success": False,
#                     "message": "User not found!",
#                 },
#                 status=status.HTTP_404_NOT_FOUND,  # Return 404 if user is not found
#             )

#         # Compare the provided password with the stored hashed password
#         if not check_password(password, user.password):
#             return Response(
#                 {
#                     "success": False,
#                     "message": "Invalid login credentials!",
#                 },
#                 status=status.HTTP_401_UNAUTHORIZED,  # Unauthorized if password doesn't match
#             )

#         return Response(
#             {
#                 "success": True,
#                 "message": "You are now logged in!",
#                 "user_id": user.id
#             },
#             status=status.HTTP_200_OK,
#         )
    
# @method_decorator(csrf_exempt, name='dispatch')
# class PasswordChangeView(APIView):
#     def post(self, request):
#         user_id = request.data["user_id"]    
#         password=request.data["password"]
#         new_password = make_password(
#             password=request.data["new_password"], salt=SALT
#         )
#         try:
#             user = User.objects.get(id = user_id)
#         except User.DoesNotExist:
#             return Response(
#                 {
#                     "success": False,
#                     "message": "User not found!",
#                 },
#                 status=status.HTTP_404_NOT_FOUND,  # Return 404 if user is not found
#             )
        
#         if not check_password(password, user.password):
#             return Response(
#                 {
#                     "success": False,
#                     "message": "Invalid login credentials!",
#                 },
#                 status=status.HTTP_401_UNAUTHORIZED,  # Unauthorized if password doesn't match
#             )
        
#         user.password = new_password
#         user.save()

#         return Response(
#             {
#                 "success": True,
#                 "message": "Password changed successfully!"
#             },
#             status=status.HTTP_200_OK,
#         )

# class UsernameChangeView(APIView):
#     def post(self, request):
#         user_id = request.data["user_id"]    
#         password = request.data["password"]
#         new_username = request.data["new_username"]

#         try:
#             user = User.objects.get(id = user_id)
#         except User.DoesNotExist:
#             return Response(
#                 {
#                     "success": False,
#                     "message": "User not found!",
#                 },
#                 status=status.HTTP_404_NOT_FOUND,  # Return 404 if user is not found
#             )
        
#         if not check_password(password, user.password):
#             return Response(
#                 {
#                     "success": False,
#                     "message": "Invalid login credentials!",
#                 },
#                 status=status.HTTP_401_UNAUTHORIZED,  # Unauthorized if password doesn't match
#             )
        
#         user.username = new_username
#         user.save()

#         return Response(
#             {
#                 "success": True,
#                 "message": "Username changed successfully!"
#             },
#             status=status.HTTP_200_OK,
#         )

from rest_framework.permissions import IsAuthenticated

class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]  # Secure this view with JWT authentication
    
    def post(self, request):
        user = User.objects.get(id = request.data["user_id"])
        password = request.data["password"]
        new_password = make_password(request.data["new_password"], salt=SALT)

        if not check_password(password, user.password):
            return Response(
                {
                    "success": False,
                    "message": "Invalid credentials!",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user.password = new_password
        user.save()

        return Response(
            {
                "success": True,
                "message": "Password changed successfully!"
            },
            status=status.HTTP_200_OK,
        )


class UsernameChangeView(APIView):
    permission_classes = [IsAuthenticated]  # Secure this view with JWT authentication
    
    def post(self, request):
        user = User.objects.get(id = request.data["user_id"])
        password = request.data["password"]
        new_username = request.data["new_username"]

        if not check_password(password, user.password):
            return Response(
                {
                    "success": False,
                    "message": "Invalid credentials!",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user.username = new_username
        user.save()

        return Response(
            {
                "success": True,
                "message": "Username changed successfully!"
            },
            status=status.HTTP_200_OK,
        )

    
class GetInfo(APIView):
    def post(self, request):
        user_id = request.data["user_id"]

        try:
            user = User.objects.get(id = user_id)
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "User not found!",
                },
                status=status.HTTP_404_NOT_FOUND,  # Return 404 if user is not found
            )
        
        name = user.name
        username = user.username

        return Response(
            {
                "success": True,
                "name": name,
                "username": username,
                "message": "Fetching was success!"
            },
            status=status.HTTP_200_OK
        )
