from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django import forms
from django.core import validators
from . import forms
import requests


'''
provided method to get district number given zipcode 
edits made: checked to see that the json object returned did not have results of 0, which is the case that the zip 
            code was not valid. If the zipcode was not vaild returned dictionary of empty values.
'''
def get_district_number(zipcode):
    resp = requests.get( 'https://congress.api.sunlightfoundation.com/districts/locate?zip={}'.format(zipcode))
    if resp.status_code != 200:
        print('Could not get district number' + resp.status_code)
    js = resp.json()
    if(len(js['results'])!=0):
        state_name = js['results'][0]['state']
        district_number = js['results'][0]['district']
        return {'state_name':state_name, 'district_number':district_number}
    else:
         return{'state_name':'','district_number':''}


'''
    paramaters: state associated with user inputed zipcode(attained through get_district_number call)
    return: Dictionary containing the list of the two senators' names, list of senators' ids
    description: get_senate method makes a call to the propublica api to get senators. The json object 
                from the api call is parsed to get relevant info i.e. senator names, and senator ids.
                Once parsed the method returns the senator names and senator ids associated with zip code user entered
                senators' ids are later used to query recent bills involving the senators. 
'''
def get_senate(state):
    headers = {'X-API-Key':'HeU67wOwjMas9zx1MWRRg4fB09F4YyJ87jgec6xv'}
    url = 'https://api.propublica.org/congress/v1/members/senate/'+ str(state)+'/current.json'
    resp = requests.get(url,headers=headers)
    if resp.status_code != 200:
        print('Could not get Representative' + str(resp.status_code))
    js = resp.json()
    if(len(js['results'])!=0):
        senator_names = [js['results'][0]['name'],js['results'][1]['name']]
        senator_ids = [js['results'][0]['id'],js['results'][1]['id']]
        return {'senator_names':senator_names,'senator_ids':senator_ids}
    else:
        senator_names = []
        senator_ids = []
        return{'senator_names':senator_names,'senator_ids':senator_ids}


'''
    paramaters: state and district number associatead with user inputed zipcode
    return: dictionary containing representative's name and representative's id
    description: get_house_rep method makes a call to the propublica api to get representative. The json object 
                from the api call is parsed to get relevant info i.e. representative's name, and representative's ids.
                Once parsed the method returns the representative's name and representative id associated with zip code user entered
                representative' ids are later used to query recent bills involving the representative. 
'''
def get_house_rep(state,district):
    headers = {'X-API-Key':'HeU67wOwjMas9zx1MWRRg4fB09F4YyJ87jgec6xv'}
    url = 'https://api.propublica.org/congress/v1/members/house/'
    url = url + str(state)+'/'+str(district)+'/'+'current.json'
    resp = requests.get(url,headers=headers)
    if resp.status_code != 200:
        print('Could not get Representative' + str(resp.status_code))
    js = resp.json()
    #parse json object for representative's name,id
    if(len(js['results'])!=0):
        representative_name = js['results'][0]['name']
        representative_id = js['results'][0]['id']
        return {'representative_name':representative_name,'representative_id':representative_id}
    else:
        representative_name = ''
        representative_id=''
        return {'representative_name':representative_name,'representative_id':representative_id}


'''
    paramaters: congressman's id
    return:  a list of dictionaries which specify the description of the bill, and the congressman's vote on the bill
    description: get_bills method makes a call to the propublica api to get a list of bills associated with the congressman via his/her id.BaseException
                 The api call returns a json object. The get_bills method then creates two objects, the first billCheck simply contains the bill's name
                 the second newBill contains all the neccessary data i.e. name and vote casted by congressman. The get_bills method loops through
                 every bill assoicated with the congressman and uses the list billChecker which contains billCheck objects to check for duplicates. If the 
                 bill is not in billsChecker get_bills adds the bill to to the list of bills to be rendered. 
'''
def get_bills(congressman_id):
    headers = {'X-API-Key':'HeU67wOwjMas9zx1MWRRg4fB09F4YyJ87jgec6xv'}
    url = 'https://api.propublica.org/congress/v1/members/'
    url = url +str(congressman_id)+'/votes.json'
    resp = requests.get(url,headers=headers)
    if resp.status_code != 200:
        print('Could not get Representative' + str(resp.status_code))
    js = resp.json()
    #list to be rendered
    bills = list()
    #list to be used for easy list contains comparison
    billsChecker = list()
    #Loop thorugh each bill returned in the Json object
    for i in range(0,len(js['results'][0]['votes'])):
        #bill to be used for contains comparison
        billCheck = {'description':js['results'][0]['votes'][i]['description']}
        #final bill
        newBill = {'description':js['results'][0]['votes'][i]['description']
                ,'position':js['results'][0]['votes'][i]['position']}
        if(billCheck not in billsChecker and billCheck['description']!=''):
           # print(newBill)
           billsChecker.append(billCheck)
           bills.append(newBill)
    return bills


'''
paramaters: request object 
    return:  a rendered webpage 
    description: zip_code_view method renders both the zip_code_form in forms.py, as well as the output of the user's 
    zipcode input only if the form is determined to be valid
                 
'''
def zip_code_view(request):
    form = forms.zip_code_form()
    if request.method == "POST":
        form = forms.zip_code_form(request.POST)
        if form.is_valid():
            #call to get_district_number using zip_code entered by the user
            results = get_district_number(format(form.cleaned_data['zip_code']))
            #if the zip code was valid,i.e. corresponds to a state
            if(results['state_name']):
            #call to get_senate method using the state name identified through the get_district_number method call
                senators = get_senate(results['state_name'])
                #check to see that state has senators
                if(senators['senator_ids']):    
                    list_of_Senator_Bills = list()
                    for senator_id in senators['senator_ids']:
                        list_of_Senator_Bills.append(get_bills(senator_id))
                else:
                    list_of_Senator_Bills=['','']
                
            #call to get_house_rep method using the state name and district number identified through the get_district_number method call
                rep =get_house_rep(results['state_name'],results['district_number'])
             #check to see that the zip code has a representative
                if(rep['representative_id']):
                    representative_bills = get_bills(rep['representative_id'])
                else:
                    representative_bills = {}
            #render the page using results attained throught the method calls above
                return render(request,'zipcoderesults.html',{'results':results,
                                                        'senators':senators['senator_names'],
                                                        'representative':rep['representative_name'],
                                                        'representative_bills':representative_bills,
                                                        'senator1_bills':list_of_Senator_Bills[0],
                                                        'senator2_bills':list_of_Senator_Bills[1]})
            # Case that the form is valid, but the zip code entered does not correspond to a state                                            
            else:
                 return render(request,'zipcodeform.html',{'form':form,'error':'INVALID ZIPCODE'})
            #otherwise render page with form validation errors
    return render(request,'zipcodeform.html',{'form':form,'formErrors':form.errors})


