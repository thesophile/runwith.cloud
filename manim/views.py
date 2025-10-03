 

from django.shortcuts import render, redirect
from django.conf import settings
from io import StringIO
import sys
import os
import subprocess
import re
import shutil
from datetime import datetime, timedelta
import time
from django.http import JsonResponse
from .utils import *
from .cache_utils import *
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Code 


from django.shortcuts import render
from django.conf import settings
import subprocess
import os
import docker

import traceback





def run_manim_command(image_name, base_dir, class_name):
    client = docker.from_env()

    user_code = 'user_code.py'
    
    # Define the volumes
    volumes = {
        f"{base_dir}/manim/python_code_files": {'bind': '/mnt/code', 'mode': 'rw'},
        f"{base_dir}/media": {'bind': '/mnt/output', 'mode': 'rw'}
    }
    
    # Define the command with the appropriate paths
    docker_command = f"manim -ql /mnt/code/{user_code} -o /mnt/output/{class_name}"
    
    try:
        # Create and start the container
        container = client.containers.run(
            image_name,
            docker_command,
            volumes=volumes,
            detach=True
        )
        
        # Wait for the container to finish and get the logs
        result = container.wait()
        logs = container.logs().decode()
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        if container:

            # Remove the container
            try:
                container.remove(force=True)
            except Exception as e:
                return f"Error removing container: {str(e)}"
    
    return logs



def run_docker_command(class_name):
    image_name = 'manimcommunity/manim'
    base_dir = os.path.join(settings.BASE_DIR)  
    try:
        run_manim_command(image_name, base_dir, class_name)
        result_message = ''

    except Exception as e:
        result_message = (
            "Error executing shell command:\n"
            f"{type(e).__name__}: {e}"
        )
        #full traceback for logs:
        full_tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        print(result_message)
        print("---- FULL TRACE FOR LOG ----")
        print(full_tb)


    return result_message    






 



import ast

current_code_name = None

def validate_user_input(user_input):
    blacklist = [';', '&', 'rm ', '`', ' sys' , ' os']  
    try:
        for item in blacklist:
            if item in user_input:
                print(f'Blacklisted item: {item}')
                return False
        return True    

    except SyntaxError:
        return False

 
 



def execute_code(request):

    saved_codes = Code.objects.filter(user=request.user) if request.user.is_authenticated else None
    
    #saving the entered code
    previous_code = get_previous_code()
    # previous_code = request.POST.get('code', '')

    current_code_name = get_current_code_name()

    if request.method == 'POST' and request.POST.get('form_type') == 'execute':
        processsed = False
        #delete old files
        media_dir = os.path.join(settings.BASE_DIR, 'media')

        delete_old_files(media_dir)

        current_code_name = get_current_code_name() # The name of the code opened or created

        #save the code as a python file 
        code = request.POST.get('code', '')
        python_file = save_python_code_to_file(code) #in utils.py

        previous_code = code
        #save code to cache
        save_to_cache(previous_code)

        # find class name
        class_name = find_class_name(code) # we need this because the resultant video is saved in a folder named after class name. 

        print(f'class name: {class_name}')

        result_message = run_docker_command(class_name)

        print(f'previous code:{previous_code}')        

        #after HTTP request
        context = {'result_message':result_message,
                   'previous_code': previous_code,
                   'MEDIA_URL': settings.MEDIA_URL,
                   'class_name':class_name,
                   'placeholder': False,
                   'saved_codes':saved_codes,
                   'request': request,
                   'current_code_name':current_code_name,
                }
        return render(request, 'manim/manim.html',context)  
         
    #before HTTP request
    placeholder = True
    context = {'previous_code': previous_code,
               'MEDIA_URL': settings.MEDIA_URL,
               'placeholder':placeholder,
               'processed' : False,
               'saved_codes':saved_codes,
               'request': request, 
               'current_code_name':current_code_name,
            }
    return render(request, 'manim/manim.html',context )

