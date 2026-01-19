from django.urls import path
from .branch_create_api import BranchCreateAPI
from .branch_list_api import BranchDetailAPI, BranchListAPI
from .branch_permission_api import BranchPermissionAPI
from .branch_sidebar_api import BranchSidebarAPI

urlpatterns = [
    path("branches/create", BranchCreateAPI.as_view()),
    path("branches", BranchListAPI.as_view()),
    path("branches/<int:pk>", BranchDetailAPI.as_view()),
    path("branches/permissions", BranchPermissionAPI.as_view()),
    path("branches/<int:branch_id>/sidebar/<int:user_id>", BranchSidebarAPI.as_view()),
]
