from swapr.classifieds.models import User, Comment, Break, BreakComment, Entry
from swapr.classifieds.models import Product, Discussion, Book, View
from swapr.classifieds.models import Event, Transportation, Student
from swapr.classifieds.models import BreakAddForm, BookComment, BookAddForm, CommentForm
from swapr.classifieds.models import DiscussionComment, EventComment, ProductComment, TransportationComment
from swapr.classifieds.models import ProductAddForm, DiscussionAddForm, EventAddForm, TransportationAddForm
from swapr.classifieds.models import LoginForm, NewUserForm, Vote, UserContactForm, category_options

import datetime, random, sha
from django.template.response import TemplateResponse, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.core import serializers
from django.http import Http404
from django.core.mail import send_mail

from swapr import settings

#static about view
def about(request):
    return TemplateResponse(request, 'about.html')

def home(request):
    #if (request.user.is_authenticated()):
        return TemplateResponse(request, 'home.html')
    #else:
    #    return redirect('/login/')

def login(request):
    if (request.method == 'POST'):
        form = LoginForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            email = data['email']
            i = email.rfind("@")
            username = email[0:i]
            password = data['password']
            
            print username + " " + password
            
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    return redirect('/')
    
    form = LoginForm()
    return TemplateResponse(request, 'login.html', 
                            {'email':form['email'], 'password':form['password']})

def login_error(request):
    return TemplateResponse(request, 'login.html')


def new_user(request):
    if (request.method == 'POST'):
        form = NewUserForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            email = data['email']
            i = email.rfind("@")
            username = email[0:i]
            password = data['password']
            fname = data['firstname']
            lname = data['lastname']
            
            print fname + " " + lname + " " + username + " " + password
           
            u = User.objects.create_user(username, email, password)
            u.first_name = fname
            u.last_name = lname
            u.is_active = False
            u.save()
            
            salt = sha.new(str(random.random())).hexdigest()[:5]
            activation_key = sha.new(salt+u.username).hexdigest()
            key_expires = datetime.datetime.today() + datetime.timedelta(2)
            
            new_student = Student(
                    user=u,
                    activation_key=activation_key,
                    key_expires=key_expires)
            new_student.save()
            
            
            confirmation_url = settings.DOMAIN+"confirmation/" + new_student.activation_key
            email_subject = "Woo hoo!! Please confirm your account at CC Swapr!"
            email_body = "Please visit the following url to confirm your account \n" + confirmation_url
    
            print (email_body)
            send_mail(email_subject,
                      email_body,
                      'barron.trevor@gmail.com',
                      [new_student.user.email])        
            
            return redirect("/")
    
    form = NewUserForm()
    return TemplateResponse(request, 'new_user.html', 
                            {'email':form['email'], 'password':form['password'], 'password_confirm':form['password_confirm'],
                             'firstname':form['firstname'], 'lastname':form['lastname']})


def logout(request):
    auth_logout(request)
    return redirect('/')

def confirm_account(request, key):
    if request.user.is_authenticated():
        return redirect('/')
    
    print (key)
    student = get_object_or_404(Student, activation_key=key)
    
    user_account = student.user
    user_account.is_active = True
    user_account.save()
    
    print(student.user.username + " " + student.user.password)
    print(user_account.username + " " + user_account.password)
    
    #uname=user_account.username
    #passwd=user_account.password
    #user=authenticate(username=uname, password=passwd)
    #if user is not None:
    #    if user.is_active:
    #        auth_login(request, user)
            
    return redirect('/')
   

def contact_user(request, uname):
    receiver = User.objects.get(username=uname)
    sender = request.user
    
    if request.method == 'POST':
        form = UserContactForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            subject = data['subject']
            message = data['message']
            emailPrivateMessage(receiver, sender, subject, message)
        
        return redirect('/')
    
    form = UserContactForm()
    return TemplateResponse(request, 'contact_user.html', 
                            {'usr':receiver, 'subject':form['subject'], 'message':form['message']})
 

#to avoid void ct increments on page reloads and post requests
#store valid view if they haven't visited the page in the last day
def logView(request, item):
    if not request.user.is_anonymous:
        usr = request.user
        print "trying to query"
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        if item.views.filter(user=usr, time__gt=yesterday, unique=True).exists():
            print "view exists"
            view = View(
                user = usr,
                time = datetime.datetime.now(),
                entry = item,    
                unique = False
            )
            view.save()
        else:
            print "view does not exist"
            view = View(
                user = usr,
                time = datetime.datetime.now(),
                entry = item,    
                unique = True
            )
            view.save()
    #else not logged in
    
