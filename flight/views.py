from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import *
from datetime import datetime
from django.contrib import messages
from django.core.mail import send_mail
import uuid
import json
import ast
from django.urls import reverse
from django.conf import settings
from .api_responses import *


# int round pending
# del - dxb
# 15/12/2023 - 25/12/2023
# indigo

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)

        page = request.POST.get('next')

        if user is not None:
            auth_login(request, user)
            if page and page.strip():
                return redirect(page)
            else:
                return redirect('index')
        else:
            error_message = 'Invalid credentials. Please check your email and password.'
            return render(request, 'login.html', {'error_message': error_message})
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(username=email).exists():
            error_message = 'User already exists.'
            return render(request, 'register.html', {'error_message':error_message})
        else:
            user = User.objects.create_user(username=email, password=password)
            user.first_name = name
            user.email = email
            user.save()
            return redirect('login')
    return render(request, 'register.html')

def send_forget_pass_mail(email, token):
    subject = 'Your forget Password Link'
    
    message = f'Hi, click on the link to reset your password https://veikeishun.com/change_password/{token}/'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True

def Forgot_Password(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            if not User.objects.filter(username=email).first():
                error_message = 'User Not exists.'
                return render(request, 'Forgot_Password.html', {'error_message':error_message})
            user_obj = User.objects.get(username = email)
            
            token = str(uuid.uuid4())
            user_profile, created = forget_password_token.objects.get_or_create(user=user_obj)
            user_profile.forget_password_token = token
            user_profile.save()
            send_forget_pass_mail(user_obj, token)
            error_message_success = 'A password reset link has been sent to your email.'
            return render(request, 'Forgot_Password.html', {'error_message_success':error_message_success})

    except Exception as e:
        print(e)
    return render(request, 'Forgot_Password.html')

def change_password(request, token):
    context = {}
    try:
        profile_obj = forget_password_token.objects.filter(forget_password_token = token).first()
        context = {'user_id': profile_obj.user.id}
        if request.method == 'POST':
            password = request.POST.get('password')
            cpassword = request.POST.get('cpassword')
            user_id = request.POST.get('user_id')

            if user_id is None:
                messages.error(request, 'No user Found.')
                return redirect(f'/change_password/{token}/')
            
            if password != cpassword:
                messages.error(request, 'Password Not Matched.')
                return redirect(f'/change_password/{token}/')
            
            user_obj = User.objects.get(id=user_id)
            user_obj.set_password(cpassword)
            user_obj.save()
            return redirect('index')
    
    except Exception as e:
        print(e)

    return render(request, 'change_password.html', context)

def logout(request):
    auth_logout(request)
    return redirect('index')

def base(request):
    return render(request, 'base.html')

def index(request):
    error_message = request.GET.get('error_message', None)
    hero_area_data = hero_area.objects.all()
    Our_Most_Popular_Tours = Our_Most_Popular_Tour.objects.all()
    Our_Best_Deals = Our_Best_Deal.objects.all()
    Video_sections = Video_section.objects.all()
    partner_logos = partner_logo.objects.all()
    testimonials = testimonial.objects.all()
    Blogs = Blog.objects.all()
    context = {
        'hero_area_data' : hero_area_data,
        'Our_Most_Popular_Tour':Our_Most_Popular_Tours,
        'Our_Best_Deal':Our_Best_Deals,
        'Video_section':Video_sections,
        'partner_logo':partner_logos,
        'testimonial':testimonials,
        'Blog':Blogs,
        'error_message':error_message
    }
    return render(request, 'index.html', context)

def flight_result(request):    
    indian_airport_codes = [
    "AAI", "AGX", "AGR", "AJL", "BLR", "AKD", "AKU", "AMD", "AMH", "ATQ", "BBI", "BHO", "BHJ", "BHU", "BIA", "BIU", "BKB", "BKI", "BOM", "CCJ", "CDP", "CCU", "DEP", "DED", "DEL", "DEP", "DIU", "DMU", "DIB", "DIK", "DLM", "DMK", "DOH", "DRJ", "DZK", "EPZ", "FRA", "GAU", "GOP", "GAY", "GOI", "GOP", "GWL", "HBX", "HKD", "HYD", "IMF", "IXB", "IXC", "IXD", "IXE", "IXG", "IXH", "IXI", "IXJ", "IXK", "IXL", "IXM", "IXP", "IXR", "IXS", "IXU", "IXV", "IXW", "IXY", "IXZ", "JGA", "JAI", "JCB", "JDH", "JGB", "JGA", "JLR", "JRH", "JSA", "JSH", "JUC", "KNU", "KUU", "KTM", "KDR", "KEK", "KLH", "LKO", "LCC", "LUH", "LUD", "MAA", "MAB", "MBB", "MCT", "MDU", "MAA", "MDC", "MYQ", "NAG", "NDC", "NDC", "NMB", "NMC", "NMS", "NMA", "PAT", "PNY", "PAB", "PGH", "PUT", "RAA", "RUP", "RAJ", "RJA", "RJI", "RAJ", "RUP", "RAJ", "RPR", "RJA", "SAG", "SHL", "IXJ", "SXR", "STV", "IXA", "TEZ", "TRZ", "TJV", "TIR", "UDR", "VNS", "VTZ", "VGA", "VII", "VNS", "VTZ"
    ]
    try:
        FlightDateR = ''
        flight_type = ''
        return_date_input = ''
        if request.method == 'POST':
            flight_type = request.POST.get('flight-type')
            print(flight_type)
            FarecabinOption = request.POST.get('cabin-class')
            if FarecabinOption == 'Economy':
                FarecabinOption = 'E'
            elif FarecabinOption == 'Business':
                FarecabinOption = 'B'
            elif FarecabinOption == 'First Class':
                FarecabinOption = 'F'

            if flight_type == 'one-way':
                flight_type = 'O'
            elif flight_type == 'round-way':
                flight_type = 'R'

            DepartureStation = request.POST.get('from-destination')
            ArrivalStation = request.POST.get('to-destination')
            journey_date_input = request.POST.get('journey-date')
            parsed_date = datetime.strptime(journey_date_input, '%m/%d/%Y')
            FlightDate = parsed_date.strftime('%Y%m%d')

            if flight_type == 'R':
                return_date_input = request.POST.get('return-date')
                parsed_dateR = datetime.strptime(return_date_input, '%m/%d/%Y')
                FlightDateR = parsed_dateR.strftime('%Y%m%d')
            adult = request.POST.get('adult')
            children = request.POST.get('children')
            infant = request.POST.get('infant')
            totalpassengers = int(adult) + int(children) + int(infant)

            availabilitycheck_Response = availabilitycheck(flight_type=flight_type, DepartureStation=DepartureStation, ArrivalStation=ArrivalStation, FlightDate=FlightDate, FlightDateR=FlightDateR, FarecabinOption=FarecabinOption, adult=adult, children=children, infant=infant)
        hero_area_data = hero_area.objects.all()
        if flight_type == 'R' and (DepartureStation not in indian_airport_codes or ArrivalStation not in indian_airport_codes):
                flight_type = "IR"
        context = {
            'indian_airport_codes': indian_airport_codes,
            'flight_type': flight_type,
            'hero_area_data' : hero_area_data,
            'DepartureStation':DepartureStation,
            'ArrivalStation':ArrivalStation,
            'journey_date_input':journey_date_input,
            'return_date_input':return_date_input,
            'totalpassengers':totalpassengers,
            'FarecabinOption':FarecabinOption,
            'adult':int(adult),
            'children':int(children),
            'infant':int(infant),
            'availabilitycheck_Response':availabilitycheck_Response,
        }
        return render(request, 'flight_result.html', context)
    
    except Exception as e:
        print(e)
        messages.error(request, 'Somthing went wrong')
        return redirect('index')

def flight_pricing(request):
    if request.method == "POST":
            # amt
        adultBaseAmount = request.POST.get('adultBaseAmount')
        adultTotalTaxAmount = request.POST.get('adultTotalTaxAmount')
        childBaseAmount = request.POST.get('childBaseAmount', '0')
        childTotalTaxAmount = request.POST.get('childTotalTaxAmount', '0')
        infantBaseAmount = request.POST.get('infantBaseAmount', '0')
        infantTotalTaxAmount = request.POST.get('infantTotalTaxAmount', '0')
        TotalBaseAmt = float(adultBaseAmount)+float(childBaseAmount)+float(infantBaseAmount)
        TotalGrossAmt = (float(adultTotalTaxAmount)+float(childTotalTaxAmount)+float(infantTotalTaxAmount))+TotalBaseAmt
        # values direct
        BaseOrigin = request.POST.get('BaseOrigin')
        BaseDestination = request.POST.get('BaseDestination')
        TripType = request.POST.get('TripType')
        AdultCount = request.POST.get('AdultCount')
        children = request.POST.get('children')
        infant = request.POST.get('infant')
        FlightID = request.POST.get('FlightID')
        FlightNumber = request.POST.get('FlightNumber')
        Origin = request.POST.get('Origin')
        Destination = request.POST.get('Destination')
        DepartureDateTime = request.POST.get('DepartureDateTime')
        ArrivalDateTime = request.POST.get('ArrivalDateTime')
        Trackid = request.POST.get('Trackid')
        Stops = request.POST.get('Stops')

        # 1stop
        FlightID1 = request.POST.get('FlightID1')
        FlightNumber1 = request.POST.get('FlightNumber1')
        Origin1 = request.POST.get('Origin1')
        Destination1 = request.POST.get('Destination1')
        DepartureDateTime1 = request.POST.get('DepartureDateTime1')
        ArrivalDateTime1 = request.POST.get('ArrivalDateTime1')

        try:
            pricing_details = Pricing(BaseOrigin, BaseDestination, TripType, AdultCount, children, infant, Trackid, FlightID, FlightNumber, Origin, Destination, DepartureDateTime, ArrivalDateTime, FlightID1, FlightNumber1, Origin1, Destination1, DepartureDateTime1, ArrivalDateTime1, TotalBaseAmt, TotalGrossAmt, Stops)
                 
            Fare_Rule = Fare_Rules(FlightID, FlightID1, Trackid, Stops)
            Fare_Rule = Fare_Rule['FareRuleInfo']['FareRuleText']
            fare_description = pricing_details['PriceItenaryInfo'][0]['AvailabilityResponse'][0]['Fares'][0]['Faredescription']

            if len(fare_description) == 2 and fare_description[1]['Paxtype'] == 'CHD':
                childP = float(pricing_details['PriceItenaryInfo'][0]['AvailabilityResponse'][0]['Fares'][0]['Faredescription'][1]['GrossAmount']) * float(children)
            else:
                childP = 0.0

            if len(fare_description) == 2 and fare_description[1]['Paxtype'] == 'INF':
                infantP = float(pricing_details['PriceItenaryInfo'][0]['AvailabilityResponse'][0]['Fares'][0]['Faredescription'][1]['GrossAmount']) * float(infant)
            else:
                infantP = 0.0

            if len(fare_description) == 3:
                infantP = float(pricing_details['PriceItenaryInfo'][0]['AvailabilityResponse'][0]['Fares'][0]['Faredescription'][2]['GrossAmount']) * float(infant)
                childP = float(pricing_details['PriceItenaryInfo'][0]['AvailabilityResponse'][0]['Fares'][0]['Faredescription'][1]['GrossAmount']) * float(children)
            

            adultP = float(pricing_details['PriceItenaryInfo'][0]['AvailabilityResponse'][0]['Fares'][0]['Faredescription'][0]['GrossAmount']) * float(AdultCount)
            Total_price = adultP+childP+infantP

            context = {
                'pricing_details':pricing_details,
                'Fare_Rule':Fare_Rule,
                'Stops':Stops,
                'Total_price':Total_price,
                'adultP':adultP,
                'childP':childP,
                'infantP':infantP,
                'TripType':TripType,
                #for api
                'AdultCount':AdultCount,
                'ChildCount':children,
                'InfantCount':infant,
                }
            return render(request, "pricing.html", context)

        except Exception as e:
            print(e)
            messages.error(request, 'Somthing went wrong')
            return redirect('index')

def Rflight_pricing(request):
    if request.method == "POST":
        # ONEWAY
        adultBaseAmount = request.POST.get('adultBaseAmount')
        adultTotalTaxAmount = request.POST.get('adultTotalTaxAmount')
        childBaseAmount = request.POST.get('childBaseAmount', '0')
        childTotalTaxAmount = request.POST.get('childTotalTaxAmount', '0')
        infantBaseAmount = request.POST.get('infantBaseAmount', '0')
        infantTotalTaxAmount = request.POST.get('infantTotalTaxAmount', '0')
        TotalBaseAmt = float(adultBaseAmount)+float(childBaseAmount)+float(infantBaseAmount)
        OneWay_TotalGrossAmt = (float(adultTotalTaxAmount)+float(childTotalTaxAmount)+float(infantTotalTaxAmount))+TotalBaseAmt
        # values direct
        BaseOrigin = request.POST.get('BaseOrigin')
        BaseDestination = request.POST.get('BaseDestination')
        TripType = request.POST.get('TripType')
        AdultCount = request.POST.get('AdultCount')
        children = request.POST.get('children')
        infant = request.POST.get('infant')
        FlightID = request.POST.get('FlightID')
        FlightNumber = request.POST.get('FlightNumber')
        Origin = request.POST.get('Origin')
        Destination = request.POST.get('Destination')
        DepartureDateTime = request.POST.get('DepartureDateTime')
        ArrivalDateTime = request.POST.get('ArrivalDateTime')
        Trackid = request.POST.get('Trackid')
        Stops = request.POST.get('Stops')
        # 1stop
        FlightID1 = request.POST.get('FlightID1')
        FlightNumber1 = request.POST.get('FlightNumber1')
        Origin1 = request.POST.get('Origin1')
        Destination1 = request.POST.get('Destination1')
        DepartureDateTime1 = request.POST.get('DepartureDateTime1')
        ArrivalDateTime1 = request.POST.get('ArrivalDateTime1')


        # Return
        RadultBaseAmount = request.POST.get('RadultBaseAmount')
        RadultTotalTaxAmount = request.POST.get('RadultTotalTaxAmount')
        RchildBaseAmount = request.POST.get('RchildBaseAmount', '0')
        RchildTotalTaxAmount = request.POST.get('RchildTotalTaxAmount', '0')
        RinfantBaseAmount = request.POST.get('RinfantBaseAmount', '0')
        RinfantTotalTaxAmount = request.POST.get('RinfantTotalTaxAmount', '0')
        RTotalBaseAmt = float(RadultBaseAmount)+float(RchildBaseAmount)+float(RinfantBaseAmount)
        ROneWay_TotalGrossAmt = (float(RadultTotalTaxAmount)+float(RchildTotalTaxAmount)+float(RinfantTotalTaxAmount))+RTotalBaseAmt
        # values direct
        RBaseOrigin = request.POST.get('RBaseOrigin')
        RBaseDestination = request.POST.get('RBaseDestination')
        RFlightID = request.POST.get('RFlightID')
        RFlightNumber = request.POST.get('RFlightNumber')
        ROrigin = request.POST.get('ROrigin')
        RDestination = request.POST.get('RDestination')
        RDepartureDateTime = request.POST.get('RDepartureDateTime')
        RArrivalDateTime = request.POST.get('RArrivalDateTime')
        RStops = request.POST.get('RStops')
        # 1stop
        RFlightID1 = request.POST.get('RFlightID1')
        RFlightNumber1 = request.POST.get('RFlightNumber1')
        ROrigin1 = request.POST.get('ROrigin1')
        RDestination1 = request.POST.get('RDestination1')
        RDepartureDateTime1 = request.POST.get('RDepartureDateTime1')
        RArrivalDateTime1 = request.POST.get('RArrivalDateTime1')
        try:
            pricing_details = Rpricing(BaseOrigin, BaseDestination, TripType, AdultCount, children, infant, Trackid, FlightID, FlightNumber, Origin, Destination, DepartureDateTime, ArrivalDateTime, FlightID1, FlightNumber1, Origin1, Destination1, DepartureDateTime1, ArrivalDateTime1, TotalBaseAmt, OneWay_TotalGrossAmt, Stops, RFlightID, RFlightNumber, ROrigin, RDestination, RDepartureDateTime, RArrivalDateTime, RFlightID1, RFlightNumber1, ROrigin1, RDestination1, RDepartureDateTime1, RArrivalDateTime1, RTotalBaseAmt, ROneWay_TotalGrossAmt, RStops)
            Fare_Rule = Fare_Rules(FlightID, FlightID1, Trackid, Stops)
            Fare_Rule = Fare_Rule['FareRuleInfo']['FareRuleText']


            #One_way_Total_price
            fare_description = pricing_details['PriceItenaryInfo'][0]['AvailabilityResponse'][0]['Fares'][0]['Faredescription']

            if len(fare_description) == 2 and fare_description[1]['Paxtype'] == 'CHD':
                childP = float(pricing_details['PriceItenaryInfo'][0]['AvailabilityResponse'][0]['Fares'][0]['Faredescription'][1]['GrossAmount']) * float(children)
            else:
                childP = 0.0

            if len(fare_description) == 2 and fare_description[1]['Paxtype'] == 'INF':
                infantP = float(pricing_details['PriceItenaryInfo'][0]['AvailabilityResponse'][0]['Fares'][0]['Faredescription'][1]['GrossAmount']) * float(infant)
            else:
                infantP = 0.0

            if len(fare_description) == 3:
                infantP = float(pricing_details['PriceItenaryInfo'][0]['AvailabilityResponse'][0]['Fares'][0]['Faredescription'][2]['GrossAmount']) * float(infant)
                childP = float(pricing_details['PriceItenaryInfo'][0]['AvailabilityResponse'][0]['Fares'][0]['Faredescription'][1]['GrossAmount']) * float(children)
        

            adultP = float(pricing_details['PriceItenaryInfo'][0]['AvailabilityResponse'][0]['Fares'][0]['Faredescription'][0]['GrossAmount']) * float(AdultCount)
            One_way_Total_price = adultP+childP+infantP

            #return_Total_price
            Rfare_description = pricing_details['PriceItenaryInfo'][1]['AvailabilityResponse'][0]['Fares'][0]['Faredescription']

            if len(Rfare_description) == 2 and Rfare_description[1]['Paxtype'] == 'CHD':
                childPR = float(pricing_details['PriceItenaryInfo'][1]['AvailabilityResponse'][0]['Fares'][0]['Faredescription'][1]['GrossAmount']) * float(children)
            else:
                childPR = 0.0

            if len(Rfare_description) == 2 and Rfare_description[1]['Paxtype'] == 'INF':
                infantPR = float(pricing_details['PriceItenaryInfo'][1]['AvailabilityResponse'][0]['Fares'][0]['Faredescription'][1]['GrossAmount']) * float(infant)
            else:
                infantPR = 0.0

            if len(Rfare_description) == 3:
                infantPR = float(pricing_details['PriceItenaryInfo'][1]['AvailabilityResponse'][0]['Fares'][0]['Faredescription'][2]['GrossAmount']) * float(infant)
                childPR = float(pricing_details['PriceItenaryInfo'][1]['AvailabilityResponse'][0]['Fares'][0]['Faredescription'][1]['GrossAmount']) * float(children)
        

            adultPR = float(pricing_details['PriceItenaryInfo'][1]['AvailabilityResponse'][0]['Fares'][0]['Faredescription'][0]['GrossAmount']) * float(AdultCount)
            retun_Total_price = adultPR+childPR+infantPR

            Total_price = One_way_Total_price + retun_Total_price

            context = {
                'pricing_details':pricing_details,
                'Fare_Rule':Fare_Rule,
                'Stops':Stops,
                'RStops':RStops,
                'Total_price':Total_price,
                'adultP':adultP,
                'childP':childP,
                'infantP':infantP,
                'TripType':TripType,
                'One_way_Total_price':One_way_Total_price,
                'retun_Total_price':retun_Total_price,

                #for api
                'AdultCount':AdultCount,
                'ChildCount':children,
                'InfantCount':infant,
                }
            return render(request, "pricing.html", context)
        
        except Exception as e:
            print(e)
            messages.error(request, 'Somthing went wrong')
            return redirect('index')

def IRflight_pricing(request):
    if request.method == 'POST':
            # amt
        adultBaseAmount = request.POST.get('adultBaseAmount')
        adultTotalTaxAmount = request.POST.get('adultTotalTaxAmount')
        childBaseAmount = request.POST.get('childBaseAmount', '0')
        childTotalTaxAmount = request.POST.get('childTotalTaxAmount', '0')
        infantBaseAmount = request.POST.get('infantBaseAmount', '0')
        infantTotalTaxAmount = request.POST.get('infantTotalTaxAmount', '0')

        print(f"adult:{adultBaseAmount}-{adultTotalTaxAmount} child:-{childBaseAmount}-{childTotalTaxAmount} inft:-{infantBaseAmount}-{infantTotalTaxAmount}")
        TotalBaseAmt = float(adultBaseAmount)+float(childBaseAmount)+float(infantBaseAmount)
        TotalGrossAmt = (float(adultTotalTaxAmount)+float(childTotalTaxAmount)+float(infantTotalTaxAmount))+TotalBaseAmt
        
        BaseOrigin = request.POST.get('BaseOrigin')
        BaseDestination = request.POST.get('BaseDestination')
        TripType = 'R'
        AdultCount = request.POST.get('AdultCount')
        ChildCount = request.POST.get('children')
        InfantCount = request.POST.get('infant')
        Trackid = request.POST.get('Trackid')
        flight_details_str = request.POST.get('FlightDetails')
        flight_details = ast.literal_eval(flight_details_str)
        selected_fields = ["FlightID", "FlightNumber", "Origin", "Destination", "DepartureDateTime", "ArrivalDateTime"]
        flight_pricing_details = [{key: flight[key] for key in selected_fields} for flight in flight_details]
        pricing_details = IRpricing(BaseOrigin, BaseDestination, TripType, AdultCount, ChildCount, InfantCount, Trackid, flight_pricing_details, TotalBaseAmt, TotalGrossAmt)
        print(pricing_details)

    context = {
                'pricing_details':pricing_details,
                'Total_price':TotalGrossAmt,
                'BaseOrigin':BaseOrigin,
                'BaseDestination':BaseDestination,
                'TripType':"IR",
                #for api
                'AdultCount':AdultCount,      
                'ChildCount':ChildCount,
                'InfantCount':InfantCount, 
    }
    return render(request, "pricing.html", context)

def flight_booking(request):
    booking_details = None
    FlightID1 = ''
    FlightNumber1 = ''
    Origin1 = ''
    Destination1 = ''
    DepartureDateTime1 = ''
    ArrivalDateTime1 = ''
    if request.method == 'POST':
        AdultCount = request.POST.get('AdultCount')
        ChildCount = request.POST.get('ChildCount')
        InfantCount = request.POST.get('InfantCount')
        Token = request.POST.get('Token')
        FlightID = request.POST.get('FlightID')
        FlightNumber = request.POST.get('FlightNumber')
        Origin = request.POST.get('Origin')
        Destination = request.POST.get('Destination')
        DepartureDateTime = request.POST.get('DepartureDateTime')
        ArrivalDateTime = request.POST.get('ArrivalDateTime')
        TotalAmount = request.POST.get('TotalAmount')
        PaxDetailsInfoi = request.POST.get('jsonData')
        jsonDataBaggagei = request.POST.get('jsonDataBaggage', '[]')
        jsonDataMeali = request.POST.get('jsonDataMeal', '[]')
        TripType = request.POST.get('TripType')
        TrackId = request.POST.get('TrackId')
        Stops = request.POST.get('Stops')
        PaxDetailsInfo = json.loads(PaxDetailsInfoi)
        jsonDataBaggage = json.loads(jsonDataBaggagei)
        jsonDataMeal = json.loads(jsonDataMeali)
        print(jsonDataMeal)
        # 1stop
        if Stops == '1':
            FlightID1 = request.POST.get('FlightID1')
            FlightNumber1 = request.POST.get('FlightNumber1')
            Origin1 = request.POST.get('Origin1')
            Destination1 = request.POST.get('Destination1')
            DepartureDateTime1 = request.POST.get('DepartureDateTime1')
            ArrivalDateTime1 = request.POST.get('ArrivalDateTime1')

        booking_details = Booking(AdultCount, ChildCount, InfantCount, Token, FlightID, FlightNumber, Origin, Destination, DepartureDateTime, ArrivalDateTime, TotalAmount, PaxDetailsInfo, TripType, TrackId, Stops, FlightID1, FlightNumber1, Origin1, Destination1, DepartureDateTime1, ArrivalDateTime1, jsonDataBaggage, jsonDataMeal)
        print(booking_details)

    if booking_details['Status']['Error']:
        error_message = booking_details['Status']['Error']
        redirect_url = reverse('index') + f'?error_message={error_message}'
        return redirect(redirect_url)


    context = {
        'booking_details':booking_details,
    }

    return render(request, 'invoice.html', context)

def Rflight_booking(request):
    FlightID1 = ''
    FlightNumber1 = ''
    Origin1 = ''
    Destination1 = ''
    DepartureDateTime1 = ''
    ArrivalDateTime1 = ''
    RFlightID1 = ''
    RFlightNumber1 = ''
    ROrigin1 = ''
    RDestination1 = ''
    RDepartureDateTime1 = ''
    RArrivalDateTime1 = ''
    if request.method == 'POST':
        AdultCount = request.POST.get('AdultCount')
        ChildCount = request.POST.get('ChildCount')
        InfantCount = request.POST.get('InfantCount')
        Token = request.POST.get('Token')
        FlightID = request.POST.get('FlightID')
        FlightNumber = request.POST.get('FlightNumber')
        Origin = request.POST.get('Origin')
        Destination = request.POST.get('Destination')
        DepartureDateTime = request.POST.get('DepartureDateTime')
        ArrivalDateTime = request.POST.get('ArrivalDateTime')
        TotalAmount = request.POST.get('One_way_Total_price')
        PaxDetailsInfoi = request.POST.get('jsonData')
        jsonDataBaggagei = request.POST.get('jsonDataBaggage', '[]')
        jsonDataMeali = request.POST.get('jsonDataMeal', '[]')
        TripType = request.POST.get('TripType')
        TrackId = request.POST.get('TrackId')
        Stops = request.POST.get('Stops')
        PaxDetailsInfo = json.loads(PaxDetailsInfoi)
        jsonDataBaggage = json.loads(jsonDataBaggagei)
        jsonDataMeal = json.loads(jsonDataMeali)
        print(jsonDataMeal)

            # 1stop
        FlightID1 = request.POST.get('FlightID1')
        FlightNumber1 = request.POST.get('FlightNumber1')
        Origin1 = request.POST.get('Origin1')
        Destination1 = request.POST.get('Destination1')
        DepartureDateTime1 = request.POST.get('DepartureDateTime1')
        ArrivalDateTime1 = request.POST.get('ArrivalDateTime1')

        #return
        RToken = request.POST.get('RToken')
        RFlightID = request.POST.get('RFlightID')
        RFlightNumber = request.POST.get('RFlightNumber')
        ROrigin = request.POST.get('ROrigin')
        RDestination = request.POST.get('RDestination')
        RDepartureDateTime = request.POST.get('RDepartureDateTime')
        RArrivalDateTime = request.POST.get('RArrivalDateTime')
        RTotalAmount = request.POST.get('retun_Total_price')
        RStops = request.POST.get('RStops')
        # R1stop
        RFlightID1 = request.POST.get('RFlightID1')
        RFlightNumber1 = request.POST.get('RFlightNumber1')
        ROrigin1 = request.POST.get('ROrigin1')
        RDestination1 = request.POST.get('RDestination1')
        RDepartureDateTime1 = request.POST.get('RDepartureDateTime1')
        RArrivalDateTime1 = request.POST.get('RArrivalDateTime1')
        try:
            booking_details = RBooking(AdultCount, ChildCount, InfantCount, Token, FlightID, FlightNumber, Origin, Destination, DepartureDateTime, ArrivalDateTime, TotalAmount, RToken, RFlightID, RFlightNumber, ROrigin, RDestination, RDepartureDateTime, RArrivalDateTime, RTotalAmount, PaxDetailsInfo, TripType, TrackId, Stops, RStops, FlightID1, FlightNumber1, Origin1, Destination1, DepartureDateTime1, ArrivalDateTime1, RFlightID1, RFlightNumber1, ROrigin1, RDestination1, RDepartureDateTime1, RArrivalDateTime1, jsonDataBaggage, jsonDataMeal)
            print(booking_details)
            context = {
                'booking_details':booking_details,
            }
            return render(request, 'invoice.html', context)
    
        except Exception as e:
            print(e)
            messages.error(request, 'Somthing went wrong')
            return redirect('index')
        
def IRflight_booking(request):
    if request.method == 'POST':
        AdultCount = request.POST.get('AdultCount')
        ChildCount = request.POST.get('ChildCount')
        InfantCount = request.POST.get('InfantCount')
        Token = request.POST.get('Token')
        Origin = request.POST.get('BaseOrigin')
        Destination = request.POST.get('BaseDestination')
        flight_details = request.POST.get('flight_details')
        flight_details_str = ast.literal_eval(flight_details)
        selected_fields = ["FlightID", "FlightNumber", "Origin", "Destination", "DepartureDateTime", "ArrivalDateTime"]
        flight_pricing_details = [{key: flight[key] for key in selected_fields} for flight in flight_details_str]
        TotalAmount = request.POST.get('TotalAmount')
        print(TotalAmount)
        PaxDetailsInfoi = request.POST.get('jsonData')
        jsonDataBaggagei = request.POST.get('jsonDataBaggage', '[]')
        jsonDataMeali = request.POST.get('jsonDataMeal', '[]')
        TripType = request.POST.get('TripType')
        TrackId = request.POST.get('TrackId')
        PaxDetailsInfo = json.loads(PaxDetailsInfoi)
        jsonDataBaggage = json.loads(jsonDataBaggagei)
        jsonDataMeal = json.loads(jsonDataMeali)

        try:
            booking_details = IRBooking(AdultCount, ChildCount, InfantCount, Token, flight_pricing_details, Origin, Destination, TotalAmount, PaxDetailsInfo, TripType, TrackId, jsonDataBaggage, jsonDataMeal)
         
            context = {
                'booking_details':booking_details,
            }
            return render(request, 'invoice.html', context)
    
        except Exception as e:
            print(e)
            messages.error(request, 'Somthing went wrong')
            return redirect('index')

def contact(request):
    return render(request, 'contact.html')
# payment
def create_order(request):
    pass