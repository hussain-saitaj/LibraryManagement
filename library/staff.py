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
import datetime


from .models import *
from .decorators import admin_only, publisher_only, reader_only, unauthenticated_user,staff_only

#pdf stuff
from django.http import FileResponse
import io
from reportlab import *
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter,inch,mm,A3
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors



@login_required(login_url='login')
@staff_only
def books(request):
	book_list = Book.objects.all()
	role=CustomUser.objects.get(user=request.user)
	for book in book_list:
		book.readers=-1*book.readers
	context = {
		'page_title':'Books',
		'books':book_list,
		'role':role
	}
	return render(request, 'library/books.html',context)


@login_required(login_url='login')
@staff_only
def manageBooks(request):
	book = {}
	publishers=CustomUser.objects.filter(role="publisher")
	if request.method == 'GET':
		data =  request.GET
		id = ''
		if 'id' in data:
			id= data['id']
		if id.isnumeric() and int(id) > 0:
			book = Book.objects.filter(id=id).first()

	context = {
		'book' : book,
		'publishers':publishers
	}
	return render(request, 'library/manageBook.html',context)




@login_required(login_url='login')
@staff_only
def saveBook(request):
	data=request.POST
	#print(data)
	resp = {'status':'failed'}
	if (data['id']).isnumeric() and int(data['id']) > 0:
		check  = Book.objects.exclude(id = data['id']).filter(isbn = data['isbn'])
	else:
		check  = Book.objects.filter(isbn = data['isbn'])

	if len(check) > 0:
		resp['status'] = 'failed'
		resp['msg'] = 'BOOK with same ISBN Already Exists'
	else:
		try:
			
			if (data['id']).isnumeric() and int(data['id']) > 0 :
				save_book = Book.objects.filter(id = data['id']).update(title=data['title'], isbn = data['isbn'],price = data['price'],category = data['category'],details = data['details'],edition=data['edition'],quantity=data['quantity'])
			else:
				pub = CustomUser.objects.filter(uname=data['publisher_id']).first() 
				save_book = Book(title=data['title'], isbn = data['isbn'],price = data['price'],category = data['category'],publisher_id = pub,details = data['details'],edition=data['edition'],quantity=data['quantity'])
				save_book.save()
			resp['status'] = 'success'
		except Exception:
			resp['status'] = 'failed'
			print(Exception)
			#print(json.dumps({"code":data['code'], "firstname" : data['firstname'],"middlename" : data['middlename'],"lastname" : data['lastname'],"dob" : data['dob'],"gender" : data['gender'],"contact" : data['contact'],"email" : data['email'],"address" : data['address'],"department_id" : data['department_id'],"position_id" : data['position_id'],"date_hired" : data['date_hired'],"salary" : data['salary'],"status" : data['status']}))
	return HttpResponse(json.dumps(resp), content_type="application/json")




@login_required(login_url='login')
@staff_only
def deleteBook(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Book.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required(login_url='login')
@staff_only
def manageReader(request):
	custom_user=CustomUser.objects.filter(role="reader")
	#print(custom_user)
	data=[]
	for reader in custom_user:
		d={}
		d['id']=reader.id
		d['username']=reader.user.username
		d['total']=len(Issued_details.objects.filter(user_id=reader))
		d['pending']=len(Issued_details.objects.filter(user_id=reader).filter(returned=False))
		d['returned']=len(Issued_details.objects.filter(user_id=reader).filter(returned=True))
		d['fine']=reader.fine
		d['status']=reader.isBan
		data.append(d)
	#print(data)
	return render(request, 'library/readers.html',{'data':data})

@login_required(login_url='login')
@staff_only
def banReader(request):
	resp={'status':'failed'}
	data=request.POST
	custom_user=CustomUser.objects.get(id=data['id'])
	if custom_user.isBan==False:
		custom_user.isBan=True
	else:
		custom_user.isBan=False
	custom_user.save()
	resp['status']='success'
	return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required(login_url='login')
@staff_only
def managePublisher(request):
	custom_user=CustomUser.objects.filter(role="publisher")
	#print(custom_user)
	data=[]
	for publisher in custom_user:
		books_list=Book.objects.filter(publisher_id=publisher)
		total_readers=0
		for book in books_list:
			issue_object=Issued_details.objects.filter(book_id=book).filter(returned=False)
			total_readers+=len(issue_object)
		d={}
		d['id']=publisher.id
		d['username']=publisher.user.username
		d['totalbooks']=len(books_list)
		d['totalreaders']=total_readers
		d['total']=len(Issued_details.objects.filter(user_id=publisher))
		d['pending']=len(Issued_details.objects.filter(user_id=publisher).filter(returned=False))
		d['returned']=len(Issued_details.objects.filter(user_id=publisher).filter(returned=True))
		d['fine']=publisher.fine
		d['status']=publisher.isBan
		data.append(d)
	#print(data)
	return render(request, 'library/publishers.html',{'data':data})

@login_required(login_url='login')
@staff_only
def payments(request):
	transactions=Transaction.objects.all()
	return render(request,'library/paymentsList.html',{'transactions':transactions})

@login_required(login_url='login')
@staff_only
def book_pdf(request):
	# Create Bytestream buffer
	buf = io.BytesIO()
	# Create a canvas
	c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
	# Create a text object
	textob = c.beginText()
	textob.setTextOrigin(inch, inch)
	textob.setFont("Helvetica", 14)

	# Add some lines of text
	#lines = [
	#	"This is line 1",
	#	"This is line 2",
	#	"This is line 3",
	#]
	
	# Designate The Model
	books = Book.objects.all()
	width, height = A3
	# Create blank list
	lines = [["Title","ISBN","Publisher","Category","Price","Edition","Details","Total\nBooks","Books\nAvailable"]]

	for book in books:
		lines.append([book.title,book.isbn,book.publisher_id.user.username,book.category,book.price,book.edition,book.details,book.quantity,(book.quantity-book.readers)])
	lines=lines[::-1]

	table = Table(lines, 9*[0.95*inch], 5*[0.6*inch])
	table.setStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
					("ALIGN", (0, 0), (-1, -1), "CENTER"),
					('INNERGRID', (0, 0), (-1, -1), 0.25,colors.black),('BOX', (0,0), (-1,-1), 0.25, colors.black),])

	table.wrapOn(c, width, height)
	table.drawOn(c, 0 * mm, 10 * mm)

	# Finish Up
	
	c.showPage()
	c.save()
	buf.seek(0)

	# Return something
	return FileResponse(buf, as_attachment=True, filename='book.pdf')


