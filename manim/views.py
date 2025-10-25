 

import os
import docker
import traceback
import json
import ast
import uuid

from .models import Code 

from .utils import *
from .cache_utils import *

from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django_q.tasks import async_task
from django_q.models import OrmQ, Task






def run_manim_command(image_name, base_dir, media_name):
    client = docker.from_env()
    container = None  # Initialize container to None

    user_code = 'user_code.py'
    
    # Define the volumes
    volumes = {
        f"{base_dir}/manim/python_code_files": {'bind': '/mnt/code', 'mode': 'ro'},
        f"{base_dir}/media": {'bind': '/mnt/output', 'mode': 'rw'}
    }
    
    # Define the command with the appropriate paths
    docker_command = f"manim -ql /mnt/code/{user_code} -o /mnt/output/{media_name}"

    # Resource limits
    mem_limit = "512m"     # 512MB memory
    cpus = 0.8             # max 0.8 of 1 vCPU
    pids_limit = 64        # max processes

    # Timeout in seconds for long-running jobs
    timeout_seconds = 300   # adjust based on your rendering needs
    
    try:
        # Run container detached
        container = client.containers.run(
            image=image_name,
            command=docker_command,
            volumes=volumes,
            detach=True,
            user="manimuser",
            # name="manim_container",
            mem_limit=mem_limit,
            nano_cpus=int(cpus * 1e9),  # docker-py uses nanoseconds
            pids_limit=pids_limit,
            network_disabled=True,       # disable network
            security_opt=["no-new-privileges"],
            read_only=False,
            tmpfs={"/tmp": "rw,size=128m"},
            remove=False                  # do not auto-remove, we'll do it manually
        )

        # Wait for the container to finish, with a timeout
        result = container.wait(timeout=timeout_seconds)
        exit_code = result.get('StatusCode', -1)

        # Get logs
        logs = container.logs().decode()
        print("=== CONTAINER LOGS ===")
        print(logs)

        if exit_code != 0:
            print(f"Container exited with non-zero status code: {exit_code}")

    except docker.errors.ContainerError as e:
        print(f"Container failed: {e}")
    except docker.errors.APIError as e:
        print(f"Docker API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if container:
            try:
                container.remove(force=True)
            except Exception as e:
                print(f"Error removing container: {e}")
    
    return logs



def run_docker_command(media_name):
    image_name = 'manimcommunity/manim'
    base_dir = os.path.join(settings.BASE_DIR)  
    try:
        logs = run_manim_command(image_name, base_dir, media_name)
        # On success, return the logs. Django-Q will save this as the task result.
        return logs
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
        # save_to_cache(previous_code)

        # find class name
        class_name = find_class_name(code) # we need this because the resultant video is saved in a folder named after class name. 

        print(f'class name: {class_name}')

        random_id = uuid.uuid4().hex[:8]
        media_name = f"{class_name}_{random_id}"
        print(f'media_name: {media_name}')

        # The hook is removed by only passing the target function and its arguments.
        # This is the correct call for your use case.
        task_id = async_task(run_docker_command, media_name)
        print('Docker task started asynchronously')
        print(f'task id: {task_id}')
        result_message = ""

        # print(f'previous code:{previous_code}')        

        #after HTTP request
        context = {'result_message':result_message,
                   'previous_code': previous_code,
                   'MEDIA_URL': settings.MEDIA_URL,
                   'media_name':media_name,
                   'placeholder': False,
                   'saved_codes':saved_codes,
                   'request': request,
                   'current_code_name':current_code_name,
                   'task_id':task_id,
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




def get_task_status(task_id):
    # 1. Completed or failed
    if Task.objects.filter(id=task_id).exists():
        task = Task.objects.get(id=task_id)
        return "done" if task.success else "failed"

    # 2. Still queued
    if OrmQ.objects.filter(payload__contains=task_id).exists():
        return "queued"

    # 3. Neither queued nor done → must be processing
    return "processing"
 

def task_status_view(request, task_id):
    status = get_task_status(str(task_id))
    return JsonResponse({'status': status})