import smtplib
import string

def emailPoster(request, obj, url_trail): 
    post_user = obj.posted_by
    post_user_email = post_user.email
    auth_user = request.user
    auth_user_name = auth_user.first_name + " " + auth_user.last_name
    url = settings.DOMAIN+"/"+url_trail
    
    host = settings.DOMAIN #'127.0.0.1:8000'
    subject = auth_user_name + " commented on your post!"
    to = post_user_email
    sender = "barron.trevor@gmail.com"
    text = "Please visit the following url to respond:\n" + url
    body = string.join((
            "From: %s" % sender,
            "To: %s" % to,
            "Subject: %s" % subject,
            "",
            text
            ), "\r\n")
    print(body)
    #server = smtplib.SMTP(host)
    #server.sendmail(sender, [to], body)
    #server.quit()
    
    
    
def emailPrivateMessage(receiver, sendr, subject, message):
    host = settings.DOMAIN #'127.0.0.1:8000'
    
    subject = sendr.first_name + " " + sendr.last_name + " sent you a message" 
    to = receiver.email
    sender = sendr.email
    text = "See your message below"
    body = string.join((
            "From: %s" % sender,
            "To: %s" % to,
            "Subject: %s" % subject,
            "",
            text
        ), "\r\n")
    
    print(body)
    #server = smtplib.SMTP(host)
    #server.sendmail(sender, [to], body)
    #server.quit()
    
    
#upvote = 1
#downvote = 0
def vote(request, v, disc_id):
    u = request.user
    disc = Discussion.objects.get(id=disc_id)
    t = datetime.datetime.now()
    voteobj = Vote(
        discussion=disc,
        user=u,
        time=t,
        vote=v
    )
    voteobj.save()
    print (v)
    
    return HttpResponse("success")
    
   
   
   
   
    
#details
def break_detail(request, break_id):
    break_detail = Break.objects.get(id=break_id)
    comments = break_detail.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            c_comment = data['comment']
            c_date = datetime.datetime.now()
            c_left_by = request.user
            c_left_on = Break.objects.get(id=break_id)
            c = BreakComment(
                comment=c_comment,
                date=c_date,
                left_by=c_left_by,
                left_on=c_left_on)
            c.save()
    else:
        logView(request, break_detail)
        
    form = CommentForm()
    return TemplateResponse(request, 'details/break_detail.html',{'break':break_detail, 'form':form['comment'], 'comments':comments})


def book_detail(request, book_id):
    book_detail = Book.objects.get(id=book_id)
    comments = book_detail.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            c_comment = data['comment']
            c_date = datetime.datetime.now()
            c_left_by = request.user
            c_left_on = Book.objects.get(id=book_id)
            c = BookComment(
                comment=c_comment,
                date=c_date,
                left_by=c_left_by,
                left_on=c_left_on)
            c.save()
            emailPoster(request, book_detail, "books/"+book_id)
    else:
        logView(request, book_detail)
        
    form = CommentForm()
    return TemplateResponse(request, 'details/book_detail.html',
                            {'book':book_detail, 'form':form['comment'], 'comments':comments})

def discussion_detail(request, disc_id):
    disc_detail = Discussion.objects.get(id=disc_id)
    comments = disc_detail.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            c_comment = data['comment']
            c_date = datetime.datetime.now()
            c_left_by = request.user
            c_left_on = Discussion.objects.get(id=disc_id)
            c = DiscussionComment(
                comment=c_comment,
                date=c_date,
                left_by=c_left_by,
                left_on=c_left_on)
            c.save()
    else:
        logView(request, disc_detail)
        
    form = CommentForm()
    return TemplateResponse(request, 'details/discussion_detail.html',
                            {'disc':disc_detail, 'form':form['comment'], 'comments':comments})

def event_detail(request, event_id):
    event_detail = Event.objects.get(id=event_id)
    comments = event_detail.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            c_comment = data['comment']
            c_date = datetime.datetime.now()
            c_left_by = request.user
            c_left_on = Event.objects.get(id=event_id)
            c = EventComment(
                comment=c_comment,
                date=c_date,
                left_by=c_left_by,
                left_on=c_left_on)
            c.save()
    else:
        logView(request, event_detail)
        
    form = CommentForm()
    return TemplateResponse(request, 'details/event_detail.html',
                            {'event':event_detail, 'form':form['comment'], 'comments':comments})

