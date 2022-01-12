from django import forms
from .models import Post
from .models import Fuser #DB의 Fuser와 데이터 비교를 위한 참조
from django.contrib.auth.hashers import check_password #패스워드 비교를 위한 참조 

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['con_f_name','file_a','file_b']
        # fields = ['title', 'cover','file_a']


class LoginForm(forms.Form):
    username = forms.CharField(max_length=32, label="아이디",
        error_messages={
            'required':"아이디를 입력하세요"
        })
    password = forms.CharField(label="비밀번호", widget=forms.PasswordInput,
        error_messages={
            'required':"비밀번호를 입력하세요"
        } )

    #유효성 검사하는 clean 메소드를 오버라이드
    def clean(self):
        clean_data = super().clean() #역추적해보면 원래 cleaned_data를 리턴하고있다.
        # 비어있지않은 데이터라면
        username = clean_data.get('username') #requestd에서 값 받아오는 것과 유사
        password = clean_data.get('password')

        # 회원 일치 조회
        if username and password : #2개 변수값이 둘다 None이 아니라면
            fuser = Fuser.objects.get(username=username) #기존 DB와 일치하는 Fuser 모델 가져오기

            if not check_password(password, fuser.password) : #비밀번호가 일치안하면
                self.add_error('password','비밀번호가 틀렸습니다.') #password필드에 에러메시지 추가
            else : #일치하면
                self.user_id = fuser.id #현재 일치하는 fuser의 pk(즉 id)를 user_id 변수로 생성해주자.