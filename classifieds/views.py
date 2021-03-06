from swapr.classifieds.models import *

import datetime, random, sha, string
from django.template.response import TemplateResponse, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.http import Http404
from django.core.mail import send_mail
from django.db.models import Q

from swapr import settings
    

#static about view
def about(request):
    return TemplateResponse(request, 'about.html')

def home(request):
    return TemplateResponse(request, 'home.html')


def login(request):
    form = LoginForm()
    if (request.method == 'POST'):
        form = LoginForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            email = data['email']
            username = form.get_user_name(email)
            password = data['password']
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    return redirect('/')
                else:
                    form.confirm_error()
            else:
                form.password_error()
                        
    return TemplateResponse(request, 'login.html', {'form':form})
        #{'email':form['email'], 'password':form['password']})

def login_error(request):
    return TemplateResponse(request, 'login.html')


def new_user(request):
    form = NewUserForm()
    if (request.method == 'POST'):
        form = NewUserForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            email = data['email']
            
            username = form.get_user_name(email)
            password = data['password']
            fname = data['firstname']
            lname = data['lastname']
            
            print fname + " " + lname + " " + username + " " + password
           
            if not User.objects.filter(username=username).exists():
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
                        key_expires=key_expires
                )
                new_student.save()
                
                confirmation_url = settings.DOMAIN+"confirmation/" + new_student.activation_key
                email_subject = "Woo hoo!! Confirm your account at CC Swapr!"
                email_body = "Hello " + new_student.user.first_name + ", \n\n"
                email_body += "Please visit the following URL to confirm your account: \n"
                email_body += confirmation_url + "\n\n"
                email_body += "Have a suggestion? Let us know at "+settings.DOMAIN+"feedback/. \n\n"
                email_body += "Thanks,\nThe CC Swapr Team (Trevor and Stanley :D )"
        
                print (email_body)
                send_mail(email_subject,
                          email_body,
                          settings.DEFAULT_FROM_EMAIL,
                          [new_student.user.email], 
                          fail_silently=True)        
                
                return redirect("/thanks/")
            else:
                form.user_exists_error()
    
    return TemplateResponse(request, 'new_user.html', {'form':form})


def logout(request):
    auth_logout(request)
    return redirect('/')

def confirm_account(request, key):
    if request.user.is_authenticated():
        return redirect('/')
    
    print (key)
    student = get_object_or_404(Student, activation_key=key)
    
    #current_time = datetime.datetime.now()
    #if (current_time < student.key_expires):
    #for now I'm not going to worry about a time limit
    #because then I'd have to deal with people registering twice
    #i guess I could just delete the current reference
    
    user_account = student.user
    user_account.is_active = True
    user_account.save()
    
    print(student.user.username + " " + student.user.password)
    print(user_account.username + " " + user_account.password)
    
    uname=user_account.username
    passwd=user_account.password
    user=authenticate(username=uname, password=passwd)
    if user is not None:
        if user.is_active:
            auth_login(request, user)
            
    return redirect('/')


def password_reset_email(request):
    form = PasswordResetEmailForm()
    if (request.method == 'POST'):
        form = PasswordResetEmailForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            email = data['email']
            
            if not User.objects.filter(email=email).exists():
                form.user_exists_error()
            else:
                u = User.objects.get(email=email)
                print u.get_full_name() + ": " + email

                salt = sha.new(str(random.random())).hexdigest()[:5]
                reset_key = sha.new(salt+u.username).hexdigest()
                
                student = u.student
                #Student.objects.get(user=u)
                student.reset_key = reset_key
                student.save()
                
                reset_url = settings.DOMAIN+"passwordreset_password/" + student.reset_key
                email_subject = "CC Swapr password reset!"
                email_body = "Hello " + u.first_name + ", \n\n"
                email_body += "Please visit the following URL to reset the password for your account: \n"
                email_body += reset_url + "\n\n"
                email_body += "Have a suggestion? Let us know at "+settings.DOMAIN+"feedback/. \n\n"
                email_body += "Thanks,\nThe CC Swapr Team (Trevor and Stanley :D )"
        
                print (email_body)
                send_mail(email_subject,
                          email_body,
                          settings.DEFAULT_FROM_EMAIL,
                          [email], 
                          fail_silently=True)        
                
                text = "An email has been sent to " + email + " so that you can reset your password"
                return TemplateResponse(request, 'password_reset_email.html', {'form':form, 'text':text})
            
    
    return TemplateResponse(request, 'password_reset_email.html', {'form':form, 'text':""})
    

