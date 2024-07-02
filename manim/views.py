 

from django.shortcuts import render
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









# def run_docker_command(class_name):
#     image_name = 'manimcommunity/manim'
#     base_dir = os.path.join(settings.BASE_DIR)  
#     user_code = 'user_code.py'
#     try:
#         result = run_manim_command(image_name, base_dir, user_code, class_name)
#         return JsonResponse(result)
#     except Exception as e:
#         return JsonResponse({'status': 'error', 'error': str(e)})



import ast

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

def run_manim(class_name,code):
    try:

        if not validate_user_input(code):
            print("Invalid input")
            result_message = 'Invalid input'
            return result_message

        base_dir = os.path.join(settings.BASE_DIR)  

        #activate_script = f'. {base_dir}/manimenv/bin/activate'

        manim_command = f'{base_dir}/manimenv/bin/manim -ql {base_dir}/manim/python_code_files/user_code.py -o {base_dir}/media/{class_name}'  

        #full_command = f'{activate_script} && {manim_command}'

        manim_command_list = manim_command.split()

        print(f"Running Manim command: {manim_command}")

        result = subprocess.run(
            manim_command_list,
            capture_output=True, 
            text=True
            )

        # stdout, stderr = process.communicate()

        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)



        # while True:
        #     if check_file_exists(class_name):
        #         break
        #     print(check_file_exists(class_name))
        #     time.sleep(2)    
            


        # print('Removing container...')
        # os.system('sudo docker rm -f docker_container')

        # Proceed to the next step
        # output = result.stdout
        
        print("Proceeding to the next step...")
        result_message = ''
        return result_message

    except subprocess.CalledProcessError as e:
        # Handle the case when the command returns a non-zero exit code
        print(" command failed with return code:", e.returncode)
        print(e.stderr)
        result_message = e.stderr
        return result_message
    except Exception as e:
        # Handle any other exceptions that may occur
        print("An error occurred:", e)
        result_message = e
        return result_message
        
# --private={base_dir}/sandbox --private={base_dir}/manim/python_code_files --private={base_dir}/media --private={base_dir}/manimenv

# manim_command = f'sudo docker run --name docker_container -v $(pwd)/manim/python_code_files:/mnt/code -v $(pwd)/media:/mnt/output manim-image manim -ql /mnt/code/user_code.py -o /mnt/output/just_name'
        

        # manim_command = f'sudo docker run -d --rm -v {base_dir}/manim/python_code_files:/mnt/code -v {base_dir}/media:/mnt/output manim-image manim -ql /mnt/code/user_code.py -o /mnt/output/{class_name}'

        

        # test_command = ['sudo','docker','run','--rm','-v',f'{base_dir}/manim/python_code_files:/mnt/code','-v',f'{base_dir}/media:/mnt/output','manim-image','manim','-ql','/mnt/code/user_code.py','-o',f'/mnt/output/{class_name}']

        # test_command = ['docker','run','manimcommunity/manim']

        

        # process = subprocess.Popen(
        #     command,
        #     stdout=subprocess.PIPE, 
        #     stderr=subprocess.PIPE
        #     )

        # print(f'command list: {command.split()}')

        # full_command = command.split()

# def run_docker_command():

#     class_name = "demo_classname"
#     image_name = 'manimcommunity/manim'
#     base_dir = os.path.join(settings.BASE_DIR)  
#     user_code = 'user_code.py'
#     try:
#         run_manim_command(image_name, base_dir, user_code, class_name)
#         result_message = ''

#     except Exception as e:
#         result_message = f"Error executing shell command: {e}"

#     return result_message    




def execute_code(request):

    
    
    #saving the entered code
    previous_code = request.POST.get('code', '')

    if request.method == 'POST':
        processsed = False
        #delete old files
        media_dir = os.path.join(settings.BASE_DIR, 'media')

        delete_old_files(media_dir)

        #save the code as a python file 
        code = request.POST.get('code', '')
        python_file = save_python_code_to_file(code)

        # find class name
        class_name = find_class_name(code) # we need this because the resultant video is saved in a folder named after class name. 

        print(f'class name: {class_name}')

        result_message = run_manim(class_name,code)        

        #after HTTP request
        context = {'result_message':result_message,
                   'previous_code': previous_code,
                   'MEDIA_URL': settings.MEDIA_URL,
                   'class_name':class_name,
                   'placeholder': False,
                }
        return render(request, 'manim/manim.html',context)  
         
    #before HTTP request
    placeholder = True
    context = {'previous_code': previous_code,
               'MEDIA_URL': settings.MEDIA_URL,
               'placeholder':placeholder,
               'processed' : False
            }
    return render(request, 'manim/manim.html',context )


