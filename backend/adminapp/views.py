from random import randint

from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password
from .serializer import UserSerializer, AdminUserSerializer
from .models import AdminUser, User, OtpTemp
from django.db import transaction
from rest_framework.permissions import BasePermission
from datetime import datetime, timedelta
from threading import Thread
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

EMAIL_HOST_USER = "cuitutorial01@gmail.com"


def send_mail_func(subject, template_name, context, from_email, to_email):
    html_content = render_to_string(template_name=template_name, context=context)
    text_content = render_to_string(template_name=template_name, context=context)
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.mixed_subtype = 'related'
    msg.send()


# Create your views here.

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == "admin":
            return True


@api_view(['GET'])
def getsomething(request):
    return Response('Hell0')


class login(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        email = request.data['email']
        password = request.data["password"]
        user = authenticate(email=email, password=password)
        if user:
            tokens = get_tokens_for_user(user)
            if user.is_staff and user.is_active:
                user_data = UserSerializer(user).data
                user_data['isSuperAdmin'] = True
            elif user.role == "admin" and user.is_active:
                user_data = AdminUserSerializer(user.adminuser).data
                user_data['isSuperAdmin'] = False

            user_data['accessToken'] = tokens['accessToken']
            user_data['refresh'] = tokens['refresh']
            user_data['role'] = user.role
            return Response(user_data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "user with this credential doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'accessToken': str(refresh.access_token),
    }


class AdminUserView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = AdminUser.objects.all()
    serializer_class = AdminUserSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        if request.user.is_staff:
            data = request.data
            data['role'] = "admin"
            data['isSuperAdmin'] = True
            data["password"] = "12345678"
            check_user = User.objects.filter(email=data['email']).first()
            if check_user:
                return Response({
                    "message": "User has been already there"
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                user = UserSerializer(data=data)
                if user.is_valid(raise_exception=True):
                    user = user.save()
                    user.set_password(data['password'])
                    user.save()
                    data['user'] = user.id
                    user_profie = AdminUserSerializer(data=data)
                    if user_profie.is_valid(raise_exception=True):
                        user_profie.save()
                        ctx = {
                            'link': 'https://irsa.edu.pk/forget-password'
                        }
                        subject = 'Welcome to IRSA'
                        thread = Thread(target=send_mail_func,
                                        args=(
                                            subject, 'admin_welcome_email.html', ctx, EMAIL_HOST_USER, [data["email"]]))
                        thread.start()

                        return Response({"msg": "Admin has been created Successfully"}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({
                            'message': user_profie.errors
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({
                        'message': user.errors
                    }, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({
                "message": "only Super Admin can create this user!"
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        var = request.GET.get('pk')
        if 'email' in request.data:
            return Response({"msg": "You can not update the email"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if var:
                partial = kwargs.pop('partial', True)
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return Response({'msg': "Your profile has been updated successfully"}, status=status.HTTP_200_OK)

            else:
                if 'email' in request.data:
                    return Response({"msg": "You can not update the email"}, status=status.HTTP_400_BAD_REQUEST)

                partial = kwargs.pop('partial', True)
                instance = self.request.user
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return Response({'msg': "Your profile has been updated successfully"}, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        if request.user.is_staff:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"msg": "only super user can access this information"}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_staff:
            instance.user.delete()
            return Response({"msg": "user has been deleted successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"msg": "only super admin can delete or destroy the user"},
                            status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        user = self.request.user
        serializer = AdminUserSerializer(user.adminuser).data
        return Response(serializer)

    def get_admin_profile(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user).data
        return Response(serializer)


class ForgetResetPasswordView(viewsets.ModelViewSet):

    @staticmethod
    @transaction.atomic
    def forgetPassword(request):
        email = request.data.get('email')
        if email:
            check_email = User.objects.filter(email=email).first()
            if check_email:
                otp_value = randint(100000, 999999)

                otp, created = OtpTemp.objects.get_or_create(user=check_email)
                otp.generated_time = datetime.now() + timedelta(hours=2)
                otp.otp = otp_value
                otp.save()
                ctx = {
                    'otp': otp_value
                }
                subject = "Reset password mail"
                thread = Thread(target=send_mail_func,
                                args=(subject, 'forget_password.html', ctx, EMAIL_HOST_USER, [check_email.email]))
                thread.start()
                return Response({
                    "message": "Check Your mail to reset your Password"
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "message": "user with this mail does not exist"
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "message": "You have to provide Your Email in order to reset password"
            }, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def resetPassword(request):
        otp_value = request.data.get('otp')
        password = request.data.get('password')
        if len(password) < 8:
            return Response({
                "Message": "Password should be minimum of length 8"
            }, status.HTTP_400_BAD_REQUEST)

        if otp_value:
            if password:
                check_otp = OtpTemp.objects.filter(otp=otp_value).first()
                if check_otp:
                    check_otp.user.set_password(password)
                    check_otp.user.is_active = True
                    check_otp.user.save()
                    return Response({
                        "message": "password has been reset successfully"
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "message": "OTP doesn't match"
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "message": "Password is not been provided"
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "message": "OTP is not been provided"
            }, status=status.HTTP_400_BAD_REQUEST)