def password_reset_password(request, key):
    form = PasswordResetPasswordForm()
    if not Student.objects.filter(reset_key=key).exists():
        raise Http404
    
    user = Student.objects.get(reset_key=key).user
    
    if (request.method == 'POST'):
        form = PasswordResetPasswordForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            p1 = data['password']
            
            if Student.objects.filter(reset_key=key).exists():
                student = Student.objects.get(reset_key=key)
                user = student.user
                user.set_password(p1)
                user.save()
                text = "Thank you, " + user.first_name + ", your password has been reset."
            else:
                text = "Sorry, " + user.first_name + ", the reset key is invalid. We could not reset your password."
            
            return TemplateResponse(request, 'password_reset_password.html', {'form':form, 'text':text})
    
    return TemplateResponse(request, 'password_reset_password.html', {'user':user, 'form':form, 'text':""})
    
    
def user_settings(request):
    form = SettingsForm()
    if (request.method == 'POST'):
        form = SettingsForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            m = data['major']
            user = request.user
            student = user.student
            student.major = m
            student.save()
        
            return TemplateResponse(request, 'settings/settings.html', {'form': form, 'valid': True})
        
    return TemplateResponse(request, 'settings/settings.html', {'form': form, 'valid':False})

def edit_user_settings(request):
    pass

def thanks(request):
    return TemplateResponse(request, 'thanks.html')
   

def feedback(request):
    form = FeedbackForm();
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            message = data['message']
            print (message)
            subject = "Feedback"
            receiver = "barron.trevor@gmail.com"
            send_mail(subject, message,
                      settings.DEFAULT_FROM_EMAIL,
                      [receiver],
                      fail_silently=True)
            
            return TemplateResponse(request, 'feedback.html', 
                                    {'message': form['message'], 'submitted':True})
    
    return TemplateResponse(request, 'feedback.html', 
                            {'message': form['message'], 'submitted':False})
    

def contact_user(request, uname):
    if (not request.user.is_authenticated()):
        raise Http404
    form = UserContactForm()
    receiver = User.objects.get(username=uname)
    if request.method == 'POST':
        form = UserContactForm(request.POST)
        if (form.is_valid()):
            data = form.clean()
            subject = data['subject']
            message = request.user.get_full_name() + " sent you this message on CC Swapr: \n" + data['message'] + "\n\n"
            message += "Have a suggestion? Let us know at "+settings.DOMAIN+"feedback/. \n\n"
            message += "Thanks,\nThe CC Swapr Team (Trevor and Stanley)"
            print (message)
             
            send_mail(subject,
                      message,
                      settings.DEFAULT_FROM_EMAIL,
                      [receiver.email],
                      fail_silently=True)
            
            m = PrivateMessage(
                    student=Student.objects.get(user=User.objects.get(username=uname)),
                    subject=subject,
                    message=message
                    )
            m.save()
            
        
    
    return TemplateResponse(request, 'contact_user.html', {'form':form, 'usr':receiver, 'submitted':False})
 

#to avoid void ct increments on page reloads and post requests
#store valid view if they haven't visited the page in the last day
#stores view either way but leaves unique=False if soon
def log_view(request, item):
    if request.user.is_authenticated:
        usr = request.user
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        if item.views.filter(user=usr, time__gt=yesterday, unique=True).exists():
            #print "view exists"
            view = View(
                user = usr,
                time = datetime.datetime.now(),
                entry = item,    
                unique = False
            )
            view.save()
        else:
            #print "view does not exist"
            view = View(
                user = usr,
                time = datetime.datetime.now(),
                entry = item,    
                unique = True
            )
            view.save()
    
    
def email_poster(request, obj): 
    post_user = obj.posted_by
    post_user_email = post_user.email
    auth_user = request.user
    auth_user_name = auth_user.get_full_name()
    url = settings.DOMAIN+obj.get_absolute_url()
    
    subject = "CC Swapr: " + auth_user_name + " commented on your post!"
    receiver = post_user_email
    message = "Please visit the following url to respond:\n" + url + "\n\n"
    message += "Have a suggestion? Let us know at "+settings.DOMAIN+"feedback/. \n\n"
    message += "Thanks,\nThe CC Swapr Team (Trevor and Stanley)"
    print(message)
    
    send_mail(subject,
              message,
              settings.DEFAULT_FROM_EMAIL,
              [receiver])
    
    
    
