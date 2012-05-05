'''
Created on May 5, 2012

@author: trevor
'''

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.contrib.auth.models import User
from swapr.classifieds.models import Student
from swapr import settings


class Command(BaseCommand):
    args = '<none>'
    help = 'sends an email to any Students who have not activated their account'
    
    def handle(self, *args, **options):
        users = User.objects.filter(is_active=False)
        for u in users:
            student = Student.objects.get(user=u)
            confirmation_url = settings.DOMAIN+"confirmation/" + student.activation_key
            email_subject = "Woo hoo!! Confirm your account at CC Swapr!"
            email_body = "Hello " + student.user.first_name + ", \n\n"
            email_body += "Please visit the following URL to confirm your account: \n"
            email_body += confirmation_url + "\n\n"
            email_body += "Have a suggestion? Let us know at "+settings.DOMAIN+"feedback/. \n\n"
            email_body += "Thanks,\nThe CC Swapr Team (Trevor and Stanley :D )"
    
            self.stdout.write(email_subject + " " + email_body)
            #send_mail(email_subject,
            #          email_body,
            #          settings.DEFAULT_FROM_EMAIL,
            #          [student.user.email], 
            #          fail_silently=True)  