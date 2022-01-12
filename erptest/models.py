from django.db import models

# Create your models here.


class Post(models.Model):
    con_f_name = models.CharField(max_length=100)
    file_a = models.FileField(upload_to='static/')
    file_b = models.FileField(upload_to='static/')
    def __str__(self):
        return self.file_a

class Fuser(models.Model):  # models.Model를 상속
    objects = models.Manager()
    username = models.CharField(max_length=32,
                                verbose_name='사용자명'  # admin 페이지에서 보일 컬럼명
                                )
    permission_u = models.CharField(max_length=32,
                                verbose_name='권한'  # admin 페이지에서 보일 컬럼명
                                )
    name_hs = models.CharField(max_length=32,
                                verbose_name='이름'  # admin 페이지에서 보일 컬럼명
                                )
    password = models.CharField(max_length=64,
                                verbose_name='비밀번호'  # admin 페이지에서 보일 컬럼명
                                )
    register_dttm = models.DateField(auto_now_add=True, # 자동으로 해당 시간이 추가됨
                                     verbose_name="가입날짜"
                                     )


    #데이터가 문자열로 변환이 될 때 어떻게 나올지(반환해줄지) 정의하는 함수가 __str__이다.
    def __str__(self):
        return self.username


    #별도로 테이블명을 지정하고 싶을 때 쓰는 코드(안해도 됨)
    class Meta:
        db_table = 'user_define_fuser_table' #테이블 명 지정
        verbose_name = '사용자 모임' #노출될 테이블 이름 변경
        verbose_name_plural = '사용자 모임'

class Document(models.Model):
    title = models.CharField(max_length = 200)
    uploadedFile = models.FileField(upload_to = "Uploaded Files/")
    dateTimeOfUpload = models.DateTimeField(auto_now = True)
    
    #별도로 테이블명을 지정하고 싶을 때 쓰는 코드(안해도 됨)
    class Meta:
        db_table = 'user_define_uploadfilestest_table' #테이블 명 지정
        verbose_name = '업로드파일목록' #노출될 테이블 이름 변경
        verbose_name_plural = '업로드파일목록'