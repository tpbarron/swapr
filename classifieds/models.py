from django.contrib.auth.models import User
from django.db import models
from django import forms
import datetime

 

break_options = (
    ('1', '1st'),
    ('2', '2nd'),
    ('3', 'Thanksgiving'),
    ('4', 'Winter'),
    ('5', '5th'),
    ('6', 'Spring'),
    ('7', '7th'),
    ('8','Summer'),
)

class Student(models.Model):
    user = models.OneToOneField(User)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()


class Entry(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    expiration = models.DateTimeField(default=datetime.datetime.now() + datetime.timedelta(days=30))
    published = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    def get_num_comments(self):
        return len(self.comments.all())
    
    def get_num_unique_views(self):
        return self.views.filter(unique=True).count()
    
    def is_expired(self):
        return datetime.datetime.now() < self.expiration
    
    def get_short_description(self):
        if (len(self.description) < 80):
            return self.description
        else:
            return self.description[0:80] + "..."
        
    class Meta:
        verbose_name = "Entry"
        verbose_name_plural = "Entries"
    
        
    
category_options = (
    ('anthropology', 'Anthropology'),
    ('art', 'Art'),
    ('asian_studies', 'Asian studies'),
    ('biochem', 'Biochemistry'),
    ('bio', 'Biology'),
    ('chem', 'Chemistry'),
    ('classics', 'Classics'),
    ('complit', 'Comparative literature'),
    ('cs', 'Computer science'),
    ('dance', 'Dance'),
    ('drama', 'Drama'),
    ('econ', 'Economics'),
    ('edu', 'Education'),
    ('english', 'English'),
    ('environ', 'Environmental science'),
    ('femgen', 'Feminist and gender studies'),
    ('franco', 'Francophone and Mediterranean studies'),
    ('geo', 'Geology'),
    ('german', 'German'),
    ('russian', 'Russian'), 
    ('east_asian', 'East Asian languages'),
    ('history', 'History'),
    ('ipe', 'International political economy'),
    ('math', 'Math'),
    ('music', 'Music'),
    ('neuro', 'Neuroscience'),
    ('philosophy', 'Philosophy'),
    ('physics', 'Physics'),
    ('polisci', 'Political science'),
    ('psych', 'Psychology'),
    ('religion', 'Religion'),
    ('russian_eurasian', 'Russian-Eurasian studies'),
    ('sociology', 'Sociology'),
    ('southwest', 'Southwest studies'),
    ('spanish', 'Spanish'),
    ('sport_science', 'Sport science'),
    ('other', 'Other'),
)

class View(models.Model):
    user = models.ForeignKey(User, related_name='views')
    time = models.DateTimeField()
    entry = models.ForeignKey(Entry, related_name='views')    
    unique = models.BooleanField()

    class Meta:
        verbose_name = "View"
        verbose_name_plural = "Views"
    
ref_options = (
    ('qr0', 'Launch QR Code'),
    ('null', 'Default no referrer')
)     
class Ref(models.Model):
    time = models.DateTimeField()
    useragent = models.CharField(max_length=1000, blank=True)
    mref = models.CharField(max_length=10, choices=ref_options)
    
    def __str__(self):
        return self.mref + " " + str(self.time)
    
    class Meta:
        verbose_name = "QR Reference"
        verbose_name_plural = "QR References"
        
class Break(Entry):
    break_name = models.CharField(max_length=100, choices=break_options)
    posted_by = models.ForeignKey(User, related_name='breaks')
    
    def get_break_name(self):
        for b in break_options:
            if b[0] == self.break_name:
                return b[1]
        return self.break_name
    
    def get_absolute_url(self):
        return "breaks/%i/" % self.id
    
    class Meta:
        verbose_name = "Break"
        verbose_name_plural = "Breaks"
        
        
    
class Product(Entry):
    posted_by = models.ForeignKey(User, related_name='products')
    
    def get_absolute_url(self):
        return "sales/%i/" % self.id
    
    class Meta:
        verbose_name = "For Sale"
        verbose_name_plural = "For Sale"
        
        
    
    
class Discussion(Entry):
    posted_by = models.ForeignKey(User, related_name='discussions')
    votesup = models.IntegerField(default=0)
    votesdown = models.IntegerField(default=0)
    
    def get_votes(self):
        return self.votes.filter(vote=1).count() - self.votes.filter(vote=0).count()
            
    def is_vote_active(self):
        usr = self.posted_by
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        
        if (self.votes.filter(user=usr, time__gt=yesterday).exists()):
            return "inactive" # if the user has voted in the last day on this discussion
        else:
            return "active" # if the uer has not voted in the last day
        
    def get_absolute_url(self):
        return "discussions/%i/" % self.id
        
    class Meta:
        verbose_name = "Discussion"
        verbose_name_plural = "Discussions"
        
        

class Book(Entry):
    posted_by = models.ForeignKey(User, related_name='books')
    category = models.CharField(max_length=25, choices=category_options)

    def get_absolute_url(self):
        return "books/%i/" % self.id
    
    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        

class Event(Entry):
    date = models.DateField()
    location = models.CharField(max_length=100)
    posted_by = models.ForeignKey(User, related_name='events')

    def get_absolute_url(self):
        return "events/%i/" % self.id
    
    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        
        
class Transportation(Entry):
    date = models.DateField()
    posted_by = models.ForeignKey(User, related_name='transportation')
       
    def get_absolute_url(self):
        return "transportation/%i/" % self.id
    
    class Meta:
        verbose_name = "Ride"
        verbose_name_plural = "Rides"
        
        
# upvote = 1
# downvote = 0
class Vote(models.Model):
    discussion = models.ForeignKey(Discussion, related_name='votes')
    user = models.ForeignKey(User, related_name='votes')
    time = models.DateTimeField()
    vote = models.SmallIntegerField()

    class Meta:
        verbose_name = "Vote"
        verbose_name_plural = "Votes"
        

class Feedback(models.Model):
    student = models.ForeignKey(Student, related_name='feedback')
    message = models.TextField()
    
class PrivateMessage(models.Model):
    student = models.ForeignKey(Student, related_name='private_message')
    subject = models.CharField(max_length=100)
    message = models.TextField()
    
    

##forms 
class FeedbackForm(forms.Form):
    message = forms.CharField(
                widget=forms.Textarea(attrs={'class' : 'form_textarea'}))
    
class LoginForm(forms.Form):
    email = forms.EmailField(
                widget=forms.TextInput(attrs={'class' : 'form_p'}))
    password = forms.CharField(
                widget=forms.PasswordInput(attrs={'class' : 'form_p'}))
    
    def get_user_name(self, email):
        i = email.rfind("@")
        username = email[0:i]
        return username
    
    def clean(self):
        cleaned_data = self.cleaned_data
        email = cleaned_data.get("email")
        if email:
            i = email.rfind("@")
            if (email[i:].lower() != "@coloradocollege.edu"):
                #raise forms.ValidationError("Please use your ColoradoCollege.edu email address")
                msg = u"Please use your ColoradoCollege.edu email address."
                self._errors["email"] = self.error_class([msg])
        
        return cleaned_data
    
    def confirm_error(self):
        msg = u"Did you confirm your account?"
        self._errors["password"] = self.error_class([msg])
        
    def password_error(self):
        msg = u"Your password is incorrect."
        self._errors["password"] = self.error_class([msg])
        
    
    
class NewUserForm(LoginForm):
    firstname = forms.CharField(max_length=30,
                label="First name",
                widget=forms.TextInput(attrs={'class' : 'form_p'}))
    lastname = forms.CharField(max_length=30,
                label="Last name",
                widget=forms.TextInput(attrs={'class' : 'form_p'}))
    password_confirm = forms.CharField(
                label="Confirm password",
                widget=forms.PasswordInput(attrs={'class' : 'form_p'}))
    
    def user_exists_error(self):
        msg = u"An account with this email has already been created."
        self._errors["email"] = self.error_class([msg])
        
    def clean(self):
        cleaned_data = self.cleaned_data
        email = cleaned_data.get("email")
        if email:
            i = email.rfind("@")
            if (email[i:].lower() != "@coloradocollege.edu"):
                msg = u"Please use your ColoradoCollege.edu email address."
                self._errors["email"] = self.error_class([msg])
                #raise forms.ValidationError("Please use your ColoradoCollege.edu email")
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("password_confirm")
        if (p1 != p2):
            msg = u"Your passwords must match."
            self._errors["password"] = self.error_class([msg])
            #raise forms.ValidationError("Your passwords must match")
        
        return cleaned_data
    
#to contact a specific user    
class UserContactForm(forms.Form):
    subject = forms.CharField(
                widget=forms.TextInput(attrs={'class' : 'form_p'}))
    message = forms.CharField(
                widget=forms.Textarea(attrs={'class' : 'form_textarea'}))
  

class AddForm(forms.Form):
    title = forms.CharField(max_length=100,
                label='Title',
                widget=forms.TextInput(attrs={'class' : 'form_p'}))
    desc = forms.CharField(
                label='Description',
                widget=forms.Textarea(attrs={'class' : 'form_textarea'}))
    
class BreakAddForm(AddForm):
    break_name = forms.ChoiceField(choices=break_options,
                label='Break',
                widget=forms.Select(attrs={'class' : 'form_p'}))

class ProductAddForm(AddForm):
    pass

class DiscussionAddForm(AddForm):
    pass

class BookAddForm(AddForm):
    category = forms.ChoiceField(choices=category_options,
                label='Category',
                widget=forms.Select(attrs={'class' : 'form_p'}))
    
#import re
class EventAddForm(AddForm):
    date = forms.DateField(
                label='Date',
                widget=forms.TextInput(attrs={'class' : 'form_p'}))
    location = forms.CharField(max_length=100,
                label='Location',
                widget=forms.TextInput(attrs={'class' : 'form_p'}))
    
#    def clean(self):
#        cleaned_data = self.cleaned_data
#        date = cleaned_data.get("date")
#        if date: #should be format mm/dd/yyyy
#            print (date)
#            rg = re.compile(r"""\d{4}     #year
#                                \-        #hyphen
#                                \d{2}     #month
#                                \-        #hyphen
#                                \d{2}$    #day""", re.X)
#            if re.match(rg, date) != None:
#                msg = u"The date must be in mm/dd/yyyy format."
#                self._errors["date"] = self.error_class([msg])
#               
#        return cleaned_data
    
class TransportationAddForm(AddForm):
    date = forms.DateField(
                widget=forms.TextInput(attrs={'class' : 'form_p'}))
      
    
#comment form
class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)
    
