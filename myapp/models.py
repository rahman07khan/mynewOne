from django.contrib.auth.models import AbstractUser
from django.db import models

class MasterRole(models.Model):
    role = models.CharField(max_length=50)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null = True)
    created_by = models.IntegerField(null=True, editable=False)
    modified_by = models.IntegerField(null=True, editable=False)

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    mobile_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    role = models.ForeignKey(MasterRole, on_delete=models.CASCADE)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    modified_at = models.DateTimeField(auto_now=True,null=True)
    created_by = models.ForeignKey(MasterRole, on_delete=models.SET_NULL, null=True, related_name='created_role')
    modified_by = models.ForeignKey(MasterRole, on_delete=models.SET_NULL, null=True, related_name='modified_role')


class Categories(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    modified_at = models.DateTimeField(auto_now=True,null=True)
    created_by = models.ForeignKey(CustomUser,on_delete=models.SET_NULL, null=True, related_name='created_category')
    modified_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='modified_category')


class Product(models.Model):
    model_name = models.CharField(max_length=30, unique=True)
    quantity = models.IntegerField()
    each_price = models.FloatField()
    total_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    modified_at = models.DateTimeField(auto_now=True,null=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    created_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_products')
    modified_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='modified_products')

    

class Bought(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    modified_at = models.DateTimeField(auto_now=True,null=True)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='created_user')
    modified_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, related_name='modified_user')
