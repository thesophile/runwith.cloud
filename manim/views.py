 

from django.shortcuts import render
from django.conf import settings
from io import StringIO
import sys
import os
import subprocess

def execute_code(request):
    previous_code = request.POST.get('code', '')  
    if request.method == 'POST':
        code = request.POST.get('code', '')
        try:
            python_file = save_python_code_to_file(code)
            
            #print(python_file)
            result = subprocess.run(['manimce','-ql', python_file], capture_output=True, text=True)
            
            # Check if the command was successful (exit code 0)
            if result.returncode == 0:
                output = result.stdout
                result_message = f"Shell command executed successfully. Output:\n{output}"
            else:
                error_message = result.stderr
                result_message = f"Error executing shell command: {error_message}"
        except Exception as e:
            result_message = f"Error executing shell command: {e}"



        #     # Capture the output of the executed code
        #     stdout = sys.stdout
        #     sys.stdout = StringIO()  # Redirect stdout to a StringIO object
        #     exec(code, globals(), locals())
        #     result = sys.stdout.getvalue()  # Get the output of the executed code
        #     sys.stdout = stdout  # Restore original stdout
        # except Exception as e:
        #     result = f"Error executing code: {e}"
        context = {'result':result_message,
                   'previous_code': previous_code,
                   'MEDIA_URL': settings.MEDIA_URL,
        }
        return render(request, 'run.html',context)       
    from django.template.loader import select_template

    template = select_template(['run.html'])
    print("Template path:", template.origin.name)     
    return render(request, 'run.html', {'previous_code': previous_code,'MEDIA_URL': settings.MEDIA_URL,})


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