from django.http import HttpResponse
from .models import *
from django.shortcuts import render, redirect
from django.contrib import auth
from django.middleware.csrf import CsrfViewMiddleware



def enter(request):
    return render(request, 'enter.html')

def account(request):
    context = {}
    if request.method == "POST":
        print(request.POST)
        try:
            username1 = request.POST.get("username")
            print(username1)
            user = User.objects.get(username=username1)
            pk = user.id
            member = Person.objects.get(person_id = pk)
            bankbook = BankBook.objects.get(user_id = member.pk)
            user_bankbook = bankbook.balance_won
            print(type(user_bankbook))
            
            amount = request.POST.get("Amount")
            print(amount)
            context["amount"] = int(amount)

            if 'input' in request.POST:
                update = user_bankbook + int(amount)
                context["update"] = update
                context["buy_possible"] = True
                print(f"입금:{amount} >> 잔액:{update}")
                BankBook.objects.filter(user_id = member.pk).update(balance_won = update)
                print(context)
            
            elif 'output' in request.POST:
                update = int(user_bankbook - int(amount))

                if update >= 0:
                    context["update"] = update
                    context["cell_possible"] = True
                    print(f"출금:{amount} >> 잔액:{update}")
                    BankBook.objects.filter(user_id = member.pk).update(balance_won = update)
                else:
                    context["cell_impossible"] = False
                    print("출금실패")
                    return render(request, 'account.html',context)
        except:
            return render(request, 'account.html')
    return render(request, 'account.html',context)


def change_calculate(request):
    #유저 접속 거부
    req_mem  = Person.objects.get(person_id = request.user.pk)
    if req_mem.is_manger == False:
        return redirect(f'/{request.user.pk}/')
    
    show_reciept     =  False
    is_cell_possible =  False
    is_buy_possible  =  False
    show_limit       =  False

    context = {
        "show_reciept"      : show_reciept,
        "is_cell_possible"  : is_cell_possible,
        "is_buy_possible"   : is_buy_possible,
        "show_limit"        : show_limit
    }

    if request.method == "POST":
        try:
            #폼 결과
            username   = request.POST.get("username")
            input       = request.POST.get("input")
            currency    = request.POST.get("currency")
            
            user    = User.objects.get(username=username)
            pk      = user.id
            member  = Person.objects.get(person_id = pk)

            #환율정보
            exchange_info = Exchange.objects.all().values()[0]
            #수수료 정보
            charge_info = Exchange.objects.all().values()[1]["dollar2won"]
            print(charge_info)

            bankbook = BankBook.objects.get(user_id = member.pk)

            if currency == "USD":
                rate = exchange_info["dollar2won"]
                user_bankbook = bankbook.balance_dol
            elif currency == "PHP":
                rate = exchange_info["pesso2won"]
                user_bankbook = bankbook.balance_pes
            elif currency == "YEN":
                rate = exchange_info["yenn2won"]
                user_bankbook = bankbook.balance_yen
                
            import math
            #외화 -> 원화
            if 'cell' in request.POST:
                input = int(input)
                if user_bankbook >= input:
                    cell_possible = True
                    change = input * rate
                    real_change = math.ceil(change * (1 - (charge_info / 100)))
                    charge = change - real_change
                    txt = str(input) + " " + str(currency)
                    
                    context["cell_possible"]    = cell_possible
                    context["change"]           = change
                    context["real_change"]      = real_change
                    context["charge"]           = charge
                    context["input"]            = txt
                    print("cell possible")
                
                else:
                    not_cell_possible = True
                    txt = "보유 외화 : " + str(user_bankbook) +" "+ currency
                    context["not_cell_possible"] = not_cell_possible
                    context["input"] = txt

            #원화 -> 외화
            else:
                input = int(input)

        except:
            pass


    return render(request, 'change_calculate.html',context)