def product_detail(request, prod_id):
    prod_detail = Product.objects.get(id=prod_id)
    comments = prod_detail.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            c_comment = data['comment']
            c_date = datetime.datetime.now()
            c_left_by = request.user
            c_left_on = Product.objects.get(id=prod_id)
            c = ProductComment(
                comment=c_comment,
                date=c_date,
                left_by=c_left_by,
                left_on=c_left_on)
            c.save()
    else:
        logView(request, prod_detail)
        
    form = CommentForm()
    return TemplateResponse(request, 'details/product_detail.html',
                            {'product':prod_detail, 'form':form['comment'], 'comments':comments})

def transportation_detail(request, trans_id):
    trans_detail = Transportation.objects.get(id=trans_id)
    comments = trans_detail.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            c_comment = data['comment']
            c_date = datetime.datetime.now()
            c_left_by = request.user
            c_left_on = Transportation.objects.get(id=trans_id)
            c = TransportationComment(
                comment=c_comment,
                date=c_date,
                left_by=c_left_by,
                left_on=c_left_on)
            c.save()
    else:
        logView(request, trans_detail)
        
    form = CommentForm()
    return TemplateResponse(request, 'details/trans_detail.html',
                            {'trans':trans_detail, 'form':form['comment'], 'comments':comments})







#additions
def break_add(request):
    if request.method == 'POST':
        form = BreakAddForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            b_name = data['break_name']
            b_title = data['title']
            b_text = data['desc']
            
            user = request.user 
            b = user.breaks.create(
                break_name = b_name,
                title = b_title,
                description = b_text,
            )
        
            return redirect(b.get_absolute_url())
    
    form = BreakAddForm()
    return TemplateResponse(request, 'add/break_add.html',
                            {'title':form['title'], 'desc':form['desc'], 'break':form['break_name']})


def book_add(request):
    if request.method == 'POST':
        form = BookAddForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            b_title = data['title']
            b_text = data['desc'] 
            cat = data['category']
            
            user = request.user 
            b = user.books.create(
                title = b_title,
                description = b_text,
                category = cat,
            )
                
            return redirect(b.get_absolute_url())
    form = BookAddForm()
    return TemplateResponse(request, 'add/book_add.html',
                            {'title':form['title'], 'desc':form['desc'], 'category':form['category']})

def product_add(request):
    if not request.user.is_authenticated():
        return redirect('/login/')
    if request.method == 'POST':
        #student = currently authenticated student
        form = ProductAddForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            p_title = data['title']
            p_text = data['desc']   
            
            user = request.user 
            b = user.products.create(
                title = p_title,
                description = p_text,
            )
            
            return redirect(b.get_absolute_url())
    
    form = ProductAddForm()
    return TemplateResponse(request, 'add/product_add.html',
                            {'title':form['title'], 'desc':form['desc']})

def discussion_add(request):
    if request.method == 'POST':
        form = DiscussionAddForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            p_title = data['title']
            p_text = data['desc']   
            
            user = request.user 
            p = user.discussions.create(
                title = p_title,
                description = p_text,
            )
            
            return redirect(p.get_absolute_url())
    
    form = DiscussionAddForm()
    return TemplateResponse(request, 'add/discussion_add.html',
                            {'title':form['title'], 'desc':form['desc']})


def event_add(request):
    if not request.user.is_authenticated():
        return redirect('/login/')
    if request.method == 'POST':
        #student = currently authenticated student
        form = EventAddForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            p_title = data['title']
            p_desc = data['desc']
            p_date = data['date']
            p_location = data['location']
               
            user = request.user 
            p = user.events.create(
                title = p_title,
                description = p_desc,
                location = p_location,
                date = p_date
            )
            
            return redirect(p.get_absolute_url())
    form = EventAddForm()
    return TemplateResponse(request, 'add/event_add.html',
                            {'title':form['title'], 'desc':form['desc'], 'date':form['date'], 'location':form['location']})

def transportation_add(request):
    if not request.user.is_authenticated():
        return redirect('/login/')
    if request.method == 'POST':
        #student = currently authenticated student
        form = TransportationAddForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            p_title = data['title']
            p_desc = data['desc']
            p_date = data['date']
              
              
            user = request.user 
            p = user.transportation.create(
                title = p_title,
                description = p_desc,
                date = p_date
            )
