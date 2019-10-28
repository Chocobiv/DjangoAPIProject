from rest_framework import viewsets, serializers
from .models import Essay, Album, Files
from .serializers import EssaySerializer, AlbumSerializer, FilesSerializer
from rest_framework.filters import SearchFilter
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

class PostViewSet(viewsets.ModelViewSet):
    # 어떤 모델을 기반으로 queryset을 만들것인지를 등록해줘야 한다
    queryset = Essay.objects.all()
    serializer_class = EssaySerializer

    # 검색 -> filters 라이브러리 사용
    filter_backends = [SearchFilter]
    search_fields = ('title', 'body')

    # serializers.py 에 있는 author_name 자동으로 저장했으면 좋겠다
    def perform_create(self, serializer):
        # 내가 지금 작성한 user로 author 필드를 저장하겠다
        serializer.save(author=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()

        # 현재 request를 보낸 user == self.request.user
        if self.request.user.is_authenticated:
            qs = qs.filter(author = self.request.user)
        else:
            qs = qs.none()

        return qs

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer


class FileViewSet(viewsets.ModelViewSet):
    queryset = Files.objects.all()
    serializer_class = FilesSerializer

    # file이 안올라가는 문제 해결하기 위해 해야할 것!
    # 1. parser_class 지정
    # MultiPartParser, FormParser?
    # -> file은 업로드될 수 있는 파일형식이 여러가지라서 그런 다양한 형식들을 업로드하기위한 것~
    parser_classes = (MultiPartParser, FormParser)
    # 2. create() 오버라이딩
    # create() -> post함수!
    def post(self, request, *args, **kargs):
        # FilesSerializer 받아와서
        serializer = FilesSerializer(data=request.data)
        # 유효성 검사하고
        if serializer.is_valid():
            # 유효하면 저장하고 serializer 데이터와 함께 HTTP_201 statsu return해라
            serializer.save()
            return Response(serializer.data, statsu=HTTP_201_CREATED)
        else:
            # 유효하지 않으면 BAD_REQUEST와 함께 error를 띄워라
            return Response(serializer.error, statsu=HTTP_400_BAD_REQUEST)