##comment classes
class Comment(models.Model):
    comment = models.TextField()
    left_by = models.ForeignKey(User)
    date = models.DateField(default=datetime.datetime.now())
    
    def __str__(self):
        return "Comment: " + str(self.pk)


class BreakComment(Comment):
    left_on = models.ForeignKey(Break, related_name="comments")

    def __str__(self):
        return "BreakComment: " + str(self.pk)
    

class ProductComment(Comment):
    left_on = models.ForeignKey(Product, related_name="comments")
    
    def __str__(self):
        return "ProductComment: " + str(self.pk)
    
    
class DiscussionComment(Comment):
    left_on = models.ForeignKey(Discussion, related_name="comments")
    
    def __str__(self):
        return "DiscussionComment: " + str(self.pk)
    
    
class BookComment(Comment):
    left_on = models.ForeignKey(Book, related_name="comments")

    def __str__(self):
        return "BookComment: " + str(self.pk)
    
    
class EventComment(Comment):
    left_on = models.ForeignKey(Event, related_name="comments")
    
    def __str__(self):
        return "EventComment: " + str(self.pk)
    

class TransportationComment(Comment):
    left_on = models.ForeignKey(Transportation, related_name="comments")
    
    def __str__(self):
        return "TransportationComment: " + str(self.pk)