#            p.get_absolute_url()
            
            return redirect(p.get_absolute_url())
    
    form = TransportationAddForm()
    return TemplateResponse(request, 'add/transportation_add.html',
                            {'title':form['title'], 'desc':form['desc'], 'date':form['date']})






#lists
def paginate(request, paginator):
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        objs = paginator.page(page)
    except (EmptyPage, InvalidPage):
        objs = paginator.page(paginator.num_pages)
    return objs

def breaks(request):
    break_list = Break.objects.all()
    paginator = Paginator(break_list, 5)
    
    breaks = paginate(request, paginator)
    
    return TemplateResponse(request, 'lists/breaks.html',
            {'breaks':breaks, 'title': "Breaks", 'url':"breaks"})

def products(request):
    product_list = Product.objects.all()
    paginator = Paginator(product_list, 5)
    
    products = paginate(request, paginator)
    
    return TemplateResponse(request, 'lists/sales.html',
            {'sales':products, 'title': "Sales", 'url':"sales"})
    
    
def books(request):
    book_list = Book.objects.all()
    paginator = Paginator(book_list, 5)
    
    books = paginate(request, paginator)
    
    return TemplateResponse(request, 'lists/books.html',
            {'books':books, 'title': "Books", 'categories':category_options, 'url':"books", 'category':False})


def book_category(request, cat):
    book_list = Book.objects.filter(category=cat)
    paginator = Paginator(book_list, 5)
    
    books = paginate(request, paginator)
    
    return TemplateResponse(request, 'lists/books.html',
            {'books':books, 'title': "Books", 'categories':category_options, 'url':"books", 'category':True})

def events(request):
    event_list = Event.objects.all()
    paginator = Paginator(event_list, 5)
    
    events = paginate(request, paginator)
    
    return TemplateResponse(request, 'lists/events.html',
            {'events':events, 'title': "Events", 'url':"events"})


def events_json(request):
    events = Event.objects.all()
    json = "["
    for i in range(len(events)):
        e = events[i]
        json += "{" + "\"id\":" + str(e.id) + ","
        json += "\"title\":" + "\"" + e.title + "\"" + ","
        json += "\"start\":" + "\"" +str(e.date.year)+"-"+str(e.date.month)+"-"+str(e.date.day) + "\","
        json += "\"url\":" + "\"" + "/events/"+str(e.id) + "\""
        json += "}"
        if (i != len(events)-1):
            json += ","
    json += "]"  
    return HttpResponse(json)  

def events_calendar(request):
    return TemplateResponse(request, 'lists/events_calendar.html', 
            {'title':"Events", 'url':"events"})

def discussions(request):
    disc_list = Discussion.objects.all()
    paginator = Paginator(disc_list, 5)
    
    discs = paginate(request, paginator)
    
    return TemplateResponse(request, 'lists/discussions.html',
            {'discussions':discs, 'title': "Discussions", "url":"discussions"})

def transportation(request):
    trans_list = Transportation.objects.all()
    paginator = Paginator(trans_list, 5)
    
    trans = paginate(request, paginator)
    
    return TemplateResponse(request, 'lists/transportation.html',
            {'trans':trans, 'title': "Transportation", 'url':"transportation"})






# search functions
def event_search(request):
    pass

def break_search(request):
    pass

def product_search(research):
    pass

def book_search(research):
    pass

def discussion_search(research):
    pass

def transportation_search(request):
    pass



#qr code
import urllib, json
def event_qrcode(request, event_id):
    auth_user = request.user
    event = Event.objects.get(id=event_id)
    poster = event.posted_by
    if (auth_user != poster):
        raise Http404
    
    qrurl = "https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl="
    qrurl += urllib.quote("http://"+settings.DOMAIN+"/events/"+str(event_id)+"/")
    return TemplateResponse(request, 'details/event_qrcode.html',
                            {'qrsrc':qrurl, 'event':event})
    
def event_map_reverse_geocode(request):
    if not request.is_ajax():
        raise Http404
    
    lat = request.GET.get('lat', '1')
    lng = request.GET.get('lng', '1')
    url='http://maps.googleapis.com/maps/api/geocode/json?latlng='+str(lat)+','+str(lng)+'&sensor=false' 
    geo_json = urllib.urlopen(url).read()
    
    parsed_json = json.loads(geo_json)
    
    if (parsed_json['status'] == "OK"):
        formatted_address = parsed_json['results'][0]['formatted_address']
        return HttpResponse(formatted_address)
    
    return HttpResponse("failure")
    
    
