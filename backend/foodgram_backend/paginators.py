from rest_framework.pagination import LimitOffsetPagination


class LimitOnlyPagination(LimitOffsetPagination):
    def get_offset(self, request):
        return 0
