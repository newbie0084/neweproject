#my_settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', #1
        'NAME': 'test', #2
        'USER': 'root', #3                      
        'PASSWORD': 'password',  #4              
        'HOST': 'localhost',   #5                
        'PORT': '3306', #6
    }
}
SECRET_KEY ='django-insecure-gq5=2_i+2)-g)6m02#=(97gxfdaljgd5ap0iog_a79qq%fzo1+'