def email_private_message(receiver, sendr, subject, message):
    subject = sendr.get_full_name() + " sent you a message on CC Swapr" 
    to = receiver.email
    text = "See your message below: \n\n " + message
        
    print(message)
    send_mail(subject,
              text,
              settings.DEFAULT_FROM_EMAIL,
              [to])
    
    
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
    

def item_completed(request, item_type, item_id):
    if (item_type == "breaks"):
        item = Break.objects.get(id=item_id)
    elif (item_type == "books"):
        item = Book.objects.get(id=item_id)
    elif (item_type == "suggestions"):
        item = Discussion.objects.get(id=item_id)
    elif (item_type == "events"):
        item = Event.objects.get(id=item_id)
    elif (item_type == "sales"):
        item = Product.objects.get(id=item_id)
    elif (item_type == "rides"):
        item = Transportation.objects.get(id=item_id)
    else:
        raise Http404
        
    item.published = False;
    item.save()
    
    return redirect("/"+item.get_absolute_url())
    
    
def delete_comment(request, item_type, item_id, comment_id):
    if (item_type == "breaks"):
        item = Break.objects.get(id=item_id)
    elif (item_type == "books"):
        item = Book.objects.get(id=item_id)
    elif (item_type == "discussions"):
        item = Discussion.objects.get(id=item_id)
    elif (item_type == "events"):
        item = Event.objects.get(id=item_id)
    elif (item_type == "sales"):
        item = Product.objects.get(id=item_id)
    elif (item_type == "rides"):
        item = Transportation.objects.get(id=item_id)
    else:
        raise Http404
    
    comment = Comment.objects.get(id=comment_id)
    comment.published=False
    comment.save()
    
    return redirect("/"+item.get_absolute_url())
    
#details
def break_detail(request, break_id):
    if not request.user.is_authenticated():
        return redirect('/login/')
    try:
        break_detail = Break.objects.get(id=break_id)
    except Break.DoesNotExist:
        raise Http404
    comments = break_detail.comments.filter(published=True)
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
            email_poster(request, break_detail)
    else:
        log_view(request, break_detail)
        
    form = CommentForm()
    return TemplateResponse(request, 'details/break_detail.html',
                            {'break':break_detail, 'form':form['comment'], 'comments':comments})


def book_detail(request, book_id):
    if not request.user.is_authenticated():
        return redirect('/login/')
    try:
        book_detail = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        raise Http404
    comments = book_detail.comments.filter(published=True)
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
            email_poster(request, book_detail)
    else:
        log_view(request, book_detail)
        
    form = CommentForm()
    return TemplateResponse(request, 'details/book_detail.html',
                            {'book':book_detail, 'form':form['comment'], 'comments':comments})

def discussion_detail(request, disc_id):
    if not request.user.is_authenticated():
        return redirect('/login/')
    try:
        disc_detail = Discussion.objects.get(id=disc_id)
    except Discussion.DoesNotExist:
        raise Http404
    comments = disc_detail.comments.filter(published=True)
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
            email_poster(request, disc_detail)
    else:
        log_view(request, disc_detail)
        
    form = CommentForm()
    return TemplateResponse(request, 'details/discussion_detail.html',
                            {'disc':disc_detail, 'form':form['comment'], 'comments':comments})

def event_detail(request, event_id):
    if not request.user.is_authenticated():
        return redirect('/login/')
    try:
        event_detail = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        raise Http404
    comments = event_detail.comments.filter(published=True)
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
            #email user with original post to notify
            email_poster(request, event_detail)
    else:
        log_view(request, event_detail)
        
    form = CommentForm()
    return TemplateResponse(request, 'details/event_detail.html',
                            {'event':event_detail, 'form':form['comment'], 'comments':comments})

def product_detail(request, prod_id):
    if not request.user.is_authenticated():
        return redirect('/login/')
    try:
        prod_detail = Product.objects.get(id=prod_id)
    except Product.DoesNotExist:
        raise Http404
    comments = prod_detail.comments.filter(published=True)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if (form.is_valid()):
            print ("valid comment")
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
            email_poster(request, prod_detail)
        else:
            print ("invalid comment")
    else:
        log_view(request, prod_detail)
        
    form = CommentForm()
    return TemplateResponse(request, 'details/product_detail.html',
                            {'product':prod_detail, 'form':form['comment'], 'comments':comments})

