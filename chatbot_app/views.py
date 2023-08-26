from django.shortcuts import render,redirect
from django.http import JsonResponse
import openai
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
import google.generativeai as palm
from django.contrib import messages   ##to delete the history

from django.utils import timezone
from django.contrib.auth.decorators import login_required


## Palm llm api key
palm_api_key = ''
palm.configure(api_key=palm_api_key)


#from . views import chatbot
open_ai_key = 'Enter API'
openai.api_key = open_ai_key

contexts = ""
def ask_palm(context,message):
    response = palm.chat(context=context, messages=message)
    answer = response.last
    return answer

def ask_openai(message):
    response = openai.Completion.create(
        model ="text-davinci-003",
        prompt = message,
        max_tokens = 150,
        n =1,
        stop = None,
        temperature = 0.9,
    )
    print(response)
    answer = response['choices'][0]['text']
    return answer
# Create your views here.
@login_required

def chatbot(request):
    user_chats = Chat.objects.filter(user=request.user) #.order_by('-created_at')
    last_chat = user_chats.last()  # Get the last chat of the user

    if request.method == 'POST':
        message = request.POST.get('message')
        context = last_chat.response if last_chat else ''  # Use the response of the last chat as the context

        #response = ask_openai(context + ' ' + message)  # Append the message to the context and send it to OpenAI
        response = ask_palm(context + ' ' + message, message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()

        return JsonResponse({'message': message, 'response': response})

    return render(request, 'chatbot.html', {'chats': user_chats})


def login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')
    

def register(request):
    if request.method=='POST':
        username = request.POST['username']
        email = request.POST['email']
        password1  = request.POST['password1']
        password2  = request.POST['password2']
        if password1 == password2:
            try:
                user = User.objects.create_user(username,email,password1)
                user.save()
                auth.login(request,user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating user'
                return render(request,'register.html',{'error_message':error_message})
        else:
            error_message = 'Password not matching'
            return render(request,'register.html',{'error_message':error_message})

    return render(request,'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')

#deleting the chat history
def delete_chat_history(request):
    if request.method == 'POST':
        Chat.objects.filter(user=request.user).delete()
        messages.success(request, 'Chat history deleted successfully.')
    return redirect('chatbot')