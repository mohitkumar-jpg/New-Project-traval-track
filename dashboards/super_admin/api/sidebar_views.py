from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

class SidebarMenuAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        BASE_URL = f"{request.scheme}://{request.get_host()}{settings.STATIC_URL}icons/"
        return Response({
            "status": True,
            "data": [
                {
                    "title": "Dashboard",
                    "icon": BASE_URL + "home.png",
                    "path": "/dashboard"
                },
                 # 🔹 CLIENTS / SALES
                {
                    "title": "Clients",
                    "icon": BASE_URL + "public-relation.png",
                    "submodules": [
                        {
                            "title": "Slab Rate List",
                            "path": "/slabs"
                        },
                        {
                            "title": "All Clients List",
                            "path": "/clients"
                        },
                        {
                            "title": "All Quotations",
                            "path": "/quotations"
                        }
                    ]
                },

                {
                    "title": "HR Management",
                    "icon": BASE_URL + "employee.png",
                    "submodules": [
                        {"title": "HR Dashboard", "path": "/hr-dashboard"},
                        {"title": "Departments", "path": "/departments"},
                        {"title": "Designations", "path": "/designations"},
                        {"title": "Employees", "path": "/employees"},
                        {"title": "Attendance", "path": "/attendance"},
                        {"title": "Loan & Advance ", "path": "/advance"},
                        {"title": "Payroll", "path": "/salary-slip"},
                        {"title": "Reports", "path": "/hr-reports"},
                    ]
                },
                {
                    "title": "Assets Management",
                    "icon": BASE_URL + "employee.png",
                    "submodules": [
                        {"title": "Asset Dashboard", "path": "/asset-dashboard"},
                        {"title": "Parties", "path": "/parties"},
                        {"title": "Purchase Order", "path": "/purchase-order"},
                        {"title": "Good Receive Note", "path": "/grn"},
                        {"title": "Bills and Purchases", "path": "/bills-purchases"},
                        {"title": "Assets ", "path": "/assets"},
                        {"title": "Scheduler", "path": "/scheduler"},
                        {"title": "Disposal", "path": "/disposal"},
                        {"title": "Reports", "path": "/asset-reports"},
                    ]
                },
                {
                    "title": "Payment Management",
                    "icon": BASE_URL + "employee.png",
                    "submodules": [
                        {"title": "Dashboard", "path": "/payment-dashboard"},
                        {"title": "Petty Cash", "path": "/petty-cash"},
                        {"title": "Payout", "path": "/payout"},
                        {"title": "Cost-Center", "path": "/cost-center"},
                    ]
                },
                # {
                #     "title": "Assets",
                #     "icon": BASE_URL + "digital-asset-management.png",
                #     "submodules": [
                #         {
                #             "title": "Assets List",
                #             "path": "/assets"
                #         }
                       
                #     ]
                # },

                {
                    "title": "Inventory",
                    "icon": BASE_URL + "checklists.png",
                    "submodules": [
                         {
                            "title": "Inventory Categories",
                            "path": "/inventory-category"
                        },
                        {
                            "title": "Inventory Items",
                            "path": "/inventories"
                        }
                    ]
                },


                {
                    "title": "Expenses",
                    "icon": BASE_URL + "expenses.png",
                    "submodules": [
                        {
                            "title": "Expense Categories",
                            "path": "/expense-category"
                        },
                        {
                            "title": "Expenses",
                            "path": "/expenses"
                        },
                       
                    ]
                },

                {
                    "title": "Settings",
                    "icon": BASE_URL + "expenses.png",
                    "submodules": [
                        {
                            "title": "Asset Categories",
                            "path": "/asset-categories"
                        },
                        {
                            "title": "Asset Models",
                            "path": "/asset-models"
                        },
                        {
                            "title": "Party Categories",
                            "path": "/party-categories"
                        },
                    ]
                },


                {
                    "title": "Branches",
                    "icon": BASE_URL + "branch.png",
                    "submodules": [
                         {
                            "title": "All Branches",
                            "path": "/branches"
                        }
                        
                       
                    ]
                },

                {
                    "title": "Agents",
                    "icon": BASE_URL + "branch.png",
                    "submodules": [
                         {
                            "title": "All Agents",
                            "path": "/agents"
                        },

                        {
                            "title": "All Deals",
                            "path": "/deals"
                        },
                        
                        
                       
                    ]
                },

            ]
        })
