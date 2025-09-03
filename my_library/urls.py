from django.urls import path 
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('home/', views.home, name='home'),
    path('users/', views.users, name='users'),
    path('viewuser/<int:user_id>', views.viewuser, name='viewuser'),
    path('edituser/<int:user_id>', views.edituser, name='edituser'),
    path('deleteuser/<int:user_id>', views.deleteuser, name='deleteuser'),
    path('users/searchuser/', views.searchuser, name='searchuser'),
    path('adduser/', views.adduser, name='adduser'),

    path('books/', views.books, name='books'),
    path('addbook/', views.addbook, name='addbook'),
    path('searchbook/', views.searchbook, name='searchbook'),
    path('editbook/<int:book_id>', views.editbook, name='editbook'),
    path('viewbook/<int:book_id>', views.viewbook, name='viewbook'),
    path('deletebook/<int:book_id>', views.deletebook, name='deletebook'),

    path('open_records/', views.open_records, name='open_records'),
    # path('open_view/<int:record_id>', views.open_view, name='open_view'),
    # path('open_edit/<int:record_id>', views.open_edit, name='open_edit'),
    path('searchopen/', views.searchopen, name='searchopen'),


    path('closed_records/', views.closed_records, name='closed_records'),
    path('searchclosed/', views.searchclosed, name='searchclosed'),

    path('borrow_book/', views.borrow_book, name='borrow_book'),
    path('return_book/<int:record_id>', views.return_book, name='return_book'),


]
