from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import ListView,DetailView
import random, os
from django.core.files.storage import FileSystemStorage
from datetime import datetime
from django.db import connection
from django.http import JsonResponse
from django.db.models import Q


# Create your views here.

def login_home(request):

    return render(request,'login_home.html')

def logout(request):
    request.session.clear()
    return redirect(login_home)

# def login(request):
#     if request.method == 'POST':
#         idname = request.POST['name']
#         password = request.POST['password']
#         print(idname,password)
#
#         cursor = connection.cursor()
#         cursor.execute("select * from login where admin_id = '"+str(idname)+"' and password = '"+str(password)+"'")
#         admin = cursor.fetchone()
#         cursor.execute("select * from tour_agency where agency_id ='"+str(idname)+"' and password ='"+str(password)+"' and status = 'approved' ")
#         tagency = cursor.fetchone()
#         cursor.execute("select * from vehicle_agency where vehicle_agency_id ='"+str(idname)+"' and password ='"+str(password)+"' and status = 'approved' ")
#         vagency = cursor.fetchone()
#         if admin == None:
#             if tagency == None:
#                 if vagency == None:
#                     return HttpResponse("<script>alert('invalid login');window.location='../login';</script>")
#                 else:
#                     request.session["vagencyid"] = idname
#                     return redirect('vindex')
#             else:
#                 request.session["tagencyid"] = idname
#                 return redirect('tindex')
#         else:
#             request.session["adminid"] = idname
#             return redirect('adminindex')
#     else:
#         return render(request,'login.html')

