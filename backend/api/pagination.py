from rest_framework.pagination import PageNumberPagination

from .constants import PAGE_SIZE


class ReceiptPagination(PageNumberPagination):
    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
