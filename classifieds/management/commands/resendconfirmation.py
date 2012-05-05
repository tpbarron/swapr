'''
Created on May 5, 2012

@author: trevor
'''

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.contrib.auth.models import User
from swapr.classifieds.models import Student
from swapr import settings
from string import Template


class Command(BaseCommand):
    args = '<none>'
    help = 'sends an email to any students who have not activated their account'
    
    def handle(self, *args, **options):
        users = User.objects.filter(is_active=False)
        for u in users:
            student = Student.objects.get(user=u)
            
            confirmation_url = settings.DOMAIN+"confirmation/" + student.activation_key +"/"
            feedback_url = settings.DOMAIN+"feedback/"
            self.stdout.write(u.get_full_name() + " " + student.activation_key + " " + confirmation_url +"\n")          
            email_subject = "Woo hoo!! Confirm your account at CC Swapr!"
            
            template_dict = dict(name=u.first_name, 
                                 confirm=confirmation_url, 
                                 feedback=feedback_url)
            email_body = Template("""
Hi $name,
                
I'm sorry if you are receiving this email for a second time. It seems that
some of my previous emails were categorized as spam. If you have already
received your confirmation email please disregard this. But if not, you 
can confirm your account here: 

$confirm

Have a suggestion? Let us know at $feedback.

Thanks,
The CC Swapr Team (Trevor and Stanley :D )""").safe_substitute(template_dict)
                        
            send_mail(email_subject,
                      email_body,
                      settings.DEFAULT_FROM_EMAIL,
                      [student.user.email], 
                      fail_silently=True)  