def transportation_detail(request, trans_id):
    if not request.user.is_authenticated():
        return redirect('/login/')
    try:
        trans_detail = Transportation.objects.get(id=trans_id)
    except Transportation.DoesNotExist:
        raise Http404
    comments = trans_detail.comments.filter(published=True)
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
            email_poster(request, trans_detail)
    else:
        log_view(request, trans_detail)
        
    form = CommentForm()
    return TemplateResponse(request, 'details/trans_detail.html',
                            {'trans':trans_detail, 'form':form['comment'], 'comments':comments})




#additions
def break_add(request):
    if not request.user.is_authenticated():
        return redirect('/login/')
    form = BreakAddForm()
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
        
            return redirect("/"+b.get_absolute_url())
    
    return TemplateResponse(request, 'add/break_add.html', {'form':form})


def book_add(request):
    if not request.user.is_authenticated():
        return redirect('/login/')
    form = BookAddForm()
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
                
            return redirect("/"+b.get_absolute_url())
    
    return TemplateResponse(request, 'add/book_add.html', {'form':form})


def product_add(request):
    if not request.user.is_authenticated():
        return redirect('/login/')
    form = ProductAddForm()
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
            
            return redirect("/"+b.get_absolute_url())
    
    return TemplateResponse(request, 'add/product_add.html', {'form': form})
#                            {'title':form['title'], 'desc':form['desc']})

def discussion_add(request):
    form = DiscussionAddForm()
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
            
            return redirect("/"+p.get_absolute_url())
    
    return TemplateResponse(request, 'add/discussion_add.html', {'form':form})


def event_add(request):
    if not request.user.is_authenticated():
        return redirect('/login/')
    form = EventAddForm()
    if request.method == 'POST':
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
            
            return redirect("/"+p.get_absolute_url())
    return TemplateResponse(request, 'add/event_add.html', {'form':form})
#                            {'title':form['title'], 'desc':form['desc'], 'date':form['date'], 'location':form['location']})

def transportation_add(request):
    if not request.user.is_authenticated():
        return redirect('/login/')
    form = TransportationAddForm()
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

            return redirect("/"+p.get_absolute_url())
    
    return TemplateResponse(request, 'add/transportation_add.html', {'form':form})






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
    break_list = Break.objects.filter(
                                expiration__gte=datetime.datetime.now()
                             ).filter(
                                published=True
                             )
    paginator = Paginator(break_list, 10)
    
    breaks = paginate(request, paginator)
    
    return TemplateResponse(request, 'lists/breaks.html',
            {'breaks':breaks, 'title': "Breaks", 'url':"breaks"})

def products(request):
    product_list = Product.objects.filter(
                                expiration__gte=datetime.datetime.now()
                             ).filter(
                                published=True
                             )
    paginator = Paginator(product_list, 10)
    
    products = paginate(request, paginator)
    
    return TemplateResponse(request, 'lists/sales.html',
            {'sales':products, 'title': "For Sale & Wanted", 'url':"sales"})
    
    
def books(request):
    book_list = Book.objects.filter(
                                expiration__gte=datetime.datetime.now()
                             ).filter(
                                published=True
                             )
    paginator = Paginator(book_list, 10)
    
    books = paginate(request, paginator)
    
    return TemplateResponse(request, 'lists/books.html',
            {'books':books, 'title': "Books", 'categories':category_options, 'url':"books", 'category':False})


def book_category(request, cat):
    book_list = Book.objects.filter(
                                expiration__gte=datetime.datetime.now()
                             ).filter(
                                published=True
                             ).filter(
                                category=cat
                             )
    paginator = Paginator(book_list, 10)
    
    books = paginate(request, paginator)
    
    return TemplateResponse(request, 'lists/books.html',
            {'books':books, 'title': "Books", 'categories':category_options, 'url':"books", 'category':True})

def events(request):
    event_list = Event.objects.filter(
                                expiration__gte=datetime.datetime.now()
                             ).filter(
                                published=True
                             )
    paginator = Paginator(event_list, 10)
    
    events = paginate(request, paginator)
    
    return TemplateResponse(request, 'lists/events.html',
            {'events':events, 'title': "Events", 'url':"events"})


