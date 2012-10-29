'''
Created on May 5, 2012

@author: trevor
'''

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from swapr.classifieds.models import Student, StudentSettings


class Command(BaseCommand):
    args = '<none>'
    help = 'creates a studentSettings obj for each user'
    
    def handle(self, *args, **options):
        users = User.objects.all()
        for u in users:
            student = Student.objects.get(user=u)
            
            ss = StudentSettings(
                    student=student,
                    default_email=u.email
            )
            
            ss.save()
            self.stdout.write(u.get_full_name()+"\n")