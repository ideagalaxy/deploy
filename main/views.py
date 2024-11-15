from django.http import HttpResponse
from .models import *
from django.shortcuts import render, redirect
from django.contrib import auth
from django.middleware.csrf import CsrfViewMiddleware
from datetime import datetime

def receipt(request,inputdata):
    return render(request, 'receipt.html')

exchange_info = Exchange.objects.all().values()[0]
FEE = exchange_info["enter_fee"]

def enter(request):
    req_mem  = Person.objects.get(person_id = request.user.pk)
    bankbooktmp = BankBook.objects.get(user_id = req_mem.pk).balance_won

    if request.method == "POST":
        context = {}
        current_time = datetime.now().strftime("%m월 %d일  %H:%M:%S")
        context["current_time"] = current_time

        #잔고가 참가비보다 적을 때 참가 못함
        if bankbooktmp < FEE:
            txt = "결제실패(잔고부족)"
            context["txt1"] = txt
            return render(request, 'receipt.html', context)
            
        if 'nomal' in request.POST:
            update = bankbooktmp - FEE
            context["is_enter"] = True
            BankBook.objects.filter(user_id = req_mem.pk).update(balance_won = update)
            txt = f"{FEE}원 결제성공(잔액: {update}원)"
            context["txt1"] = txt
            return render(request, 'receipt.html', context)
        
        if 'casino' in request.POST:
            return redirect(f'casino')

    return render(request, 'enter.html')

def casino(request):
    context = {}
    coin_price = 50000
    context["price"] = coin_price
    context['enter_fee'] = int(FEE)

    req_mem  = Person.objects.get(person_id = request.user.pk)
    bankbooktmp = BankBook.objects.get(user_id = req_mem.pk).balance_won

    if request.method == "POST":
        if 'buy' in request.POST:
            input_str = request.POST.get("input")
            try:
                input = int(input_str)
                if input < 0:
                    current_time = datetime.now().strftime("%m월 %d일  %H:%M:%S")
                    context["current_time"] = current_time
                    txt = "0보다 큰 값을 입력하십시오."
                    context["txt1"] = txt
                    txt2 = "처음부터 다시 참가과정을 진행하십시오."
                    context["txt2"] = txt2
                    return render(request, 'receipt.html', context)

            except (TypeError, ValueError):
                input = None  # 또는 기본값 설정

            if input != None:
                current_time = datetime.now().strftime("%m월 %d일  %H:%M:%S")
                context["current_time"] = current_time

                if (input+FEE) <= bankbooktmp:
                    update = bankbooktmp - input - FEE
                    context["is_enter"] = True
                    BankBook.objects.filter(user_id = req_mem.pk).update(balance_won = update)
                    txt = f"{input+FEE}원 결제성공(잔액: {update}원)"
                    context["txt1"] = txt
                    context['txt2'] = f"참가비({FEE}원) + 결제비({input}원)"
                    return render(request, 'receipt.html', context)
                
                else:
                    txt = "결제실패(잔고부족)"
                    context["txt1"] = txt
                    return render(request, 'receipt.html', context)

    return render(request, 'casino.html',context)

#입출금 : 매니저 전용
def account(request):
    #유저 접속 거부
    req_mem  = Person.objects.get(person_id = request.user.pk)
    if req_mem.is_manger == False:
        return redirect(f'/{request.user.pk}/')

    context = {}
    if request.method == "POST":
        print(request.POST)
        current_time = datetime.now().strftime("%m월 %d일  %H:%M:%S")
        context["current_time"] = current_time
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

            if int(amount) < 0:
                txt = "실패 : 0원 보다 큰 값을 입력하세요."
                context["txt1"] = txt
                return render(request, 'manager_receipt.html', context)

            if 'input' in request.POST:
                update = user_bankbook + int(amount)
                BankBook.objects.filter(user_id = member.pk).update(balance_won = update)
                print(context)

                txt = f"입금성공 : +{amount}원 (잔고: {update}원)"
                context["txt1"] = txt
                return render(request, 'manager_receipt.html', context)
            
            elif 'output' in request.POST:
                update = int(user_bankbook - int(amount))

                if update >= 0:
                    BankBook.objects.filter(user_id = member.pk).update(balance_won = update)

                    txt = f"출금성공 : -{amount}원 (잔고: {update}원)"
                    context["txt1"] = txt
                    return render(request, 'manager_receipt.html', context)
                else:
                    txt = f"출금실패 : 잔액부족"
                    context["txt1"] = txt
                    return render(request, 'manager_receipt.html', context)
        except:
            pass
        
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

    current_time = datetime.now().strftime("%m월 %d일  %H:%M:%S")
    context["current_time"] = current_time

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

            percent = int(exchange_info["change_rate_percent"])/100
            print(percent)

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
                if input <= 0:
                    txt = "0보다 큰 값을 입력하십시오."
                    context["txt1"] = txt
                    return render(request, 'receipt.html', context)
                
                if user_bankbook >= input:
                    is_cell_possible = True
                    rate = rate*(1-percent)
                    get_won = int(input * rate)
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

                        txt1 = str(input)+" "+currency+ " -> "+str(get_won)+"원 : 환전(판매)완료"
                        context["txt1"] = txt1

                        return render(request, 'receipt.html', context)
                        
                    except:
                        txt = "환전 실패"
                        context["txt1"] = txt
                        txt2 = "재시도하거나 은행을 방문하시길 바랍니다."
                        context["txt2"] = txt2
                        return render(request, 'receipt.html', context)
                else:
                    txt = currency + " 부족"
                    context["txt1"] = txt
                    return render(request, 'receipt.html', context)

                    
            #원화 -> 외화
            elif 'buy' in request.POST:
                #환전 최대 가능량
                rate = rate*(1+percent)
                show_limit = True
                context["show_limit"] = show_limit

                limit = int(user_won / rate)-1
                context["limit"] = str(limit) +currency

                input = int(input)
                if input <= 0:
                    txt = "0보다 큰 값을 입력하십시오."
                    context["txt1"] = txt
                    return render(request, 'receipt.html', context)
                
                if limit >= input:
                    use_money = int(input * rate)
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
                        
                        txt1 = str(use_money)+ " 원 -> "+str(input)+" "+currency+ " : 환전(구매)완료"
                        context["txt1"] = txt1

                        return render(request, 'receipt.html', context)
                        
                    except:
                        txt = "환전 실패"
                        context["txt1"] = txt
                        txt2 = "재시도하거나 은행을 방문하시길 바랍니다."
                        context["txt2"] = txt2
                        return render(request, 'receipt.html', context)
                    
                else:
                    txt = "잔고 부족"
                    context["txt1"] = txt
                    return render(request, 'receipt.html', context)
        except:
            pass

    return render(request, 'change_money.html',context)

#우승자 확인 : 매니저 전용
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