def reader_pdf(request):
	# Create Bytestream buffer
	buf = io.BytesIO()
	# Create a canvas
	c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
	# Create a text object
	textob = c.beginText()
	textob.setTextOrigin(inch, inch)
	textob.setFont("Helvetica", 14)

	custom_user=CustomUser.objects.filter(role="reader")
	#print(custom_user)
	data=[['id','username','Issued\nTotal Books','Reading\nBooks','Returned\nBooks','fine']]
	for reader in custom_user:
		
		data.append([reader.id,reader.user.username,len(Issued_details.objects.filter(user_id=reader)),len(Issued_details.objects.filter(user_id=reader).filter(returned=False)),len(Issued_details.objects.filter(user_id=reader).filter(returned=True)),reader.fine])
		
		#data.append(d)
	width, height = A3
	# Create blank list
	#data=[['id','username','totalbooks','totalreaders','total Books\nIssued','pending','returned','fine']]
	data=data[::-1]
	

	table = Table(data, 6*[0.95*inch], (len(custom_user)+1)*[0.6*inch])
	table.setStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
					("ALIGN", (0, 0), (-1, -1), "CENTER"),
					('INNERGRID', (0, 0), (-1, -1), 0.25,colors.black),('BOX', (0,0), (-1,-1), 0.25, colors.black),])

	table.wrapOn(c, width, height)
	table.drawOn(c, 0 * mm, 10 * mm)

	# Finish Up
	
	c.showPage()
	c.save()
	buf.seek(0)

	# Return something
	return FileResponse(buf, as_attachment=True, filename='reader.pdf')

def publisher_pdf(request):
	# Create Bytestream buffer
	buf = io.BytesIO()
	# Create a canvas
	c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
	# Create a text object
	textob = c.beginText()
	textob.setTextOrigin(inch, inch)
	textob.setFont("Helvetica", 14)

	custom_user=CustomUser.objects.filter(role="publisher")
	#print(custom_user)
	data=[['id','username','Published\nTotal Books','Total Readers','Issued\nTotal Books','Reading\nBooks','Returned\nBooks','fine']]
	for publisher in custom_user:
		books_list=Book.objects.filter(publisher_id=publisher)
		total_readers=0
		for book in books_list:
			issue_object=Issued_details.objects.filter(book_id=book).filter(returned=False)
			total_readers+=len(issue_object)
		data.append([publisher.id,publisher.user.username,len(books_list),total_readers,len(Issued_details.objects.filter(user_id=publisher)),len(Issued_details.objects.filter(user_id=publisher).filter(returned=False)),len(Issued_details.objects.filter(user_id=publisher).filter(returned=True)),publisher.fine])
		
		#data.append(d)
	width, height = A3
	# Create blank list
	#data=[['id','username','totalbooks','totalreaders','total Books\nIssued','pending','returned','fine']]
	data=data[::-1]
	

	table = Table(data, 8*[0.95*inch], (len(custom_user)+1)*[0.6*inch])
	table.setStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
					("ALIGN", (0, 0), (-1, -1), "CENTER"),
					('INNERGRID', (0, 0), (-1, -1), 0.25,colors.black),('BOX', (0,0), (-1,-1), 0.25, colors.black),])

	table.wrapOn(c, width, height)
	table.drawOn(c, 0 * mm, 10 * mm)

	# Finish Up
	
	c.showPage()
	c.save()
	buf.seek(0)

	# Return something
	return FileResponse(buf, as_attachment=True, filename='publisher.pdf')


