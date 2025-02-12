from django.contrib.auth.models import User, Group
from rest_framework import viewsets, views
from service.serializers import PlayerSerializer, GroupSerializer, PlaySerializer
from rest_framework.response import Response
from rungame import Game
from service.models import Player, Experiment, Play
from rest_framework import status
from rest_framework.renderers import JSONRenderer

class PlayerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class LoginUserView(views.APIView):

    def post(self,request, *args, **kw):
        # Process any get params that you may need
        # If you don't need to process get params,
        # you can skip this part
        #get_arg1 = request.GET.get('arg1', None)
        #get_arg2 = request.GET.get('arg2', None)

        # Any URL parameters get passed in **kw
        #myClass = CalcClass(get_arg1, get_arg2, *args, **kw)
        try:
            username = request.DATA.get('username', None)
            password = request.DATA.get('password', None)
            if username and password:
            # share_url(email, url)
                j = Player.objects.get(username=username)
                if j.password == password:

                    service = Game().get_instance()
                    service.register_user(j)

                    return Response({"success": True})
                else:
                    return Response({"success": False, "msg":"username and password do not match!!"})
        except Exception as e:
            return Response({"success": False, "msg":"An error has occurred!", "exception": str(e)})

class ReadyToPlayView(views.APIView):

    def get(self, request, *args, **kw):
        # Process any get params that you may need
        # If you don't need to process get params,
        # you can skip this part
        #get_arg1 = request.GET.get('arg1', None)
        #get_arg2 = request.GET.get('arg2', None)

        # Any URL parameters get passed in **kw
        #myClass = CalcClass(get_arg1, get_arg2, *args, **kw)

        service = Game().get_instance()
        isReady = service.readyToPlay()

        #response = Response(isReady,status.HTTP_200_OK)
        return Response({"levelReadyToPlay:":isReady},status.HTTP_200_OK)

class GetAreaView(views.APIView):

    def get(self, request, *args, **kw):
        # Process any get params that you may need
        # If you don't need to process get params,
        # you can skip this part
        #get_arg1 = request.GET.get('arg1', None)
        #get_arg2 = request.GET.get('arg2', None)

        # Any URL parameters get passed in **kw
        #myClass = CalcClass(get_arg1, get_arg2, *args, **kw)

        service = Game().get_instance()
        area = service.getArea()

        a = []
        for i in range(len(area)):
            for j in range(3):
              a.append(area[i][j])

        #response = Response(area,status.HTTP_200_OK)
        return Response({"area:":a},status.HTTP_200_OK)

class GetPlaysView(views.APIView):

    def get(self, request, *args, **kw):
        # Process any get params that you may need
        # If you don't need to process get params,
        # you can skip this part
        #get_arg1 = request.GET.get('arg1', None)
        #get_arg2 = request.GET.get('arg2', None)

        # Any URL parameters get passed in **kw
        #myClass = CalcClass(get_arg1, get_arg2, *args, **kw)

        #username = request.GET.get('arg1', None)
        try:
            username = self.kwargs['username']
            username = username.replace("/","")
            service = Game().get_instance()
            user = service.getUserFromGameUsers(username)
            if user is not None:
                plays = service.getPlays(user)
                msg = "["
                for i in range(len(plays)):
                    msg += '{\"id\":' + str(plays[i].id) + ","
                    msg += '"level":' + str(plays[i].level) + ","
                    msg += '"chromosomeOne":' + plays[i].chromosomeOne + ","
                    msg += '"chromosomeTwo":' + plays[i].chromosomeTwo + ","
                    if i != len(plays)-1:
                        msg += '"player:":"' + plays[i].play_player.username + '},'
                    else:
                        msg += '"player:":"' + plays[i].play_player.username + '}'
                msg += "]"

                response = Response(msg,status.HTTP_200_OK)
            else:
                msg = "Usuario invalido!"
                response = Response({"msg":msg})
        except Exception as e:
            print e
            msg = "Usuario invalido!"
            response = Response({"msg":msg + str(e)})

        return response

class UserRegistrationView(views.APIView):

    def post(self,request, *args, **kw):
        # Process any get params that you may need
        # If you don't need to process get params,
        # you can skip this part
        #get_arg1 = request.GET.get('arg1', None)
        #get_arg2 = request.GET.get('arg2', None)

        # Any URL parameters get passed in **kw
        #myClass = CalcClass(get_arg1, get_arg2, *args, **kw)
        user = request.DATA.get('username',None)
        e = request.DATA.get('email',None)
        password = request.DATA.get('password',None)
        escolaridade = request.DATA.get('schooling',None)
        sexo = request.DATA.get('gender',None)
        idade = request.DATA.get('age',None)
        nome = request.DATA.get('name',None)
        type = "H"

        jogador = Player(username = user, email = e, password = password,
                                   schooling = escolaridade,
                                   gender = sexo,
                                   age = idade,
                                   name = nome,
                                   type = type)
        jogador.save()

        if jogador:
           # share_url(email, url)
            return Response({"success": True})
        else:
            return Response({"success": False})

class StartExperimentView(views.APIView):

    def get(self,request, *args, **kw):

        #numPlayes = request.DATA.get('num_players', None)
        #numLevels = request.DATA.get('num_levels',None)

        succeed,id = False,-1

        #if numLevels and numPlayes:

        service = Game().get_instance()

            #succeed = service.start_experiment(numPlayes,numLevels)
        succeed,id = service.start_experiment()
        return Response({"success": succeed,"experiment_id":id})

class SendResultView(views.APIView):

    def post(self,request, *args, **kw):

        username = request.DATA.get('username', None)
        result = request.DATA.get('result',None)

        succeed = False

        if username and result:

            service = Game().get_instance()

            succeed = service.setResult(username,result)

        return Response({"success": succeed})


class ReadyToPlayFakeView(views.APIView):

    def get(self, request, *args, **kw):
        # Process any get params that you may need
        # If you don't need to process get params,
        # you can skip this part
        #get_arg1 = request.GET.get('arg1', None)
        #get_arg2 = request.GET.get('arg2', None)

        # Any URL parameters get passed in **kw
        #myClass = CalcClass(get_arg1, get_arg2, *args, **kw)

        game = Game().get_instance()
        isReady = game.fake()

        #response = Response(isReady,status.HTTP_200_OK)
        return Response({"levelReadyToPlay:":isReady},status.HTTP_200_OK)

class GetRankView(views.APIView):

    def get(self, request, *args, **kw):
        # Process any get params that you may need
        # If you don't need to process get params,
        # you can skip this part
        #get_arg1 = request.GET.get('arg1', None)
        #get_arg2 = request.GET.get('arg2', None)

        # Any URL parameters get passed in **kw
        #myClass = CalcClass(get_arg1, get_arg2, *args, **kw)

        game = Game().get_instance()
        r = game.getRank()

        #response = Response(isReady,status.HTTP_200_OK)
        return Response({"rank:":r},status.HTTP_200_OK)