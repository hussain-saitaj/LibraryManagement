from configparser import ExtendedInterpolation
from posixpath import basename
from pyexpat import model
from sre_parse import CATEGORIES
from telnetlib import STATUS
from tkinter import CASCADE
from unicodedata import category
from django.db import models
from django.contrib.auth.models import User

#Create your models here.
class CustomUser(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    email=models.EmailField(max_length=100,blank=True)
    uname=models.CharField(max_length=50,blank=True)
    phone_no=models.CharField(max_length=10,blank=True)
    address=models.TextField(blank=True)
    ROLES=[
        ("staff","staff"),
        ("publisher","publisher"),
        ("reader","reader"),
    ]
    role=models.CharField(max_length=10,choices=ROLES,default="reader",blank=True)
    fine=models.IntegerField(default=0)
    isBan=models.BooleanField(default=False,blank=True)

    def __str__(self):
        return self.user.username

class Book(models.Model):
    isbn=models.CharField(max_length=10,blank=True)
    title=models.CharField(max_length=10,blank=True)
    price=models.CharField(max_length=10,blank=True)
    CATEGORIES=[
        ("general","general"),
        ("novel","novel"),
        ("story","story"),
    ]
    category=models.CharField(max_length=10,choices=CATEGORIES,default="novel",blank=True)
    edition=models.CharField(max_length=10,blank=True)
    publisher_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    details=models.CharField(max_length=100,blank=True)
    quantity=models.IntegerField(default=20)
    readers=models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)

class Issued_details(models.Model):
    issued_date=models.DateField(auto_now_add=True)
    return_date=models.DateField()
    book_id=models.ForeignKey(Book,on_delete=models.CASCADE)
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    returned=models.BooleanField(default=False,blank=True)
    fine=models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)


#cahnge here
class Request(models.Model):
    user_id=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    STATUS=[
        ("approved","approved"),
        ("notapproved","notapproved"),
    ]
    status=models.CharField(max_length=15,choices=STATUS,default="notapproved",blank=True)
    register_date=models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

class Transaction(models.Model):
    book_id=models.ForeignKey(Book,on_delete=models.CASCADE)
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    transaction_date=models.DateField(auto_now_add=True)
    total_amount=models.IntegerField(default=0)
    amount_paid=models.IntegerField(default=0)


    def __str__(self):
        return str(self.id)

class History(models.Model):
    transaction_id=models.ForeignKey(Transaction,on_delete=models.CASCADE)
    amount_paid=models.IntegerField(default=0)
    paid_date=models.DateField(auto_now_add=True)

    




