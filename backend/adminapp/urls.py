from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenBlacklistView
from .views import AdminUserView, getsomething, login, ForgetResetPasswordView

router = DefaultRouter()

urlpatterns = [
    ####################### AUTH URLS #############################################
    path('logout', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('login', login.as_view({'post': 'create'})),
    path('forgetPassword', ForgetResetPasswordView.as_view({"post": "forgetPassword"})),
    path('resetPassword', ForgetResetPasswordView.as_view({"post": "resetPassword"})),
    #################################################################################
    path('some', getsomething, name="something"),

    ##################### ADMIN URLS ###################################################
    path('admin-auth/register', AdminUserView.as_view({'post': 'create'})),
    path('admin-auth/update', AdminUserView.as_view({'put': 'update'})),
    path('admin-auth/getalladminuser', AdminUserView.as_view({'get': 'list'})),
    path('admin-auth/deleteadmin/<int:pk>', AdminUserView.as_view({'delete': 'destroy'})),
    path('admin-auth/getme', AdminUserView.as_view({'get': 'retrieve'})),
    path('admin-auth/getadmin/<int:pk>/', AdminUserView.as_view({'get': 'get_admin_profile'})),
    #######################################################################################

]
urlpatterns += router.urls
