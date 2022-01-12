from django.contrib import admin
from .models import Fuser
from .models import Document

# Register your models here.

class FuserAdmin(admin.ModelAdmin): #admin의 ModelAdmin 클래스를 상속
    # pass #상속만 받아 새로운 클래스를 생성
    list_display = ('username','password','permission_u','register_dttm')

admin.site.register(Fuser,FuserAdmin) #admin 페이지에 등록


class DocumentAdmin(admin.ModelAdmin): #admin의 ModelAdmin 클래스를 상속
    # pass #상속만 받아 새로운 클래스를 생성
    list_display = ('title','dateTimeOfUpload')

admin.site.register(Document,DocumentAdmin) #admin 페이지에 등록