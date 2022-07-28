from django.contrib import admin

from .models import *
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Book)
admin.site.register(Issued_details)
admin.site.register(Request)
