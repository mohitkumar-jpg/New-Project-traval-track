# dashboards/super_admin/models/hr.py
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone
from dashboards.super_admin.models.base import SoftDeleteModel





# Departments
class Department(SoftDeleteModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    name = models.CharField(max_length=150, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name



# Designations
class Designation(SoftDeleteModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    designation_name = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.designation_name




# Employee
class Employee(SoftDeleteModel):

    # ================= BASIC DETAILS =================
       # LOGIN LINK
    user = models.OneToOneField(  settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="employee_profile"  )
    branch = models.ForeignKey( "branch.Branch",on_delete=models.CASCADE,related_name="employees",null=True,blank=True)

    # ORG STRUCTURE
    department = models.ForeignKey( Department,on_delete=models.PROTECT)
    designation = models.ForeignKey(Designation,on_delete=models.PROTECT)
    employee_id = models.CharField(max_length=20,unique=True,blank=True, verbose_name="Employee ID" )
    name = models.CharField(max_length=255,verbose_name="Employee Name")
    dob = models.DateField(verbose_name="Date of Birth")
    father_name = models.CharField(max_length=255,blank=True,null=True,verbose_name="Father Name")
    mother_name = models.CharField(max_length=255,blank=True,null=True,verbose_name="Mother Name")
    upload_photo = models.ImageField(upload_to='employee_photos/',blank=True,null=True,verbose_name="Employee Photo")
    upload_employee_signature = models.ImageField(upload_to='employee_signature/',blank=True,null=True,verbose_name="Employee Signature Upload")
    joining_date = models.DateField(verbose_name="Joining Date")
    basic_salary = models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Basic Salary")
    about = models.TextField(blank=True,null=True,verbose_name="About Employee")
    email = models.EmailField(unique=True,verbose_name="Email Id")

    # ================= ADDRESS DETAILS =================
    current_address = models.TextField(verbose_name="Current Address",blank=True,null=True, )
    permanent_address = models.TextField(verbose_name="Permanent Address",blank=True,null=True, )


    # ================= CONTACT DETAILS =================
    contact_number = models.CharField(max_length=15,blank=True,null=True,verbose_name="Primary Contact Number" )
    alternate_contact_number = models.CharField(max_length=15,blank=True,null=True,verbose_name="Alternate / Emergency Contact Number" )
    marital_status = models.CharField(max_length=10,
        choices=[
            ('married', 'Married'),
            ('unmarried', 'Unmarried')
        ],blank=True,
        null=True,
        default='unmarried',
        verbose_name="Marital Status"
    )

    # ================= GENDER =================
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]
    gender = models.CharField(max_length=6,choices=GENDER_CHOICES,verbose_name="Gender")

    # ================= OFFER LETTER =================
    
    offer_letter_number = models.CharField(max_length=20,unique=True,blank=True,null=True,verbose_name="Offer Letter Number")
    offer_letter_file = models.FileField(upload_to='employee_docs/offer_letters/',blank=True,null=True,verbose_name="Offer Letter Upload")


    # ================= DOCUMENTS =================
    pan_number = models.CharField(max_length=15,unique=True,blank=True,null=True,verbose_name="PAN Number")
    pan_upload = models.ImageField(upload_to='employee_docs/pan/',blank=True,null=True,verbose_name="PAN Card Upload")
    passport_number = models.CharField(max_length=15,unique=True,blank=True,null=True,verbose_name="Passport Number")
    aadhar_card_no = models.CharField(max_length=12,unique=True,blank=True,null=True,verbose_name="Aadhar Number")
    aadhar_card_front = models.ImageField(upload_to='employee_docs/aadhar_front/',blank=True,null=True,verbose_name="Aadhar Front")
    aadhar_card_back = models.ImageField(upload_to='employee_docs/aadhar_back/',blank=True,null=True,verbose_name="Aadhar Back")

    # ================= EDUCATION =================
    highest_qualification = models.CharField(max_length=255,blank=True,null=True,verbose_name="Highest Qualification")
    year_of_passing = models.CharField(max_length=4,blank=True,null=True,verbose_name="Year of Passing")
    board_name = models.CharField(max_length=255,blank=True,null=True,verbose_name="Board / University")

    # ================= EXPERIENCE =================
    period = models.CharField(max_length=255,blank=True,null=True,verbose_name="Experience Period")
    reference_name = models.CharField(max_length=255,blank=True,null=True,verbose_name="Reference Name")
    reference_number = models.CharField(max_length=20,blank=True,null=True,verbose_name="Reference Contact Number")
    three_year_other_company_details = models.TextField(blank=True,null=True,verbose_name="Last 3 Years Company Details")
    previous_company_name = models.CharField(max_length=255,blank=True,null=True,verbose_name="Previous Company Name")
    previous_company_position = models.CharField(max_length=255,blank=True,null=True,verbose_name="Previous Position")

    # ================= BANK DETAILS =================
    uan_no = models.CharField(max_length=20,blank=True,null=True,verbose_name="UAN Number")
    pf_no = models.CharField(max_length=20,blank=True,null=True,verbose_name="PF Number")
    ifsc_code = models.CharField(max_length=11,blank=True,null=True,verbose_name="IFSC Code")
    branch_name = models.CharField(max_length=255,blank=True,null=True,verbose_name="Bank Branch Name")
    bank_name = models.CharField(max_length=255,blank=True, null=True,verbose_name="Bank Name")
    bank_account_no = models.CharField(max_length=50,blank=True,null=True,verbose_name="Bank Account Number")

    # ================= STATUS =================
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on-leave', 'On Leave')
    ]

    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='Active',verbose_name="Employment Status")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="Created At")

    # ================= STRING =================
    def __str__(self):
        return f"{self.name} ({self.employee_id})"

    # ================= AUTO EMPLOYEE ID =================
    def _generate_employee_id(self):
        """
        First letter of name + 4 digit running number
        Example: M0001, M0002
        """
        prefix = self.name[0].upper() if self.name else "E"

        last_emp = Employee.objects.filter(
            employee_id__startswith=prefix
        ).order_by("-employee_id").first()

        if last_emp and last_emp.employee_id[1:].isdigit():
            new_number = int(last_emp.employee_id[1:]) + 1
        else:
            new_number = 1

        return f"{prefix}{new_number:04d}"

    def save(self, *args, **kwargs):
        if not self.employee_id:
            self.employee_id = self._generate_employee_id()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        permissions = [
            ("view_employee_salary", "Can view employee salary"),
            ("edit_employee_bank", "Can edit bank details"),
            ("upload_employee_docs", "Can upload employee documents"),
        ]





