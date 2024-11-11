from django.http import HttpResponse
from .models import *
from django.shortcuts import render, redirect
from django.contrib import auth
from django.middleware.csrf import CsrfViewMiddleware

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
    print(request.body)
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

    if request.method == "POST":
        try:
            username1 = request.POST.get("username")
            print(username1)
            
            input = request.POST.get("input")
            
            currency = request.POST.get("currency")
            
            user = User.objects.get(username=username1)
            pk = user.id
            member = Person.objects.get(person_id = pk)
            exchange_info = Exchange.objects.all().values()[0]

            manager = str(request.user)

            if currency == "USD":
                rate = exchange_info["dollar2won"]
            elif currency == "PHP":
                rate = exchange_info["pesso2won"]
            else:
                rate = exchange_info["yenn2won"]
            
            if not member.is_manger:
                print("is not manager")
                bankbook = BankBook.objects.get(user_id = member.pk)
                charge_free = False

                if currency == "USD":
                    user_bankbook = bankbook.balance_dol
                    if manager == "usd":
                        charge_free = True
                        
                elif currency == "PHP":
                    user_bankbook = bankbook.balance_pes
                    if manager == "php":
                        charge_free = True
                else:
                    user_bankbook = bankbook.balance_yen
                    if manager == "yen":
                        charge_free = True
                txt = input + " " +currency

                print(f"charge free : {charge_free}")

                if 'cell' in request.POST:
                    input = int(input)
                    if user_bankbook >= input:
                        is_cell_possible = True
                        print(f"is cell possibile : {is_cell_possible}")
                        #나중에 수수료 면제

                        #받는 원화 가격
                        get_won = input * rate

                        #환전 수수료
                        if charge_free == False:
                             charge = get_won * 0.1
                             charge = int(charge)
                        else:
                            charge = 0
                        get_won = int(get_won - charge)
                        print(f"charge : {charge}")
                        print(f"get won = {get_won}")
                        
                        context["is_cell_possible"] = is_cell_possible
                        context["get_won"] = get_won
                        context["charge"] = charge
                        context["input"] = txt

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

                            


                else:
                    user_bankbook = bankbook.balance_won

                    #환전 최대 가능량
                    show_limit = True
                    limit = int(user_bankbook / (rate * 1.1))

                    context["show_limit"] = show_limit
                    context["limit"] = limit
                    input = int(input)
                    if limit >= input:
                        is_buy_possible = True

                        use_money = input * rate
                        
                        if charge_free == False:
                            charge = int(use_money * 0.1)
                        else:
                            charge = 0
                        use_money = int(use_money + charge)

                        context["is_buy_possible"] = is_buy_possible
                        context["currency"] = currency
                        context["charge"] = charge
                        context["use_money"] = use_money
                        context["input"] = txt


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
        user = User.objects.get(username = userid)
        print(user.is_active)

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




