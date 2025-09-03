from django.db import models
from django.core.exceptions import ValidationError
import re,os
from datetime import date, timedelta



def clean_email(value):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(pattern, value):
        raise ValidationError("Enter a valid mail address!") 

class userdata(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(validators=[clean_email], unique=True)
    phone_no = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=1,
        choices=[('0', 'inactive'), ('1', 'active'), ('5', 'deleted')], 
        default=1
    )

    def has_active_borrow(self):
        return self.borrowrecord_set.filter(returned_on__isnull=True).exists()

    class Meta:
        db_table = 'user_table'
        managed = False


class bookdata(models.Model):
    book_name = models.CharField(max_length=100)
    author = models.CharField(max_length=70)
    type = models.CharField(max_length=150)
    stock = models.IntegerField(default=0)

    status = models.CharField(
        max_length=1,
        choices=[('0', 'inactive'), ('1', 'active'), ('5', 'deleted')], 
        default=1
    )
    
    class Meta:
        db_table = 'books'
        managed = False

    def available(self):
        if self.status!=5:
            from .models import borrowrecord
            active_borrows=borrowrecord.objects.filter(book=self, returned_on__isnull=True).count()
            return self.stock - active_borrows
        else:
            return 0

def return_date(issue_date):
    if not return_date:
        return_date=issue_date + timedelta(days=7)
        return return_date

class borrowrecord(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('userdata', on_delete=models.CASCADE, db_column='user_id')
    book = models.ForeignKey('bookdata', on_delete=models.CASCADE, db_column='book_id')
    issue_date = models.DateField(default=date.today)
    return_date = models.DateField(default=[return_date])
    returned_on = models.DateField(blank=True, null=True)
    
    def is_active(self):
        return self.returned_on is None
    
    def fine(self):
        today = date.today()

        if (self.return_date < today):
            late_days = (today - self.return_date).days
            return late_days*2
        else:
            return 0
             
       

    
    class Meta:
        db_table = 'borrow_records'
        managed = False