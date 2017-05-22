from django import forms
from django.core import validators
from localflavor.us import forms as us_forms
import re


'''
module description: this forms module defines the zip_code_form used to allow the user to enter their zipcode
                    Also includes validator (required_empty,zip_code) methods to ensure proper input is given to form,and no errors
                    are thrown during api calls.
'''


'''  
    paramaters: value associated with the hidden input field
    return: Raises a form Validation error only if the hidden input field is not empty(sign of a bot)
    description: required_empty is a simple validation method used to ensure that bots don't malicioulsy submit requests through the form
                 If the hidden field on the form contains any input, raise a validation error to prevent form from submiting any requests
'''
def required_empty(value):
    if value:
        raise forms.ValidationError('is not empty,You are a Bot!')


'''
    paramaters: value associated with the zip_code field
    return: raises a form Validation error only if the user does not enter a proper zip code in teh form of 5 digits. 
    description: Attempts to match the user's input to the regex expression,which specifies exactly 5 digits. If the user's input 
                is not exactly 5 digits throw a form Validation error prompting the user to enter a proper zipcode. 

'''
def zip_code(value):
    if re.match(r'\b\d{5}\b', str(value)) is None:
         raise forms.ValidationError('Please Enter a proper Zip Code i.e. XXXXX')


'''
    class description: zip_code_form is the zip code form to be rendered by the zip_code_form view in views.py, which prompts the user for their zipcode
'''
class zip_code_form(forms.Form):
    #zip_code input field uses zip_code validator method defined above
    zip_code = forms.IntegerField(validators =[zip_code])
    #zip_code = us_forms.USZipCodeField()---> does not actually work due to API Call that translates ZIP Code to State
    #honeypot field to be used for bot detection used validator method required_empty above
    honeypot = forms.CharField(required=False,
                                widget=forms.HiddenInput,
                                label ="Please Leave Empty",
                                validators=[required_empty]
                            )

    
   