class SalarySlip(SoftDeleteModel):
    employee = models.ForeignKey("Employee",on_delete=models.CASCADE,related_name="salary_slips")

    # SINGLE DATE (Salary Period Date)
    salary_date = models.DateField(help_text="Salary month reference date")
    generated_on = models.DateTimeField(default=timezone.now)

    # ================= GROSS SALARY =================
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total gross salary")

    # ================= EARNINGS =================
    basic = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2)
    da = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    total_earnings = models.DecimalField(max_digits=12, decimal_places=2)

    # ================= DEDUCTIONS =================
    pf = models.DecimalField(max_digits=10, decimal_places=2)
    esi = models.DecimalField(max_digits=10, decimal_places=2)
    professional_tax = models.DecimalField(max_digits=10, decimal_places=2)
    tds = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    leave_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # ADVANCE AUTO DEDUCTION
    advance_deduction = models.DecimalField(max_digits=10,decimal_places=2,default=Decimal("0.00"))
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # duplicate salary for same month
        unique_together = ("employee", "salary_date")
        ordering = ["-salary_date"]

    def __str__(self):
        return f"{self.employee.name} - {self.salary_date.strftime('%B %Y')}"

    def save(self, *args, **kwargs):
        # Calculate components based on gross_salary
        if self.gross_salary:
            # Basic = 50% of Gross
            self.basic = self.gross_salary * Decimal('0.5')
            
            # HRA = 50% of Basic
            self.hra = self.basic * Decimal('0.5')
            
            # Allowance = Gross - HRA - Basic
            self.allowance = self.gross_salary - self.hra - self.basic
            
            # PF: if Basic >= 15000, fixed 1800, else 12% of Basic
            if self.basic >= Decimal('15000'):
                self.pf = Decimal('1800')
            else:
                self.pf = self.basic * Decimal('0.12')
            
            # ESI: if Gross <= 21000, 0.75% of Gross, else 0
            if self.gross_salary <= Decimal('21000'):
                self.esi = self.gross_salary * Decimal('0.0075')
            else:
                self.esi = Decimal('0')
            
            # Total Earnings = Basic + HRA + DA + Allowance + Overtime
            self.total_earnings = self.basic + self.hra + self.da + self.allowance + self.overtime
            
            # Total Deductions = PF + ESI + Professional Tax + TDS + Leave Deduction + Advance Deduction
            self.total_deductions = self.pf + self.esi + self.professional_tax + self.tds + self.leave_deduction + self.advance_deduction
            
            # Net Salary = Total Earnings - Total Deductions
            self.net_salary = self.total_earnings - self.total_deductions
        
        super().save(*args, **kwargs)
        
class Attendance(SoftDeleteModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    check_in = models.TimeField(blank=True, null=True)
    check_out = models.TimeField(blank=True, null=True) 
    status = models.CharField(
        max_length=20,
        choices=[
            ("present", "Present"),
            ("absent", "Absent"),
            ("halfday", "Halfday"),
            ("leave", "Leave"),
        ]
    )
    # 👇 yeh naya field – yahin leave reason / OT / comment le sakte ho
    note = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.employee.name} - {self.status}"

    class Meta:
        unique_together = ("date", "employee")


# advance 
class AdvanceRequest(SoftDeleteModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("closed", "Closed"),
    ]

    TERMS_CHOICES = [
        ("3", "3 Months"),
        ("6", "6 Months"),
        ("12", "12 Months"),
        ("custom", "Custom"),
    ]

    employee = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="advances"
    )

    branch = models.ForeignKey(
    "branch.Branch",
    on_delete=models.PROTECT,
    related_name="advances",
    null=True,
    blank=True
    )


    approver = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )
    
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    purpose = models.CharField(max_length=255)
    repayment_terms = models.CharField(
        max_length=10,
        choices=TERMS_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # ================= CALCULATED =================
    @property
    def total_installment_amount(self):
        return sum(
            (inst.amount for inst in self.installments.all()),
            Decimal("0.00")
        )

    @property
    def outstanding_amount(self):
        return self.amount - self.total_installment_amount
    
    def __str__(self):
        return f"Advance #{self.id} - {self.employee.name}"
    


class AdvanceInstallment(SoftDeleteModel):
    advance = models.ForeignKey(
        AdvanceRequest,
        on_delete=models.CASCADE,
        related_name="installments"
    )

    installment_no = models.PositiveIntegerField()
    due_date = models.DateField()

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payslip_deduction = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.advance} - Installment {self.installment_no}"
