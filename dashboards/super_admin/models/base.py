from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.forms.models import model_to_dict
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.auth import get_user_model

from config import settings

User = get_user_model()

class SoftDeleteQuerySet(models.QuerySet):
    def delete(self, user=None):
        for obj in self:
            obj.delete(user=user)
    
    def hard_delete(self):
        for obj in self:
            obj.hard_delete()


class ActiveManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)


class AllManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)

#to store the object id of deleted records for backup
class DeletedRecord(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    model_name = models.CharField(max_length=100)
    data = models.JSONField()   # FULL BACKUP
    deleted_by = models.ForeignKey( settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="deleted_records" )
    deleted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.model_name} #{self.object_id}"

#to implement soft delete functionality
class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = ActiveManager()
    all_objects = AllManager()

    class Meta:
        abstract = True

    def delete(self, user=None, *args, **kwargs):
        if self.is_deleted:
            return

        DeletedRecord.objects.create(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk,
            model_name=self.__class__.__name__,
            data=model_to_dict(self),
            deleted_by=user,
        )

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def hard_delete(self):
        # remove backup first
        DeletedRecord.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.pk,
        ).delete()
        super().delete()


class Location(SoftDeleteModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    parent = GenericForeignKey("content_type", "object_id")
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("content_type", "object_id")

    def __str__(self):
        return f"{self.city.name}, {self.state.name}, {self.country.name}"

# Base modal Category
class Category(SoftDeleteModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    cat_type=models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class PartyMaster(SoftDeleteModel):
    VENDOR_TYPE = [
        ("individual", "Individual"),
        ("company", "Company"),
        ("dealer", "Dealer/Showroom"),
        ("contractor", "Contractor"),
        ("service_provider", "Service Provider"),
    ]
    vendor_type = models.CharField(max_length=50, choices=VENDOR_TYPE, default="individual")
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    location = GenericRelation(Location)
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    pan_number = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,null=True,blank=True)
    payment_terms = models.TextField(blank=True, null=True)
    STATUS_TYPE = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_TYPE, default="active")
    created_at = models.DateTimeField(auto_now_add=True)   

    def delete(self, user=None, *args, **kwargs):
        for loc in self.location.all():
            loc.delete(user=user)
        super().delete(user=user)

    def hard_delete(self):
        for loc in self.location.all():
            loc.hard_delete()
        super().hard_delete()

    def __str__(self):
        return self.name
    


class FollowUp(SoftDeleteModel):

    FOLLOWUP_TYPES = [
        ("call", "Phone Call"),
        ("whatsapp", "WhatsApp"),
        ("email", "Email"),
        ("meeting", "Meeting"),
        ("reminder", "Reminder"),
        ("confirmation", "Confirmation"),
    ]

    # 🔹 Generic Relation
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    followup_type = models.CharField(
        max_length=20,
        choices=FOLLOWUP_TYPES
    )

    remarks = models.TextField()

    next_followup_date = models.DateField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.followup_type} - {self.content_object}"