@csrf_exempt
def save_new_code(request):
    if request.method == 'POST' and request.POST.get('form_type') == 'save':
        print('save button clicked')
        code_text = request.POST.get('hidden_code_new')
        save_to_cache(code_text)
        name = request.POST.get('name')
        if name:
            # Save the code with the entered name
            Code.objects.create(user=request.user, code_text=code_text, name=name)
            set_current_code_name(name)
            print('code saved')
            # return redirect('home')  # Redirect to home page or wherever you want
        # Handle case where name is not provided (optional)
    return redirect('manim_home')  # Redirect back to execute page after saving

## Old save function
# def save_current_code(request):
#     if request.method == 'POST' and request.POST.get('form_type') == 'save_current':
#         print('save button clicked')
#         new_code_text = request.POST.get('hidden_code_current')
#         save_to_cache(new_code_text)
#         print(new_code_text)
#         current_code_name = get_current_code_name()
#         print(f'current_code_name:{current_code_name}')
#         if current_code_name:
#             # Save the code with the entered name
#             Code.objects.filter(user=request.user, name=current_code_name).update(code_text=new_code_text)
#             print('code saved')
#             #save code to display locally
             
#             # return redirect('home')  # Redirect to home page or wherever you want
#         else:
             
#             print('current_code_name not defined')
    
#     return redirect('manim_home')  # Redirect back to execute page after saving

# @csrf_exempt
# def save_current_code(request):
#     print('save button clicked')
#     new_code_text = request.POST.get('code_text')
#     save_to_cache(new_code_text)
#     print(new_code_text)
#     current_code_name = get_current_code_name()
#     print(f'current_code_name:{current_code_name}')
#     if current_code_name:
#         # Save the code with the entered name
#         Code.objects.filter(user=request.user, name=current_code_name).update(code_text=new_code_text)
#         print('code saved')
#         #save code to display locally
        
#         # return redirect('home')  # Redirect to home page or wherever you want
#     else:
        
#         print('current_code_name not defined')
    
#     return redirect('manim_home')  # Redirect back to execute page after saving   
         

@csrf_exempt  # testing
def save_current_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_code_text = data.get('code_text')

            save_to_cache(new_code_text)
            print(new_code_text)
            
            if not new_code_text:
                return JsonResponse({'status': 'error', 'message': 'Code text is required'}, status=400)

            current_code_name = get_current_code_name()

            if not current_code_name:
                print ("No current Code name") 
                print(f'current_code_name:{current_code_name}')
            
            # Save the code with the entered name
            Code.objects.filter(user=request.user, name=current_code_name).update(code_text=new_code_text)
            print('code saved')
            
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    

# def get_code(request, code_id):
#     code = Code.objects.get(id=code_id, user=request.user)
#     return JsonResponse({'code_text': code.code_text})

def get_code_text(request, code_id):
    code = Code.objects.get(id=code_id)
    set_current_code_name(code.name)
    print(f'Current code name set as {code.name}') 
    return JsonResponse({'code_text': code.code_text,'code_name':code.name})

def contact(request):
    return render(request, 'contact.html')

# update the django varible 'previous_code' when user opens a code 
@csrf_exempt
def update_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_code = data.get('code_text')
        save_to_cache(new_code) 
        return JsonResponse({'status': 'success', 'code_text': new_code})
    return JsonResponse({'status': 'failed'})


def set_code_name(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)  # Parse JSON data from the request
        code_name = data.get('code_name')

        # Call your util.py function
        result = set_current_code_name(code_name)

        # Respond with success
        return JsonResponse({"status": "success", "message": "Code name set successfully", "result": result})

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

def get_code_name(request):
    if request.method == "POST":
        import json

        # Call your util.py function
        result = get_current_code_name()

        # Respond with success
        return JsonResponse({"status": "success", "message": "Code name set successfully", "result": result})

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
