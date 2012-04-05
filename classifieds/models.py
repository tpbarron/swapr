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


class Entry(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.title
    
    def get_num_comments(self):
        return len(self.comments.all())
    
    def get_num_unique_views(self):
        return self.views.filter(unique=True).count()
    
    def get_short_description(self):
        if (len(self.description) < 80):
            return self.description
        else:
            return self.description[0:80] + "..."
    
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

        
class Break(Entry):
    break_name = models.CharField(max_length=100, choices=break_options)
    posted_by = models.ForeignKey(User, related_name='breaks')
    
    def get_break_name(self):
        for b in break_options:
            if b[0] == self.break_name:
                return b[1]
        return self.break_name
        
    
class Product(Entry):
    posted_by = models.ForeignKey(User, related_name='products')
    
    
class Discussion(Entry):
    posted_by = models.ForeignKey(User, related_name='discussions')
    votesup = models.IntegerField(default=0)
    votesdown = models.IntegerField(default=0)
    
    def get_votes(self):
        return self.votes.filter(vote=1).count() - self.votes.filter(vote=0).count()
            

class Book(Entry):
    posted_by = models.ForeignKey(User, related_name='books')
    category = models.CharField(max_length=25, choices=category_options)

class Event(Entry):
    date = models.DateField()
    location = models.CharField(max_length=100)
    posted_by = models.ForeignKey(User, related_name='events')


class Transportation(Entry):
    date = models.DateField()
    posted_by = models.ForeignKey(User, related_name='transportation')
       
 


class Vote(models.Model):
    discussion = models.ForeignKey(Discussion, related_name='votes')
    user = models.ForeignKey(User, related_name='votes')
    time = models.DateTimeField()
    vote = models.SmallIntegerField()




    

##forms 
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    
    def clean(self):
        cleaned_data = self.cleaned_data
        email = cleaned_data.get("email")
        if email:
            i = email.rfind(".")
            if (email[i:] != ".edu"):
                raise forms.ValidationError("Must use .edu email")
        
        return cleaned_data
    
class NewUserForm(LoginForm):
    firstname = forms.CharField(max_length=30)
    lastname = forms.CharField(max_length=30)
    
#to contact a specific user    
class UserContactForm(forms.Form):
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)
  

class AddForm(forms.Form):
    title = forms.CharField(max_length=100)
    desc = forms.CharField(widget=forms.Textarea)
    
class BreakAddForm(AddForm):
    break_name = forms.ChoiceField(choices=break_options)

class ProductAddForm(AddForm):
    pass

class DiscussionAddForm(AddForm):
    pass

class BookAddForm(AddForm):
    category = forms.ChoiceField(choices=category_options)
    
class EventAddForm(AddForm):
    date = forms.DateField()
    location = forms.CharField(max_length=100)
    
class TransportationAddForm(AddForm):
    date = forms.DateField()
      
    
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
