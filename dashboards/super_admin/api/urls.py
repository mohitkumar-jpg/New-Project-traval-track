from django.urls import path
from dashboards.super_admin.api.agents_api import AgentDetailAPI, AgentListAPI
from dashboards.super_admin.api.asset_api import AssetAPI,AssetDetailAPI, CategoryAPI, AssetDisposalAPI
from dashboards.super_admin.api.attendance_api import AttendanceAPI


from dashboards.super_admin.api.department_api import DepartmentAPI, DepartmentDetailAPI
from dashboards.super_admin.api.designation_api import DesignationAPI, DesignationDetailAPI
from dashboards.super_admin.api.employee_api import EmployeeAPI, EmployeeDetailAPI 
from dashboards.super_admin.api.expense_api import ExpenseAPI

from dashboards.super_admin.api.quotation_api import QuotationAPI, QuotationDetailAPI, QuotationFollowUpAPI
from dashboards.super_admin.api.salary_api import SalaryAPI
from dashboards.super_admin.api.deals_api import DealDetailAPI, DealListAPI
from dashboards.super_admin.api.sidebar_views import SidebarMenuAPI
from dashboards.super_admin.api.slab_rate_api import SlabRateAPI, SlabRateDetailAPI
from dashboards.super_admin.api.advance_api import AdvanceAPI
from dashboards.super_admin.api.timezones_api import TimezonesAPI
from dashboards.super_admin.api.purchase_order_api import PurchaseOrderAPI, PurchaseOrderActionAPI, PurchaseOrderUpdateAPI
from dashboards.super_admin.api.partymaster_api import PartyMasterAPI, PartyMasterDetailAPI
from dashboards.super_admin.api.grn import GRNAPI, GRNDetailAPI, GRNActionAPI, PurchaseOrderFetchAPI

from dashboards.users.api.login import LoginAPI
from dashboards.users.api.logout import LogoutAPI
from django.contrib.auth import get_user_model
User = get_user_model()

from .auth_views import (
  
    SuperAdminForgotPasswordAPI,
    SuperAdminResetPasswordAPI,
    SuperAdminProfileAPI,
)


urlpatterns = [
    path("sidebar", SidebarMenuAPI.as_view()),

    path("login/", LoginAPI.as_view(), name="super_admin_login"),
    path("logout/", LogoutAPI.as_view()),
    path("forgot-password", SuperAdminForgotPasswordAPI.as_view()),
    path("reset-password", SuperAdminResetPasswordAPI.as_view()),
    path("profile", SuperAdminProfileAPI.as_view()),

    path("slab-rates", SlabRateAPI.as_view()),
    path("slab-rates/<int:pk>", SlabRateDetailAPI.as_view()),

    path("quotations", QuotationAPI.as_view()),
    path("quotations/<int:pk>", QuotationDetailAPI.as_view()),
    path("quotations/followups", QuotationFollowUpAPI.as_view()),

    

    path("timezones", TimezonesAPI.as_view()),
    # path("branches", BranchCreateAPI.as_view()),
    # path("branches/<int:pk>", BranchAPI.as_view()),
    # path("branches", BranchListAPI.as_view()),
    # path("branch/dashboard", BranchDashboardAPI.as_view()),
    # path("staff/<str:branch_code>", AssignStaffPermissionAPI.as_view()),

    path("departments", DepartmentAPI.as_view()),
    path("departments/<int:pk>", DepartmentDetailAPI.as_view()),

    path("designations", DesignationAPI.as_view()),
    path("designations/<int:pk>", DesignationDetailAPI.as_view()),

    path("employees", EmployeeAPI.as_view()),
    path("employees/<int:pk>", EmployeeDetailAPI.as_view()),
    path("attendance", AttendanceAPI.as_view()),
    path("attendance/<int:pk>", AttendanceAPI.as_view()),
    path("salaries", SalaryAPI.as_view()),
    
    path("advances", AdvanceAPI.as_view()),
    path("advances/<int:pk>", AdvanceAPI.as_view()),
    # path("advances")
    path("categories",CategoryAPI.as_view(),name="category_list_create"),
    path("categories/<int:pk>", CategoryAPI.as_view(), name="category_update"),

    path("assets", AssetAPI.as_view(),name="asset_list_create"),
    path("assets/<int:pk>", AssetDetailAPI.as_view(),name="asset_detail_update_delete"),

    path("assets/disposal", AssetDisposalAPI.as_view()),

   
    path("party-master", PartyMasterAPI.as_view()),
    path("party-master/<int:pk>", PartyMasterDetailAPI.as_view()),

    path("expenses", ExpenseAPI.as_view()),

    path("purchase-order", PurchaseOrderAPI.as_view()),
    path("purchase-order/<int:pk>", PurchaseOrderActionAPI.as_view()),
    path("purchase-order/actions/<int:pk>", PurchaseOrderUpdateAPI.as_view()),

    path("grn", GRNAPI.as_view()),
    path("grn/purchase-fetch", PurchaseOrderFetchAPI.as_view()),
    path("grn/<int:pk>", GRNDetailAPI.as_view()),
    path("grn/actions/<int:pk>", GRNActionAPI.as_view()),

    # agents
    path("agents/", AgentListAPI.as_view()),
    path("agents/<int:pk>/", AgentDetailAPI.as_view()),

    path("deals/", DealListAPI.as_view()),
    path("deals/<int:pk>/", DealDetailAPI.as_view()),



]
