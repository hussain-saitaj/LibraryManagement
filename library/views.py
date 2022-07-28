import json
from django.shortcuts import render,redirect,reverse
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.http import HttpResponsePermanentRedirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from datetime import date, datetime

#from library_management.accounts.decorators import unauthenticated_user

from .models import *
from .decorators import admin_only, allowed_users, publisher_only, reader_only, unauthenticated_user,staff_only



# Create your views here.
@unauthenticated_user
def loginPage(request):
	if request.method=='POST':
		username = request.POST['username']
		password = request.POST['password']
		#print(password)
		user = authenticate(username=username, password=password)
		if user is not None and user.is_staff:
			auth.login(request,user)
			return redirect('adminPage')
		elif user is not None:
			custom_user=CustomUser.objects.get(user=user)
			# print(user.username)
			# print(custom_user.role)
			if custom_user.role=="reader":
				auth.login(request, user)
				#applications_list=Application.objects.filter(payment_status=1)
				return redirect('reader')
			elif custom_user.role == "publisher":
				
				auth.login(request,user)
				return redirect('publisher')
			elif custom_user.role=="staff":
				request_object=Request.objects.get(user_id=custom_user)
				if request_object.status=="approved":
					auth.login(request,user)
					return redirect('staff')
				else:
					return HttpResponse("your profile is not approved")
		else:
			
			return HttpResponse('Invalid Credentials')
				
	else:
		return render(request,'library/login.html')

# @csrf_exempt
# def signin(request):
# 	resp = {"status":'failed','msg':'','url':''}


@csrf_exempt
def signup(request):
	#print('hai')
	resp = {"status":'failed','msg':''}
	#print(request.POST)
	if request.method=="POST":
		#print('hai')
		userid=request.POST.get('userid')
		email=request.POST.get('email')
		user_name=request.POST.get('uname')
		phone=request.POST.get('phone_no')
		address=request.POST.get('address')
		password1=request.POST.get('password')
		
		role=request.POST.get('role')
		#print(phone)

		if len(User.objects.filter(username=userid))!=0:
			resp['status'] = 'failed'
			resp['msg']="User already exits"
			return HttpResponse(json.dumps(resp),content_type='application/json')

		if len(phone)!=10 or not phone.isnumeric():
			resp['status'] = 'failed'
			resp['msg']="Phone number not valid"
		else:
			user_object=User.objects.create_user(username=userid,password=password1)
			user_object.save()
			custom_user_object=CustomUser()
			custom_user_object.user=user_object
			custom_user_object.email=email
			custom_user_object.uname=user_name
			custom_user_object.phone_no=phone
			custom_user_object.address=address
			custom_user_object.role=role
			
			custom_user_object.save()
			if role=="staff":
				request_object=Request()
				request_object.user_id=custom_user_object
				request_object.status="notapproved"
				request_object.register_date=date.today()
				request_object.save()

			return redirect(reverse('login'))
	#print(resp)
	return HttpResponse(json.dumps(resp),content_type='application/json')


		


@unauthenticated_user
def registerPage(request):
	return render(request,'library/signup.html')

def logoutUser(request):
	logout(request)
	return redirect('login')



@login_required(login_url='login')
@publisher_only
def  publisher(request):
	custom_user=CustomUser.objects.get(user=request.user)
	books=Book.objects.filter(publisher_id=custom_user)
	totalReaders=0
	for book in books:
		issued_object=Issued_details.objects.filter(book_id=book).filter(returned=False)
		totalReaders+=len(issued_object)
	context = {
		'page_title':'Home',
		'total_book':len(books),
		'total_readers':totalReaders,
		'fine':custom_user.fine,
	}
	return render(request, 'library/publisherHome.html',context)



@login_required(login_url='login')
@publisher_only
def myBooks(request):
	custom_user=CustomUser.objects.get(user=request.user)
	books=Book.objects.filter(publisher_id=custom_user)
	if custom_user.isBan:
		return render(request,'library/pbannedpage.html')
	return render(request,'library/publisherBooks.html',{'books':books})

