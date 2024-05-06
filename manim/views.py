 

from django.shortcuts import render
from django.conf import settings
from io import StringIO
import sys
import os
import subprocess
import re

from datetime import datetime, timedelta

def delete_old_files(media_dir):
    threshold_time = datetime.now() - timedelta(minutes=10)

    for filename in os.listdir(media_dir):
        filepath = os.path.join(media_dir, filename)
        modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        if modified_time < threshold_time:
            os.remove(filepath)
            print(f'Deleted {filename}')


def execute_code(request):
    #saving the entered code
    previous_code = request.POST.get('code', '')  

    if request.method == 'POST':
        #delete old files
        image_dir = os.path.join(settings.BASE_DIR, 'media')
        delete_old_files(media_dir)

        #save the code as a python file 
        code = request.POST.get('code', '')
        python_file = save_python_code_to_file(code)

        # find class name
        # we need this because the resultant video is saved in a folder named after class name.  
        pattern = r"class\s+(\w+)\s*\(" # example: class class_name(scene)

        for line in code.split('\n'):
            # Use regular expression to find the class name
            match = re.match(pattern, line)
            if match:
                # If a match is found, extract the class name
                class_name = match.group(1)
                #print("Class name:", class_name)
                break  # Stop searching after the first match
        else:
            print("No match found.")
            class_name="undefined"

        try:
            # execute the python file using manim    
            activate_script = '/home/ubuntu/env/bin/activate'
            result = subprocess.run(['bash', '-c', f'source {activate_script} && manim -ql {python_file}'], capture_output=True,text=True)
          
            # Check if the command was successful (exit code 0)
            if result.returncode == 0:
                output = result.stdout
                result_message = '' #we don't need error message if command is executed successfully
                #result_message = f"Shell command executed successfully. Output:\n{output}"
            else:
                error_message = result.stderr
                result_message = f"Error executing shell command: {error_message}"
        except Exception as e:
            result_message = f"Error executing shell command: {e}"


        #after HTTP request
        context = {'result_message':result_message,
                   'previous_code': previous_code,
                   'MEDIA_URL': settings.MEDIA_URL,
                   'class_name':class_name,
                }
        return render(request, 'run.html',context)  
         
    #before HTTP request
    context = {'previous_code': previous_code,
               'MEDIA_URL': settings.MEDIA_URL,
            }
    return render(request, 'run.html',context )


def save_python_code_to_file(code):
    # Define the directory where Python files will be saved
    app_dir = os.path.join(settings.BASE_DIR, 'manim')
    save_dir = os.path.join(app_dir, 'python_code_files')
    os.makedirs(save_dir, exist_ok=True)  # Create the directory if it doesn't exist

    # Generate a unique filename for the Python file
    filename = os.path.join(save_dir, 'user_code.py')

    # Write the user's Python code to the file
    with open(filename, 'w') as file:
        file.write(code)

    return filename