from django.urls import path

from . import staff
from . import views



urlpatterns = [
    path('register/', views.registerPage, name="register"),
    path('login/',views.loginPage,name="login"),
    path('logout/',views.logoutUser,name='logout'),
    path('signup/',views.signup),
    #path('signin/',views.signin),
    
    path('',views.adminPage,name="adminPage"),

    path('reader/',views.reader,name="reader"),
    path('publisher/', views.publisher,name="publisher"),
    path('staff/', views.home,name="staff"),

    path('books', staff.books, name="book-page"),
    path('manageBooks/',staff.manageBooks,name="manageBooks-page"),
    path('saveBook/',staff.saveBook,name="saveBook-page"),
    path('deleteBook/',staff.deleteBook,name="deleteBook"),
    path('manageReaders/',staff.manageReader,name="readers-page"),
    path('banReader/',staff.banReader,name="ban-reader"),
    path('managePublishers/',staff.managePublisher,name="publishers-page"),
    path('payments-list',staff.payments,name="payments-list"),
    path('bookPdf',staff.book_pdf,name="book-pdf"),
    path('publisherPdf',staff.publisher_pdf,name="publisher-pdf"),
    path('readerPdf',staff.reader_pdf,name="reader-pdf"),

    path('adminPage/',views.adminPage,name="adminPage"),
    path('requests/',views.requests,name="requests-page"),
    path('approveRequest/',views.approveStaff,name="approveStaff"),
    path('filter/',views.filter),

    path('readbooks/',views.books,name="reader-books"),
    path('request-book/',views.requestBooks,name="request-book"),
    path('saveRequest/',views.saveRequest,name="saveRequest"),
    path('issuedBooks',views.issuedBooks,name="reader-issued-books"),
    path('returnBook/',views.returnBooks,name="return-book"),
    path('payments',views.payments,name="reader-payments"),
    path('payFine',views.payFine,name="pay-fine"),
    path('viewTransactions',views.viewTransactions,name="view-transactions"),

    path('myBooks',views.myBooks,name="publisher-books"),
    path('viewReaders',views.viewReaders,name="view-readers"),
    path('otherBooks',views.otherBooks,name="other-books"),
    path('issuedPBooks',views.issuedPBooks,name="publisher-issued-books"),
    
]