@login_required(login_url='login')
@publisher_only
def viewReaders(request):
	data=request.GET
	#print(data['id'])
	book=Book.objects.get(id=data['id'])
	issued_objects=Issued_details.objects.filter(book_id=book).filter(returned=False)
	readers=[]
	for object in issued_objects:
		user=object.user_id.user.username
		readers.append(user)
	res="<br>".join(readers)
	print(res)
	return HttpResponse(res)

@login_required(login_url='login')
@publisher_only
def otherBooks(request):
	custom_user=CustomUser.objects.get(user=request.user)
	book_list = Book.objects.exclude(publisher_id=custom_user)
	context = {
		'page_title':'Books',
		'books':book_list,
		
	}
	if custom_user.isBan:
		return render(request,'library/pbannedpage.html')
	return render(request, 'library/publisherNBooks.html',context)


@login_required(login_url='login')
@publisher_only
def issuedPBooks(request):
	user_id=CustomUser.objects.get(user=request.user)
	issued_objects=Issued_details.objects.filter(user_id=user_id)
	if user_id.isBan:
		return render(request,'library/pbannedpage.html')
	return render(request,'library/publisherIssuedBooks.html',{'data':issued_objects})


@login_required(login_url='login')
@reader_only
def reader(request):
	custom_user=CustomUser.objects.get(user=request.user)
	issued_object=Issued_details.objects.filter(user_id=custom_user)

	context = {
		'page_title':'Home',
		'total_books':len(issued_object),
		'books_returned':len(issued_object.filter(returned=True)),
		'books_pending':len(issued_object.filter(returned=False)),
		'fine':custom_user.fine,
		'user':custom_user.user
	}
	return render(request, 'library/readerHome.html',context)


@login_required(login_url='login')
@reader_only
def books(request):
	book_list = Book.objects.all()
	for book in book_list:
		book.readers=-1*book.readers
	context = {
		'page_title':'Books',
		'books':book_list,
		
	}
	custom_user=CustomUser.objects.get(user=request.user)
	if custom_user.isBan:
		return render(request,'library/bannedpage.html')
	return render(request, 'library/readerBooks.html',context)

@login_required(login_url='login')
@allowed_users(["publisher","reader"])
def requestBooks(request):
    book = {}
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            book = Book.objects.filter(id=id).first()
    
    context = {
        'book' : book
    }
    return render(request, 'library/readerRequest.html',context)


@login_required(login_url='login')
@allowed_users(["publisher","reader"])
def saveRequest(request):
	data=request.POST
	#print(data)
	resp = {'status':'failed'}
	user_id=CustomUser.objects.get(user=request.user)
	book_id=Book.objects.get(id=data['id'])
	return_date=data['return_date']
	#print(user_id,book_id,return_date)
	issued_object=Issued_details.objects.filter(user_id=user_id).filter(book_id=book_id).filter(returned=False)
	if len(issued_object)!=0:
		resp['msg']="This Book is already Issued,Please select another Book"
		return HttpResponse(json.dumps(resp), content_type="application/json")
	issued_data=Issued_details()
	issued_data.user_id=user_id
	issued_data.book_id=book_id
	issued_data.return_date=return_date
	issued_data.save()
	book_id.readers+=1
	book_id.save()
	resp['status']='success'
	return HttpResponse(json.dumps(resp), content_type="application/json")



@login_required(login_url='login')
@reader_only
def issuedBooks(request):
	user_id=CustomUser.objects.get(user=request.user)
	issued_objects=Issued_details.objects.filter(user_id=user_id)
	if user_id.isBan:
		return render(request,'library/bannedpage.html')
	return render(request,'library/readerIssuedBooks.html',{'data':issued_objects})

