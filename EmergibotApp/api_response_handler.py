from rest_framework.response import Response
from rest_framework import status

CODES = {
    'HTTP_200_OK': 'HTTP_200_OK',
    'HTTP_400_BAD_REQUEST': 'HTTP_400_BAD_REQUEST',
    'HTTP_401_UNAUTHORIZED': 'HTTP_401_UNAUTHORIZED',
    'HTTP_403_FORBIDDEN': 'HTTP_403_FORBIDDEN',
    'HTTP_404_NOT_FOUND': 'HTTP_404_NOT_FOUND',
    'HTTP_405_METHOD_NOT_ALLOWED': 'HTTP_405_METHOD_NOT_ALLOWED',
    'HTTP_500_INTERNAL_SERVER_ERROR': 'HTTP_500_INTERNAL_SERVER_ERROR'
}

class APIResponseHandler:

    @classmethod
    def HTTP_200_OK(cls, data, message="OK"):
        return Response(
            {
                'status': 200,
                'status_code': CODES['HTTP_200_OK'],
                'message': message,
                'data': data
            },
            status=status.HTTP_200_OK
        )

    @classmethod
    def HTTP_400_BAD_REQUEST(cls, errors=None, message="Bad Request"):
        return Response(
            {
                'status': 400,
                'status_code': CODES['HTTP_400_BAD_REQUEST'],
                'message': message,
                'errors': errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @classmethod
    def HTTP_401_UNAUTHORIZED(cls, message="Unauthorized"):
        return Response(
            {
                'status': 401,
                'status_code': CODES['HTTP_401_UNAUTHORIZED'],
                'message': message
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    @classmethod
    def HTTP_403_FORBIDDEN(cls, message="Forbidden"):
        return Response(
            {
                'status': 403,
                'status_code': CODES['HTTP_403_FORBIDDEN'],
                'message': message
            },
            status=status.HTTP_403_FORBIDDEN
        )

    @classmethod
    def HTTP_404_NOT_FOUND(cls, message="Not Found"):
        return Response(
            {
                'status': 404,
                'status_code': CODES['HTTP_404_NOT_FOUND'],
                'message': message
            },
            status=status.HTTP_404_NOT_FOUND
        )

    @classmethod
    def HTTP_405_METHOD_NOT_ALLOWED(cls, message="Method Not Allowed"):
        return Response(
            {
                'status': 405,
                'status_code': CODES['HTTP_405_METHOD_NOT_ALLOWED'],
                'message': message
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @classmethod
    def HTTP_500_INTERNAL_SERVER_ERROR(cls, errors=None, message="Internal Server Error"):
        return Response(
            {
                'status': 500,
                'status_code': CODES['HTTP_500_INTERNAL_SERVER_ERROR'],
                'message': message,
                'errors': errors
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


