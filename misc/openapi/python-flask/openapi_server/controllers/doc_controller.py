__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import connexion
import six

from openapi_server.models.api_response import ApiResponse  # noqa: E501
from openapi_server.models.doc import Doc  # noqa: E501
from openapi_server import util


def get_doc_by_id(doc_id):  # noqa: E501
    """Find Doc by ID

    Returns a single Doc # noqa: E501

    :param doc_id: ID of Doc to return
    :type doc_id: int

    :rtype: Doc
    """
    return 'do some magic!'


def upload_flow_file(limit, file=None):  # noqa: E501
    """index with an flow

    index with an flow yaml file # noqa: E501

    :param limit: limit number of indexing
    :type limit: int
    :param file: file to upload
    :type file: str

    :rtype: ApiResponse
    """
    return 'do some magic!'


def upload_query_file(topk, file=None):  # noqa: E501
    """querydoc with an image

     # noqa: E501

    :param topk: topk numbers  to return
    :type topk: int
    :param file:  image file to upload
    :type file: str

    :rtype: ApiResponse
    """
    return 'do some magic!'
