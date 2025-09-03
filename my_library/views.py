from django.shortcuts import render, redirect
from .form import userdataform, bookdataform, borroerecordForm
from .models import userdata, bookdata, borrowrecord
from django.db.models import Q
from django.utils.timezone import now
from datetime import date, timezone
from django.db.models import Exists, OuterRef
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from django.http import JsonResponse
from django.utils import timezone
from django.template.loader import render_to_string


static_mail ='admin@library.com'
static_password = 'library#123'

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
    
        if email == static_mail and password == static_password:
            return redirect('home')
        else:
            print('Invalid credentials!')
            return render(request, 'login.html')

    return render(request, 'login.html')            

def home(request):
    user_count = userdata.objects.exclude(status=5).count()
    book_count = bookdata.objects.exclude(status=5).count()
    open_records_count = borrowrecord.objects.exclude(returned_on__isnull=False).count()
    closed_records_count = borrowrecord.objects.exclude(returned_on__isnull=True).count()

    context = {
        'user_count' : user_count,
        'book_count' : book_count,
        'open_records_count' : open_records_count,
        'closed_records_count' : closed_records_count,
    }

    return render(request, 'home.html', context)

def borrow_book(request):

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        book_id = request.POST.get('book_id')
        issue_date = request.POST.get('issue_date')
        return_date = request.POST.get('return_date')

        issue_date = date.fromisoformat(issue_date)
        
        if issue_date > date.today():
            raise ValidationError("issue date can't be future!")
        
        return_date = issue_date + timedelta(days=7)
        
        if not user_id or not book_id or not issue_date:
            print("All fields are required!")
            return redirect("borrow_book") 
        

        user_has_active = borrowrecord.objects.filter(
            user_id = user_id,
            returned_on__isnull=True
        ).exists()


        if user_has_active:
            print("This member already has an active borrow record")
        else:
            borrowrecord.objects.create(
                user_id = user_id,
                book_id = book_id,
                issue_date = issue_date,
                return_date=return_date,

            )
            form = borroerecordForm(request.POST)
            if form.is_valid():
                form.save()
            print("Book issued successfully!")
            return redirect("open_records")

    active_borrow = borrowrecord.objects.filter(
        user_id=OuterRef('pk'),
        returned_on__isnull=True, 
        )
    
    users = (
        userdata.objects.exclude(status = '5').annotate(has_active=Exists(active_borrow)).order_by('full_name')
    )
    

    context = {
        'users': users,
        'books': bookdata.objects.exclude(status=5),
        'today': date.today().isoformat()
        
    }

    return render(request, 'borrow_book.html', context)


def open_records(request):
    records = borrowrecord.objects.filter(returned_on__isnull=True)
    return render(request, 'open_records.html',{'records': records, 'today': date.today()
    })


def return_book(request, record_id):
    record = borrowrecord.objects.get(id=record_id)

    if request.method == "POST":
        record.returned_on = now().date()
        record.save()
        return redirect('open_records')
    fine = record.fine()
    if fine > 0:
        print(f"{record.user.full_name} has late to return. Fine of rs.{fine} may apply!")
    else:
        print(f"Book reterned successfylly {record.user.full_name}!")
    return redirect('open_records')    


# def open_view(request, record_id):
#     record = borrowrecord.objects.get(id=record_id)
#     print(f"showing info of id:{record.id}")
    

#     return render(request, 'open_view.html', {'record': record})


# def open_edit(request, record_id):
#         record = borrowrecord.objects.get(id=record_id)
#         if request.method == 'POST':
#             record.returned_on = request.POST.get('returned_on')
#             record.save()
#             return redirect('open_records')
#         print (f"Editing user id: {record.id} ")

        # if request.method == 'POST':
        #     form = borroerecordForm(request.POST, instance=record)
        #     print("Form data received:", request.POST)

        #     if form.is_valid():
        #         try:
        #             form.save()
        #             form.save()
        #             print(f"Data saved successfully! ID: {record.id}")
        #             return redirect('open_records')
                
        #         except Exception as e:
        #             print(f"Database Error:{e}")

        #     else:
        #         print("Form error:", form.errors)

        # else:
        #     form=userdataform(instance=record)
        #     print("Initializing form with user data")


    
        # return render(request, 'open_edit.html', { 'form': form, 'record': record})     

def searchopen(request):

    query = request.GET.get('q', '').strip()
    records = borrowrecord.objects.filter(returned_on__isnull=True)

    if query:
        records = records.filter(
            Q(book__book_name__icontains = query) | Q(user__full_name__icontains = query ) | Q(book__author__icontains = query )
        ).distinct()
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html =  render_to_string('open_rows.html', {'records':records, "today": timezone.now().date()})
        return JsonResponse({"html": html})

    return render(request, 'open_records.html', {'records': records, "today": timezone.now().date()})



def closed_records(request):
    records = borrowrecord.objects.filter(returned_on__isnull=False).order_by('-returned_on')
    return render(request, 'closed_records.html', {'records': records})

def searchclosed(request):

    query = request.GET.get('q', '').strip()
    records = borrowrecord.objects.filter(returned_on__isnull=False)

    if query:
        records = records.filter(
            Q(book__book_name__icontains = query) | Q(user__full_name__icontains = query )
        ).distinct()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            html =  render_to_string('closed_rows.html', {'records':records})
            return JsonResponse({"html": html})

    return render(request, 'closed_records.html', {'records': records})