def events_json(request):
    events = Event.objects.filter(
                                expiration__gte=datetime.datetime.now()
                             ).filter(
                                published=True
                             )
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
            {'title':"Events Calendar", 'url':"events"})

def discussions(request):
    disc_list = Discussion.objects.filter(
                                expiration__gte=datetime.datetime.now()
                             ).filter(
                                published=True
                             )
    paginator = Paginator(disc_list, 10)
    
    discs = paginate(request, paginator)
    
    return TemplateResponse(request, 'lists/discussions.html',
            {'discussions':discs, 'title': "Suggestions", "url":"suggestions"})

def transportation(request):
    trans_list = Transportation.objects.filter(
                                expiration__gte=datetime.datetime.now()
                             ).filter(
                                published=True
                             )
    paginator = Paginator(trans_list, 10)
    
    trans = paginate(request, paginator)
    
    return TemplateResponse(request, 'lists/transportation.html',
            {'trans':trans, 'title': "Rides", 'url':"rides"})



# search functions
def event_search(request):
    try:
        query = str(request.GET.get('q', '1'))
    except ValueError:
        query = ""
    
    if (query == ""):
        redirect("/events/")
    else:
        events_list = Event.objects.filter(
           Q(title__contains=query) | 
           Q(description__contains=query)
        )
        paginator = Paginator(events_list, 10)        
        events = paginate(request, paginator)
        
        return TemplateResponse(request, 'lists/events.html',
                {'events':events, 'title': "Events", 'url':"events"})
 

def break_search(request):
    try:
        query = str(request.GET.get('q', '1'))
    except ValueError:
        query = ""
    
    if (query == ""):
        redirect("/breaks/")
    else:
        break_list = Break.objects.filter(
            Q(title__contains=query) | 
            Q(description__contains=query) | 
            Q(break_name__contains=query)
        )
        
        paginator = Paginator(break_list, 10)        
        breaks = paginate(request, paginator)
        
        return TemplateResponse(request, 'lists/breaks.html',
                {'breaks':breaks, 'title': "Breaks", 'url':"breaks"})


def product_search(request):
    try:
        query = str(request.GET.get('q', '1'))
    except ValueError:
        query = ""
    
    if (query == ""):
        redirect("/sales/")
    else:
        product_list = Product.objects.filter(
            Q(title__contains=query) | 
            Q(description__contains=query)
        )
        
        paginator = Paginator(product_list, 10)        
        sales = paginate(request, paginator)
        
        return TemplateResponse(request, 'lists/sales.html',
                {'sales':sales, 'title': "Sales", 'url':"sales"})

        
def book_search(request):
    try:
        query = str(request.GET.get('q', '1'))
    except ValueError:
        query = ""
        
    if (query == ""):
        print("empty query")
        redirect("/books/")
    else:
        book_list = Book.objects.filter(
            Q(title__contains=query) | Q(description__contains=query)
        )
        
        paginator = Paginator(book_list, 10)        
        books = paginate(request, paginator)
        return TemplateResponse(request, 'lists/books.html',
                {'books':books, 'title': "Books", 'categories':category_options, 'url':"books", 'category':True})

def discussion_search(request):
    try:
        query = str(request.GET.get('q', '1'))
    except ValueError:
        query = ""
    
    if (query == ""):
        redirect("/discussions/")
    else:
        disc_list = Discussion.objects.filter(
            Q(title__contains=query) | Q(description__contains=query)
        )
        
        paginator = Paginator(disc_list, 10)        
        discs = paginate(request, paginator)
        return TemplateResponse(request, 'lists/discussions.html',
                {'discussions':discs, 'title': "Discussions", 'url':"discussions"})


def transportation_search(request):
    try:
        query = str(request.GET.get('q', '1'))
    except ValueError:
        query = ""
    
    if (query == ""):
        redirect("/transportation/")
    else:
        trans_list = Transportation.objects.filter(
            Q(title__contains=query) | Q(description__contains=query)
        )
        
        paginator = Paginator(trans_list, 10)        
        trans = paginate(request, paginator)
        return TemplateResponse(request, 'lists/transportation.html',
                {'trans':trans, 'title': "Rides", 'url':"rides"})



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
    
    