def change_money(request):
    show_reciept = False
    is_cell_possible = False
    is_buy_possible = False
    is_success = False

    context = {
        "show_reciept" : show_reciept,
        "is_cell_possible" :is_cell_possible,
        "is_buy_possible" : is_buy_possible,
        "is_success" : is_success
    }

    req_mem  = Person.objects.get(person_id = request.user.pk)
    context["is_manger"] = req_mem.is_manger
    if not req_mem.is_manger:
        bankbooktmp = BankBook.objects.get(user_id = req_mem.pk)
        user_won = bankbooktmp.balance_won
        user_dol = bankbooktmp.balance_dol
        user_php = bankbooktmp.balance_pes
        user_yen = bankbooktmp.balance_yen
        context["user_won"] = user_won
        context["user_dol"] = user_dol
        context["user_php"] = user_php
        context["user_yen"] = user_yen

    if request.method == "POST":
        try:
            #manger change
            if req_mem.is_manger:
                username1 = request.POST.get("username")
                print(username1)
                user = User.objects.get(username=username1)
                pk = user.id
                member = Person.objects.get(person_id = pk)
            #user direct
            else:
                member = req_mem
            
            input = request.POST.get("input")
            currency = request.POST.get("currency")
            exchange_info = Exchange.objects.all().values()[0]

            percent = 0.1

            if currency == "USD":
                rate = exchange_info["dollar2won"]
            elif currency == "PHP":
                rate = exchange_info["pesso2won"]
            else:
                rate = exchange_info["yenn2won"]
            
            bankbook = BankBook.objects.get(user_id = member.pk)

            if currency == "USD":
                user_bankbook = bankbook.balance_dol
                    
            elif currency == "PHP":
                user_bankbook = bankbook.balance_pes
            else:
                user_bankbook = bankbook.balance_yen
            txt = input + " " +currency

            #외화 -> 원화
            if 'cell' in request.POST:
                input = int(input)
                if user_bankbook >= input:
                    is_cell_possible = True
                    rate = rate*(1-percent)
                    get_won = int(input * rate)

                    print(f"get won = {get_won}")
                    
                    context["is_cell_possible"] = is_cell_possible
                    context["get_won"] = get_won
                    context["input"] = str(input)+currency

                    try:
                        origin = user_bankbook
                        origin_won = bankbook.balance_won

                        update = origin - input
                        update_won = origin_won + get_won

                        if currency == "USD":
                            BankBook.objects.filter(user_id = member.pk).update(balance_dol = update)
                                
                        elif currency == "PHP":
                            BankBook.objects.filter(user_id = member.pk).update(balance_pes = update)

                        else:
                            BankBook.objects.filter(user_id = member.pk).update(balance_yen = update)

                        BankBook.objects.filter(user_id = member.pk).update(balance_won = update_won)
                        is_success = True
                        context["is_success"] = is_success
                        
                    except:
                        print("db fail")
                        return redirect('/change_money')
            #원화 -> 외화
            else:
                #환전 최대 가능량
                rate = rate*(1+percent)
                show_limit = True
                context["show_limit"] = show_limit

                limit = int(user_won / rate)-1
                context["limit"] = str(limit) +currency
                print(user_won)
                print(limit)

                input = int(input)
                if limit >= input:
                    is_buy_possible = True
                    context["is_buy_possible"] = is_buy_possible

                    use_money = int(input * rate)
                    
                    context["currency"] = currency
                    context["use_money"] = use_money
                    context["input"] = str(input)+currency


                    try:
                        origin_won = bankbook.balance_won
                        update_won = origin_won - use_money

                        if currency == "USD":
                            origin = BankBook.objects.get(user_id = member.pk).balance_dol
                            update = origin + input
                            BankBook.objects.filter(user_id = member.pk).update(balance_dol = update)
                                
                        elif currency == "PHP":
                            origin = BankBook.objects.get(user_id = member.pk).balance_pes
                            update = origin + input
                            BankBook.objects.filter(user_id = member.pk).update(balance_pes = update)

                        else:
                            origin = BankBook.objects.get(user_id = member.pk).balance_yen
                            update = origin + input
                            BankBook.objects.filter(user_id = member.pk).update(balance_yen = update)

                        BankBook.objects.filter(user_id = member.pk).update(balance_won = update_won)
                        is_success = True
                        context["is_success"] = is_success
                        
                    except:
                        print("db fail")
                        return redirect('/change_money')

        except:
            pass


    return render(request, 'change_money.html',context)

def checkwinner(request):
    #유저 접속 거부
    req_mem  = Person.objects.get(person_id = request.user.pk)
    if req_mem.is_manger == False:
        return redirect(f'/{request.user.pk}/')
    
    top_won = BankBook.objects.order_by('-balance_won')[:5]
    top_dol = BankBook.objects.order_by('-balance_dol')[:5]
    top_pes = BankBook.objects.order_by('-balance_pes')[:5]
    top_yen = BankBook.objects.order_by('-balance_yen')[:5]
    context = {}
    i = 1
    for won in top_won:
        if won.user.is_player:
            context["won"+str(i)+"name"] = won.user.person
            context["won"+str(i)] = won.balance_won
            i += 1
        if i == 3:
            break
    
    i = 1
    for dol in top_dol:
        if dol.user.is_player:
            context["dol"+str(i)+"name"] = dol.user.person
            context["dol"+str(i)] = dol.balance_dol
            i += 1
        if i == 3:
            break

    i = 1
    for pes in top_pes:
        if pes.user.is_player:
            context["pes"+str(i)+"name"] = pes.user.person
            context["pes"+str(i)] = pes.balance_pes
            i += 1
        if i == 3:
            break
    
    i = 1
    for yen in top_yen:
        if yen.user.is_player:
            context["yen"+str(i)+"name"] = yen.user.person
            context["yen"+str(i)] = yen.balance_yen
            i += 1
        if i == 3:
            break
    

    return render(request, 'checkwinner.html',context)



def first_page(request):
    print("this is first_page")
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "log_in":
            print(action)
            return redirect('/log_in')

    return render(request, 'first_page.html')

def login_page(request):
    print("this is login_page")
    print(request)

    if request.method == "POST":
        userid = request.POST.get("username")
        pwd = request.POST.get("password")
        print(userid)
        print(pwd)
        user = auth.authenticate(request, username = userid, password = pwd)
        print(user)
        #user = User.objects.get(username = userid)

        if user is not None:
            auth.login(request, user)
            print(user.pk)
            return redirect(f'/{user.pk}/')


    return render(request, 'login_page.html')

def exchange_rate(request):
    exchange_info = Exchange.objects.all().values()[0]
    user_pk = request.user.pk
    user = User.objects.get(id=user_pk)
    context = {'info' : exchange_info,
               'user' : user}
    return render(request, 'exchange.html',context)


def user_main_page(request, pk):
    #Cut Another Link
    if request.user.pk != pk:
        return redirect(f'/{request.user.pk}/')
    
    user = User.objects.get(id=pk)
    member = Person.objects.get(person_id = pk)
    
    if member.is_manger:
        bankbook = []
    else:
        bankbook = BankBook.objects.get(user_id = member.pk)

    
    context = {"user_detail" : user,
               "bankbook_ifo" : bankbook,
               "member" : member}
    return render(request, 'user_main_page.html',context)




