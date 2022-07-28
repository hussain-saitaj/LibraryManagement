from django.http import HttpResponse
from django.shortcuts import redirect
from .models import CustomUser

def unauthenticated_user(view_func):
	def wrapper_func(request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect('reader')
		else:
			return view_func(request, *args, **kwargs)

	return wrapper_func

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            group = None
            if request.user.is_staff:
                return redirect('adminPage')
            custom_user=CustomUser.objects.get(user=request.user)
            if custom_user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('staff')
        return wrapper_func
    return decorator

def staff_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        if request.user.is_staff:
            return redirect('adminPage')
        custom_user=CustomUser.objects.get(user=request.user)
        if custom_user.role == 'staff':
            return view_func(request, *args, **kwargs)
        elif  custom_user.role=="reader":
            return  redirect('reader')
        elif custom_user.role=="publisher":
            return redirect('publisher')
        

    return wrapper_function

def reader_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        if request.user.is_staff:
            return redirect('adminPage')
        custom_user=CustomUser.objects.get(user=request.user)
        if custom_user.role == 'reader':
            return view_func(request, *args, **kwargs)
        elif custom_user.role=="staff":
            return  redirect('staff')
        elif custom_user.role=="publisher":
            return redirect('publisher')
        

    return wrapper_function

def publisher_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        if request.user.is_staff:
            return redirect('adminPage')
        custom_user=CustomUser.objects.get(user=request.user)
        if custom_user.role == 'publisher':
            return view_func(request, *args, **kwargs)
        elif  custom_user.role=="reader":
            return  redirect('reader')
        elif  custom_user.role=="staff":
            return redirect('staff')
        

    return wrapper_function

def admin_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            custom_user=CustomUser.objects.get(user=request.user)
            if custom_user.role=="reader":
                return  redirect('reader')
            elif  custom_user.role=="staff":
                return redirect('staff')
            else:
                return redirect('publisher')
        

    return wrapper_function