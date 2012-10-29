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
    help = 'sends an email to all students who have created an account to try to urge them to use the site'
    
    def handle(self, *args, **options):
        users = User.objects.all()
        for u in users:
            student = u.student
            
            active = True
            if (u.is_active == False):
                active = False
                
            self.stdout.write("Sending to: " + u.get_full_name() + ", active: " + str(active) + "\n")
            email_subject = "CC Swapr - save green: save money, save trees!"
            feedback_url = settings.DOMAIN+"feedback/"
            
            if not active:
                confirmation_url = settings.DOMAIN+"confirmation/" + student.activation_key +"/"
                template_dict = dict(name=u.first_name,
                                 feedback=feedback_url,
                                 confirm=confirmation_url)
                email_body = Template("""
Hi $name,
                
Thank you for joining CC Swapr! Please activate it by visiting the following link:

$confirm

CC Swapr is a free service to help CC students save money and the environment. Trade books for class and other miscellaneous items, organize ride shares, and plan events.

Can you do me a favor and post some old books or random items you have lying around? You might even make a little $$$ from it!

Have a suggestion? Let me know at $feedback.

Thanks,
The CC Swapr Team
(Trevor Barron)""").safe_substitute(template_dict)

            else:
                template_dict = dict(name=u.first_name,
                                 feedback=feedback_url)
                email_body = Template("""
Hi $name,
                
Thank you for joining CC Swapr! CC Swapr is a free service to help CC students save money and the environment. Trade books for class and other miscellaneous items, organize ride shares, and plan events.

Can you do me a favor and post some old books or random items you have lying around? You might even make a little $$$ from it!

Have a suggestion? Let me know at $feedback.

Thanks,
The CC Swapr Team
(Trevor Barron)""").safe_substitute(template_dict)
             
            self.stdout.write(email_subject + "\n" + email_body+"\n\n")
            send_mail(email_subject,
                      email_body,
                      settings.DEFAULT_FROM_EMAIL,
                      [student.user.email], 
                      fail_silently=True)  
