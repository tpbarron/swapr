'''
Created on Feb 3, 2012

@author: trevor
'''

from django.contrib import admin
from CC_Classifieds.classifieds.models import *

class StudentAdmin(admin.ModelAdmin):
    pass

class CommentAdmin(admin.ModelAdmin):
    pass

class BookAdmin(admin.ModelAdmin):
    pass

class BreakAdmin(admin.ModelAdmin):
    pass

class DiscussionAdmin(admin.ModelAdmin):
    pass

class ProductAdmin(admin.ModelAdmin):
    pass

class TransportationAdmin(admin.ModelAdmin):
    pass

class EventAdmin(admin.ModelAdmin):
    pass

#admin.site.register(User, StudentAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Break, BreakAdmin)
admin.site.register(Discussion, DiscussionAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Transportation, TransportationAdmin)
admin.site.register(Event, EventAdmin)