@login_required(login_url='login')
@allowed_users(["publisher","reader"])
def returnBooks(request):
	data =  request.POST
	resp = {'status':''}
	custom_user=CustomUser.objects.get(user=request.user)
	try:
		issued_object=Issued_details.objects.get(id = data['id'])
		issued_object.returned=True
		book=issued_object.book_id
		today=date.today()
		if today>issued_object.return_date:
			issued_object.fine=1000
			custom_user.fine=custom_user.fine+1000
			custom_user.save()
			transaction_object=Transaction()
			transaction_object.user_id=custom_user
			transaction_object.book_id=issued_object.book_id
			transaction_object.total_amount=1000
			transaction_object.save()

		book.readers-=1
		book.save()		
		issued_object.save()
		resp['status'] = 'success'
	except:
		resp['status'] = 'failed'
	return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required(login_url='login')
@allowed_users(["publisher","reader"])
def payments(request):
	custom_user=CustomUser.objects.get(user=request.user)
	transactions=Transaction.objects.filter(user_id=custom_user)
	#print(transactions)
	if custom_user.role=="reader":
		return render(request,'library/payments.html',{'transactions':transactions,'user':custom_user})
	return render(request,'library/ppayments.html',{'transactions':transactions,'user':custom_user})

@login_required(login_url='login')
@allowed_users(["publisher","reader"])
def payFine(request):
	resp={'status':'failed','error':'enter correct amount'}
	data=request.POST
	print(data)
	transaction_object=Transaction.objects.get(id=data['id'])
	if(int(data['pay'])<=0 or transaction_object.amount_paid+int(data['pay'])>transaction_object.total_amount):
		return HttpResponse(json.dumps(resp), content_type="application/json")
	
	transaction_object.amount_paid+=int(data['pay'])
	transaction_object.completed_date=datetime.today()
	history_object=History()
	history_object.transaction_id=transaction_object
	history_object.amount_paid=int(data['pay'])
	history_object.save()
	user_id=transaction_object.user_id
	user_id.fine-=int(data['pay'])
	user_id.save()
	transaction_object.save()
	resp['status']="success"
	return HttpResponse(json.dumps(resp), content_type="application/json")


def viewTransactions(request):
	data=request.GET
	transaction_id=data['id']
	history_object=History.objects.filter(transaction_id=transaction_id)
	if len(history_object)==0:
		return HttpResponse("No records Found")
	res=[]
	for object in history_object:
		res.append("Amount "+str(object.amount_paid)+"&nbsp;&nbsp;&nbsp;&nbsp;paid on Date: "+str(object.paid_date))
	res="<br>".join(res)
	return HttpResponse(res)


@login_required(login_url='login')
@staff_only
def home(request):
	publishers=CustomUser.objects.filter(role="publisher")
	readers=CustomUser.objects.filter(role="reader")
	context = {
		'page_title':'Home',
		'total_book':len(Book.objects.all()),
		'total_readers':len(readers),
		'total_publishers':len(publishers),
	}
	return render(request, 'library/home.html',context)






@login_required(login_url='login')
@admin_only
def adminPage(request):
	request_list = Request.objects.all()
	context = {
	'page_title':'Admin',
	'total_requests':len(request_list),
	}
	return render(request,'library/adminHome.html',context)


@login_required(login_url='login')
@admin_only
def requests(request):
	print("hai")
	request_list = Request.objects.all()
	context = {
		'page_title':'Requests',
		'requests':request_list,
	}
	return render(request, 'library/requests.html',context)

def filter(request):
	resp={'status':'failed'}
	request_list = Request.objects.all()
	if request.method == "POST":
		data=request.POST
		print(data)
		request_list=Request.objects.filter(status=data['value'])
		print(request_list)
	return HttpResponse(json.dumps(resp), content_type="application/json")



@login_required(login_url='login')
@admin_only
def approveStaff(request):
	data=request.POST
	#print(data)
	resp = {'status':''}
	try:
		request_object=Request.objects.get(id = data['id'])
		if request_object.status=="approved":
			request_object.status="notapproved"
		else:
			request_object.status="approved"
		request_object.save()
		resp['status'] = 'success'
	except:
		resp['status'] = 'failed'
	return HttpResponse(json.dumps(resp), content_type="application/json")




