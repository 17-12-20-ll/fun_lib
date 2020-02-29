from django.utils.deprecation import MiddlewareMixin

from utils.manage_resp import resp
from utils.manage_token import check_token


class IsTokenMiddleWare(MiddlewareMixin):
    """添加阅读量"""

    def process_request(self, request):
        need_token = ['/user/get_admins/', '/user/update_admin/', '/user/update_profile/', '/user/update_pwd/']
        if request.path in need_token:
            # 判断需要token的路由，如果没有token，则不通过
            token = request.META.get('HTTP_AUTHENTICATION')
            if (not token) or token == 'null':
                return resp(400, '没有token')
            if not check_token(token):
                return resp(401, 'token过期')