def signin(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        cursor = connection.cursor()
        cursor.execute("delete from otp where phone ='"+str(phone)+"' ")
        otp = random.randint(1000, 9999)

        otp =str(otp)
        request.session["regphone"] = phone
        cursor.execute("insert into otp values(null, '" + str(phone) + "', '" + otp + "')")
        return HttpResponse("<script>alert('your otp is "+otp+"'); window.location = '../validate_otp';</script>")

    return render(request, 'register.html')
def validate(request):
    phone = request.session["regphone"]
    if request.method == 'POST':
        otp = request.POST['otp']
        cursor = connection.cursor()
        cursor.execute("select * from otp where phone ='"+str(phone)+"' and otp ='"+str(otp)+"'")
        data = cursor.fetchone()
        if data == None:
            cursor.execute("delete from otp where phone='" + str(phone) + "'")
            return HttpResponse("<script>alert('invalid otp');window.location='../signin';</script>")
        else:
            cursor = connection.cursor()
            cursor.execute("select * from chat_account where phone ='"+str(phone)+"'")
            data = cursor.fetchone()
            cursor.execute("delete from otp where phone='" + str(phone) + "'")
            if data == None:
                return redirect(account_details)

            return redirect('account_home')

    return render(request, 'validateotp.html')

def account_details(request):
    phone = request.session["regphone"]
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        address = request.POST['address']
        cursor = connection.cursor()
        cursor.execute("delete from otp where phone ='" + str(email) + "' ")
        otp = random.randint(1000, 9999)

        otp = str(otp)
        request.session["name"] = name
        request.session["address"] = address
        request.session["email"] = email
        cursor.execute("insert into otp values(null, '" + str(email) + "', '" + otp + "')")
        return HttpResponse("<script>alert('your email otp is " + otp + "'); window.location = '../validate_email';</script>")


    return render(request, 'add_account_details.html')


def validate_email(request):
    phone = request.session["regphone"]
    email = request.session["email"]
    if request.method == 'POST':
        otp = request.POST['otp']
        cursor = connection.cursor()
        cursor.execute("select * from otp where phone ='"+str(email)+"' and otp ='"+str(otp)+"'")
        data = cursor.fetchone()

        if data == None:
            cursor.execute("delete from otp where phone ='" + str(email) + "' ")
            return HttpResponse("<script>alert('invalid otp');window.location='../signin';</script>")
        else:
            cursor.execute("delete from otp where phone ='" + str(email) + "' ")
            name = request.session["name"]
            address = request.session["address"]
            cursor.execute("insert into chat_account values(null,'" + phone + "','"+str(name)+"','"+str(email)+"', '"+str(address)+"', 'null.png'  )")
            return redirect(account_home)



    return render(request,'validatemail.html')

def account_home(request):
    phone = request.session["regphone"]
    cursor = connection.cursor()
    cursor.execute("select * from chat_account where phone = '" + str(phone) + "' ")
    data = cursor.fetchone()
    return render(request,'index.html',{'profile':data})

def profile(request):
    phone = request.session["regphone"]
    cursor = connection.cursor()
    cursor.execute("select * from chat_account where phone = '"+str(phone)+"' ")
    data = cursor.fetchone()
    return render(request, 'view_profile.html',{'profile':data})

def updatepic(request):
    phone = request.session["regphone"]
    cursor = connection.cursor()
    cursor.execute("select * from chat_account where phone ='" + str(phone) + "'")
    data = cursor.fetchone()
    if request.method == "POST" and request.FILES['upload']:
        icon = request.FILES['upload']
        upload = request.FILES['upload']
        original_filename, file_extension = os.path.splitext(upload.name)
        current_time = datetime.now().strftime('%Y%m%d%H%M%S')

        # desired_filename = '"'+phone+'"'+'"'+current_time+'"'+'"'+file_extension+'"'
        desired_filename = f'{phone}{current_time}{file_extension}'
        fss = FileSystemStorage()
        file = fss.save(desired_filename, upload)
        file_url = fss.url(file)

        cursor.execute("update chat_account set pic ='"+str(desired_filename)+"' where phone ='"+str(phone)+"'")
        return redirect(profile)
    return render(request,'update_pic.html',{'profile': data})

def search_contacts(request):
    phone = request.session["regphone"]
    cursor = connection.cursor()
    cursor.execute("select * from chat_account where phone ='" + str(phone) + "'")
    data = cursor.fetchone()
    a =list(data)

    cursor = connection.cursor()
    cursor.execute("select contacts.fname,chat_account.phone,chat_account.pic from contacts join chat_account  where contacts.chat_acc_id ='"+str(a[0])+"' and contacts.contact_id = chat_account.account_id")
    contactss = cursor.fetchall()

    search_query = request.GET.get('query', '')

    with connection.cursor() as cursor:
        sql_query = ("""select contacts.fname, chat_account.phone, chat_account.pic from contacts join chat_account where  contacts.fname like %s or chat_account.phone like %s """, ['%' + search_query + '%', '%' + search_query + '%'],""" and contacts.chat_acc_id ='""" + str(a[0]) + """' and contacts.contact_id = chat_account.account_id""")

        cursor.execute("""select contacts.fname, chat_account.phone, chat_account.pic, chat_account.account_id  from contacts join chat_account on contacts.chat_acc_id ='""" + str(a[0]) + """' and contacts.contact_id = chat_account.account_id where contacts.fname like %s or chat_account.phone like %s """, ['%' + search_query + '%', '%' + search_query + '%'])
        contacts = cursor.fetchall()

    contact_list =[{'name': row[0],'phone':row[1],'pic':row[2], 'id':row[3]} for row in contacts]

    return render(request, 'contacts.html',{'profile':data,'contactss': contacts, 'contacts': contact_list})


def new_contact(request):
        phone = request.session["regphone"]
        cursor = connection.cursor()
        cursor.execute("select * from chat_account where phone ='" + str(phone) + "'")
        data = cursor.fetchone()
        if request.method == 'POST':
            contact = request.POST['phone']
            cursor.execute("select * from chat_account where phone ='" + str(contact) + "' ")
            sea = cursor.fetchone()

            if sea == None:
                return HttpResponse(
                    "<script>alert('No such phone number registered');window.location='../add_new_contact';</script>")
            else:
                if phone == contact:
                    return HttpResponse(
                        "<script>alert('This Is Your Number');window.location='../add_new_contact';</script>")
                else:
                    cursor.execute("select account_id from chat_account where phone ='" + str(phone) + "' ")
                    sae = cursor.fetchone()
                    accid = list(sae)
                    request.session['accid'] = str(accid[0])
                    cursor.execute("select account_id from chat_account where phone ='" + str(contact) + "' ")
                    id = cursor.fetchone()
                    id = list(id)
                    request.session['contactaccid'] = str(id[0])
                    cursor.execute(
                        "select * from contacts where contact_id ='" + str(id[0]) + "' and chat_acc_id ='" + str(
                            accid[0]) + "' ")
                    exist = cursor.fetchone()
                    if exist == None:
                        return redirect("contact_details")
                    else:
                        return HttpResponse(
                            "<script>alert('already saved in your contact list ');window.location='../add_new_contact';</script>")

        return render(request, 'newcontact.html', {'profile': data})

def contact_details(request):
        phone = request.session["regphone"]
        cursor = connection.cursor()
        cursor.execute("select * from chat_account where phone ='" + str(phone) + "'")
        data = cursor.fetchone()
        accid = request.session['accid']
        contactaccid = request.session['contactaccid']
        if request.method == 'POST':
            fname = request.POST['fname']
            lname = request.POST['lname']
            details = request.POST['details']
            cursor = connection.cursor()
            cursor.execute("insert into contacts values(null, '" + str(fname) + "', '" + str(lname) + "', '" + str(
                details) + "', '" + str(contactaccid) + "', '" + str(accid) + "')")
            return redirect(search_contacts)
        return render(request, 'contact_details.html', {'profile': data})

def send_message(request):
    if request.method == 'POST':
        message = request.POST['message']
        id = request.session["viewchat"]
        phone = request.session["regphone"]
        cursor = connection.cursor()
        cursor.execute("select account_id from chat_account where phone ='" + str(phone) + "' ")
        sae = cursor.fetchone()
        accid = list(sae)
        cursor.execute(" select chatid from chatbw where user1 = '"+str(accid[0])+"' and user2 = '"+str(id)+"' ")
        eas = cursor.fetchone()
        if eas == None:
            cursor.execute("select chatid from chatbw where user1 ='"+str(id)+"' and user2 = '"+str(accid[0])+"' ")
            eax = cursor.fetchone()
            if eax == None:
                cursor.execute("insert into chatbw values(null,'"+str(accid[0])+"', '"+str(id)+"')")
                cursor.execute("select chatid from chatbw where user1 = '"+str(accid[0])+"' and user2 = '"+str(id)+"' ")
                eaz = cursor.fetchone()
                chatid = list(eaz)
                chatid = chatid[0]
                cursor.execute("insert into chats values(null,'"+str(accid[0])+"','"+str(id)+"','"+str(message)+"',null,'"+str(chatid)+"' )")
                return redirect('view_contact', id=id)
            else:
                chatid = list(eax)
                chatid = chatid[0]
                cursor.execute("insert into chats values(null,'" + str(accid[0]) + "','" + str(id) + "','" + str(
                    message) + "',null,'" + str(chatid) + "' )")
                return redirect('view_contact', id=id)
        else:
            chatid = list(eas)
            chatid = chatid[0]
            cursor.execute(
                "insert into chats values(null,'" + str(accid[0]) + "','" + str(id) + "','" + str(message) + "',null,'" + str(
                    chatid) + "' )")
            return redirect('view_contact', id=id)




def view_contact(request,id):
    search_query = request.GET.get('query', '')
    request.session["viewchat"] = id
    phone = request.session["regphone"]
    cursor = connection.cursor()
    cursor.execute("select account_id from chat_account where phone ='" + str(phone) + "' ")
    sae = cursor.fetchone()
    accid = list(sae)
    cursor.execute("select * from contacts where contact_id ='" + str(id) + "' and chat_acc_id='"+str(accid[0])+"'")
    con = cursor.fetchone()
    if con == None:
        cursor.execute(" select chatid from chatbw where user1 = '"+str(accid[0])+"' and user2 = '"+str(id)+"' ")
        ams = cursor.fetchone()
        if ams == None:
            cursor.execute(" select chatid from chatbw where user1 = '" + str(id) + "' and user2 = '" + str(accid[0]) + "' ")
            aams = cursor.fetchone()
            if aams == None:
                return redirect(search_contacts)

    cursor.execute("select chat_account.pic, contacts.fname from contacts join chat_account where contacts.contact_id = '"+str(id)+"' and contacts.chat_acc_id ='"+str(accid[0])+"' and contacts.contact_id = chat_account.account_id ")
    contact = cursor.fetchone()
    if contact == None:
        cursor.execute("select pic,phone from chat_account where account_id ='"+str(id)+"' ")
        contact = cursor.fetchone()

    cursor.execute("select chatid from chats where sender ='" + str(accid[0]) + "' or reciever = '" + str(accid[0]) + "' ")
    chats = cursor.fetchall()
    chats = list(chats)
    chats = list(reversed(chats))
    s = []
    for i in chats:
        if i[0] not in s:
            s.append(i[0])
    li = []
    for i in s:
        cursor.execute("select id,message,sender,reciever from chats where chatid ='" + str(i) + "'")
        ch = cursor.fetchall()
        ch = list(ch)
        ch = list(reversed(ch))
        he = ch[0]
        h = he[0]
        m = he[1]
        sen = he[2]
        rec = he[3]
        cursor.execute("select * from chats where chatid ='"+str(i)+"' and id ='"+str(h)+"' and sender ='"+str(accid[0])+"'")
        data = cursor.fetchone()
        if data == None:
            cursor.execute("select * from chats where chatid ='"+str(i)+"' and id = '"+str(h)+"' and reciever ='"+str(accid[0])+"' ")
            data = cursor.fetchone()
            if data == None:
                return redirect(search_contacts)
            else:
                cursor.execute("select fname from contacts where chat_acc_id ='""" + str(accid[0]) + """' and contact_id ='""" + str(sen) + """' and fname like %s """, ['%' + search_query + '%'])
                data = cursor.fetchone()

                if data == None:
                    cursor.execute("select phone, pic from chat_account where account_id ='" + str(sen) + "' ")
                    data = cursor.fetchone()
                    l=[]
                    l.append(data[0])
                    l.append(sen)
                    l.append(m)
                    l.append(data[1])
                    l = tuple(l)
                    li.append(l)

                else:
                    cursor.execute("select phone, pic from chat_account where account_id ='" + str(sen) + "' ")
                    datas = cursor.fetchone()
                    l=[]
                    l.append(data[0])
                    l.append(sen)
                    l.append(m)
                    l.append(datas[1])
                    l = tuple(l)
                    li.append(l)

        else:
            cursor.execute("select fname from contacts where chat_acc_id ='"""+str(accid[0])+"""' and contact_id ='"""+str(rec)+"""' and fname like %s """, ['%' + search_query + '%'])
            data = cursor.fetchone()
            if data == None:
                cursor.execute("select phone, pic from chat_account where account_id ='"+str(rec)+"' ")
                data = cursor.fetchone()
                l=[]
                l.append(data[0])
                l.append(rec)
                l.append(m)
                l.append(data[1])
                l = tuple(l)
                li.append(l)

            else:
                cursor.execute("select phone, pic from chat_account where account_id ='" + str(rec) + "' ")
                datas = cursor.fetchone()
                l=[]
                l.append(data[0])
                l.append(rec)
                l.append(m)
                l.append(datas[1])
                l = tuple(l)
                li.append(l)
    li = tuple(li)
    contact_list = [{'name': row[0], 'id': row[1], 'message': row[2], 'pic': row[3]} for row in li]

    cursor.execute("select chatid from chats where sender ='"+str(id)+"' and reciever ='"+str(accid[0])+"'")
    data1 = cursor.fetchone()
    cursor.execute("select chatid from chats where sender ='" + str(accid[0]) + "' and reciever ='" + str(id) + "'")
    data2 = cursor.fetchone()
    if data1 == None:
        if data2 == None:
            chat =()
            cursor.execute("select * from chat_account where phone ='" + str(phone) + "'")
            data = cursor.fetchone()
            count = 0
            chathe = []
            chatme = []
            for i in chat:
                count = count + 1

                if i[1] == str(accid[0]):
                    chathe.append("")
                    chatme.append(i[3])
                else:
                    chatme.append("")
                    chathe.append(i[3])
            range_count = range(0, count)
            mata = zip(range_count, chathe, chatme)
            context = {
                'data': mata,
            }

            return render(request,'view_contact.html',{'contact': contact,'chathe': chathe, 'chatme': chatme, 'range_count': range_count, 'contacts': contact_list, 'profile': data,'data': mata})
        else:
            cursor.execute("select * from chats where chatid ='" + str(data2[0]) + "' ")
            chat = cursor.fetchall()
            cursor.execute("select * from chat_account where phone ='" + str(phone) + "'")
            data = cursor.fetchone()
            count = 0
            chathe = []
            chatme = []
            for i in chat:
                count = count + 1

                if i[1] == str(accid[0]):
                    chathe.append("")
                    chatme.append(i[3])
                else:
                    chatme.append("")
                    chathe.append(i[3])
            range_count = range(0, count)
            mata = zip(range_count, chathe, chatme)
            context = {
                'data': mata,
            }

            return render(request,'view_contact.html',{'contact': contact,'chathe': chathe, 'chatme': chatme, 'range_count': range_count, 'contacts': contact_list, 'profile': data,'data': mata})
    else:

        cursor.execute("select * from chats where chatid ='"+str(data1[0])+"' ")
        chat = cursor.fetchall()
        cursor.execute("select * from chat_account where phone ='" + str(phone) + "'")
        data = cursor.fetchone()
        count = 0
        chathe = []
        chatme = []
        for i in chat:
            count = count + 1

            if i[1] == str(accid[0]):
                chathe.append("")
                chatme.append(i[3])
            else:
                chatme.append("")
                chathe.append(i[3])
        range_count = range(0, count)
        mata = zip(range_count, chathe, chatme)
        context = {
            'data': mata,
        }

        return render(request,'view_contact.html',{'contact': contact,'chathe': chathe, 'chatme': chatme, 'range_count': range_count, 'contacts': contact_list, 'profile': data,'data': mata})





# def search_contacts(request):
#     phhone = request.session["regphone"]
#     cursor = connection.cursor()
#     cursor.execute("select * from chat_account where phone ='" + str(phhone) + "'")
#     data = cursor.fetchone()
#     a = list(data)
#     print(a)
#     search_query = request.GET.get('query', '')
#     print(search_query)
#     with connection.cursor() as cursor:
#         sql_query =("""select contacts.fname, chat_account.phone, chat_account.pic from contacts join chat_account where contacts.chat_acc_id ='"""+ str(a[0]) + """' and contacts.contact_id = chat_account.account_id and contacts.fname like %s or chat_account.phone like %s """,['%'+search_query+'%','%'+search_query+'%'])
#         print(sql_query)
#         cursor.execute("""select contacts.fname, chat_account.phone, chat_account.pic from contacts join chat_account where contacts.chat_acc_id ='"""+ str(a[0]) + """' and contacts.contact_id = chat_account.account_id and contacts.fname like %s or chat_account.phone like %s """,['%'+search_query+'%','%'+search_query+'%'])
#
#         results = []
#         for row in cursor.fetchall():
#             name,phone,pic = row
#             results.append({
#                 'fname': name,
#                 'phone': phone,
#                 'pic': pic,
#             })
#         print(results)
#
#     return JsonResponse({'results': results})