def books(request):
    if request.method == 'GET':
        books = bookdata.objects.exclude(status=5)
        # query = request.GET.get('b', '').strip()

        # if query:
        #     books = books.filter(Q(book_name__icontains=query)).distinct() 'query': query

        return render(request, 'books.html', {'books': books, } )
    
 
def addbook(request):
    if request.method == 'POST':
        form = bookdataform(request.POST)
        print("Form Submited!")

        if form.is_valid():
            print("from is valid!")
        
            try:
                form.save()
                return redirect('books')
            except Exception as e:
                print(f"Database Error:{e}")
        else:
            print("ERROR!")
    else:
        form=bookdataform()

    return render(request, 'addbook.html', {'form':form})

def searchbook(request):

    query = request.GET.get('b', '').strip()
    books = bookdata.objects.exclude(status=5)

    if query:
        books = books.filter(
            Q(book_name__icontains = query) | Q(author__icontains=query)
        ).distinct()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
            html =  render_to_string('book_rows.html', {'books':books})
            return JsonResponse({"html": html})



    return render(request, 'books.html', {'books': books})

def viewbook(request, book_id):
    book = bookdata.objects.get(id=book_id)
    print(f"showing info of id:{book.id}")

    return render(request, 'viewbook.html', {'book': book})


def editbook(request, book_id):
        book = bookdata.objects.get(id=book_id)
        print (f"Editing user id: {book.id} ")
        active_book = book.stock - book.available()

        if request.method == 'POST':
            form = bookdataform(request.POST, instance=book)
            print("Form data received:", request.POST)

            if form.is_valid():
                if (book.stock < active_book):
                    print("Error edit process blocked!")
                
                else:                
                    try:
                        book= form.save()
                        book.save()
                        print(f"Data saved successfully! ID: {book.id}")
                        return redirect('books')
                    
                    except Exception as e:
                        print(f"Database Error:{e}")

            else:
                print("Form error:", form.errors)

        else:
            form=userdataform(instance=book)
            print("Initializing form with user data")


    
        return render(request, 'editbook.html', { 'form': form, 'book': book, 'active_book' : active_book})         

def deletebook(request, book_id):
    active_borrow = borrowrecord.objects.filter(book_id=book_id, returned_on__isnull=True).exists()
    book = bookdata.objects.get(id=book_id)
    print (f"trying to deleted book id: {book.id} ")

    # if active_borrow:
    #     print("book deletion blocked! \n-active borrow records found!")
    #     return redirect('books')

    if (book.stock != book.available):
        print("book deletion blocked! \n-active borrow records found!")
        return redirect('books')
    
    try:
        book.status = '5'
        book.save()
        print(f"Data deleted successfully!")

    except Exception as e:
        print(f"{e} error")

    return redirect('books')


def adduser(request):
    if request.method == 'POST':
        form = userdataform(request.POST)
        print("Form Submited!")

        if form.is_valid():
            print("from is valid!")
        
            try:
                form.save()
                return redirect('users')
            except Exception as e:
                print(f"Database Error:{e}")
        else:
            print("ERROR!")
    else:
        form=userdataform()

    return render(request, 'adduser.html', {'form':form})

def users(request):
    if request.method == 'GET':
        users = userdata.objects.exclude(status = '5')
    return render(request, 'users.html', {'users': users} )

def searchuser(request):

    query = request.GET.get('q', '').strip()
    users = userdata.objects.exclude(status='5')

    if query:
        users = users.filter(
            Q(full_name__icontains = query)
        ).distinct()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            html =  render_to_string('user_rows.html', {'users':users})
            return JsonResponse({"html": html})
    return render(request, 'users.html', {'users': users})




def viewuser(request, user_id):
    user = userdata.objects.get(id=user_id)
    print(f"showing info of id:{user.id}")

    return render(request, 'viewuser.html', {'user': user})

def edituser(request, user_id):
        user = userdata.objects.get(id=user_id)
        print (f"Editing user id: {user.id} ")

        if request.method == 'POST':
            form = userdataform(request.POST, instance=user)
            print("Form data received:", request.POST)

            if form.is_valid():
                try:
                    user= form.save()
                    user.save()
                    print(f"Data saved successfully! ID: {user.id}")
                    return redirect('users')
                
                except Exception as e:
                    print(f"Database Error:{e}")

            else:
                print("Form error:", form.errors)

        else:
            form=userdataform(instance=user)
            print("Initializing form with user data")


    
        return render(request, 'edit.html', { 'form': form, 'user': user})         

def deleteuser(request, user_id):

    active_borrow = borrowrecord.objects.filter(user_id=user_id, returned_on__isnull=True).exists()
    user = userdata.objects.get(id=user_id)
    print (f"deleted user id: {user.id} ")

    if active_borrow:
        print("user deletion blocked! \n -active borrow records found!")
        return redirect('users')

    else:
        try:
            user.status = '5'
            user.save()
            print(f"Data deleted successfully!")

        except Exception as e:
                print(f"{e} error")

        return redirect('users')