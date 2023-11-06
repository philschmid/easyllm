# COPIED and ADAPTED from https://github.com/andrewjroth/requests-auth-aws-sigv4/blob/master/requests_auth_aws_sigv4/__init__.py

import hashlib
import hmac
import os
import urllib.parse
from datetime import datetime
from typing import Optional

from requests import __version__ as requests_version
from requests.auth import AuthBase
from requests.compat import urlparse
from requests.models import PreparedRequest

try:
    import boto3
    from botocore.config import Config
except ImportError:
    boto3 = None

from easyllm.utils.logging import setup_logger

logger = setup_logger()

# aws sigv4 version
__version__ = "0.8"


def sign_msg(key, msg):
    """Sign message using key"""
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


class AWSSigV4(AuthBase):
    def __init__(self, service, **kwargs):
        """Create authentication mechanism

        :param service: AWS Service identifier, for example `ec2`.  This is required.
        :param region:  AWS Region, for example `us-east-1`.  If not provided, it will be set using
            the environment variables `AWS_DEFAULT_REGION` or using boto3, if available.
        :param session: If boto3 is available, will attempt to get credentials using boto3,
            unless passed explicitly.  If using boto3, the provided session will be used or a new
            session will be created.

        """
        # Set Service
        self.service = service

        # First, get credentials passed explicitly
        self.aws_access_key_id = kwargs.get("aws_access_key_id")
        self.aws_secret_access_key = kwargs.get("aws_secret_access_key")
        self.aws_session_token = kwargs.get("aws_session_token")
        # Next, try environment variables or use boto3
        if self.aws_access_key_id is None or self.aws_secret_access_key is None:
            if boto3 is not None:
                # Setup Session
                if "session" in kwargs:
                    if type(kwargs["session"]) == boto3.Session:
                        session = kwargs["session"]
                    else:
                        raise ValueError("Session must be boto3.Session, {} invalid, ".format(type(kwargs["session"])))
                else:
                    session = boto3.Session()
                logger.debug("Using boto3 session: %s", session)
                cred = session.get_credentials()
                if cred is None:
                    raise ValueError(
                        "No credentials found in boto3 session, please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables or configure boto3 session"
                    )
                logger.debug("Got credential from boto3 session")
                self.aws_access_key_id = cred.access_key
                self.aws_secret_access_key = cred.secret_key
                self.aws_session_token = cred.token
                self.region = session.region_name
                logger.debug("Got region from boto3 session")
            else:
                logger.debug("Checking environment for credentials")
                self.aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
                self.aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
                self.aws_session_token = os.environ.get("AWS_SESSION_TOKEN") or os.environ.get("AWS_SECURITY_TOKEN")
        # Last, fail if still not found
        if self.aws_access_key_id is None or self.aws_secret_access_key is None:
            raise KeyError(
                "AWS Access Key ID and Secret Access Key are required, please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables"
            )

        # Get Region passed explicitly
        self.region = kwargs.get("region")
        # Next, try environment variables or use boto3
        if self.region is None:
            logger.debug("Checking environment for region")
            self.region = os.environ.get("AWS_DEFAULT_REGION") or os.environ.get("AWS_REGION")
        # Last, fail if not found
        if self.region is None:
            raise KeyError("Region is required, please set AWS_DEFAULT_REGION or AWS_REGION environment variable")

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        """Called to add authentication information to request

        :param r: `requests.models.PreparedRequest` object to modify

        :returns: `requests.models.PreparedRequest`, modified to add authentication

        """
        # Create a date for headers and the credential string
        t = datetime.utcnow()
        self.amzdate = t.strftime("%Y%m%dT%H%M%SZ")
        self.datestamp = t.strftime("%Y%m%d")
        logger.debug("Starting authentication with amzdate=%s", self.amzdate)

        # Parse request to get URL parts
        url_parts = urlparse(r.url)
        logger.debug("Request URL: %s", url_parts)
        host = url_parts.hostname
        if self.service == "s3":
            uri = url_parts.path
        else:
            uri_segments = []
            for segment in url_parts.path.split("/"):
                uri_segments.append(urllib.parse.quote(segment, safe=""))
            uri = "/".join(uri_segments)
        if len(url_parts.query) > 0:
            qs = dict(map(lambda i: i.split("="), url_parts.query.split("&")))
        else:
            qs = {}

        # Setup Headers
        # r.headers is type `requests.structures.CaseInsensitiveDict`
        if "Host" not in r.headers:
            r.headers["Host"] = host
        if "Content-Type" not in r.headers:
            r.headers["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8; application/json"
        if "User-Agent" not in r.headers:
            r.headers["User-Agent"] = "python-requests/{} auth-aws-sigv4/{}".format(requests_version, __version__)
        r.headers["X-AMZ-Date"] = self.amzdate
        if self.aws_session_token is not None:
            r.headers["x-amz-security-token"] = self.aws_session_token

        # Task 1: Create Canonical Request
        # Ref: http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html
        # Query string values must be URL-encoded (space=%20) and be sorted by name.
        canonical_querystring = "&".join(("=".join(p) for p in sorted(qs.items())))

        # Create payload hash (hash of the request body content).
        if r.method == "GET" and not r.body:
            payload_hash = hashlib.sha256("".encode("utf-8")).hexdigest()
        else:
            if r.body:
                if isinstance(r.body, bytes):
                    logger.debug("Request Body: <bytes> %s", r.body)
                    payload_hash = hashlib.sha256(r.body).hexdigest()
                else:
                    logger.debug("Request Body: <str> %s", r.body)
                    payload_hash = hashlib.sha256(r.body.encode("utf-8")).hexdigest()
            else:
                logger.debug("Request Body is empty")
                payload_hash = hashlib.sha256(b"").hexdigest()
        r.headers["x-amz-content-sha256"] = payload_hash

        # Create the canonical headers and signed headers. Header names
        # must be trimmed and lowercase, and sorted in code point order from
        # low to high. Note that there is a trailing \n.
        headers_to_sign = sorted(
            filter(lambda h: h.startswith("x-amz-") or h == "host", (h_key.lower() for h_key in r.headers.keys()))
        )
        canonical_headers = "".join((":".join((h, r.headers[h])) + "\n" for h in headers_to_sign))
        signed_headers = ";".join(headers_to_sign)

        # Combine elements to create canonical request
        canonical_request = "\n".join(
            [r.method, uri, canonical_querystring, canonical_headers, signed_headers, payload_hash]
        )
        logger.debug("Canonical Request: '%s'", canonical_request)

        # Task 2: Create string to sign
        credential_scope = "/".join([self.datestamp, self.region, self.service, "aws4_request"])
        string_to_sign = "\n".join(
            [
                "AWS4-HMAC-SHA256",
                self.amzdate,
                credential_scope,
                hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
            ]
        )
        logger.debug("String-to-Sign: '%s'", string_to_sign)

        # Task 3: Calculate Signature
        k_date = sign_msg(("AWS4" + self.aws_secret_access_key).encode("utf-8"), self.datestamp)
        k_region = sign_msg(k_date, self.region)
        k_service = sign_msg(k_region, self.service)
        k_signing = sign_msg(k_service, "aws4_request")
        signature = hmac.new(k_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
        logger.debug("Signature: %s", signature)

        # Task 4: Add signing information to request
        r.headers["Authorization"] = "AWS4-HMAC-SHA256 Credential={}/{}, SignedHeaders={}, Signature={}".format(
            self.aws_access_key_id, credential_scope, signed_headers, signature
        )
        logger.debug(
            "Returning Request: <PreparedRequest method=%s, url=%s, headers=%s, SignedHeaders=%s, Signature=%s",
            r.method,
            r.url,
            r.headers,
            signed_headers,
            signature,
        )
        return r


def get_bedrock_client(
    assumed_role: Optional[str] = None,
    region: Optional[str] = None,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    runtime: Optional[bool] = True,
):
    """Create a boto3 client for Amazon Bedrock, with optional configuration overrides

    Parameters
    ----------
    assumed_role :
        Optional ARN of an AWS IAM role to assume for calling the Bedrock service. If not
        specified, the current active credentials will be used.
    region :
        Optional name of the AWS Region in which the service should be called (e.g. "us-east-1").
        If not specified, AWS_REGION or AWS_DEFAULT_REGION environment variable will be used.
    runtime :
        Optional choice of getting different client to perform operations with the Amazon Bedrock service.
    """
    if region is None:
        target_region = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION"))
    else:
        target_region = region

    session_kwargs = {"region_name": target_region}
    client_kwargs = {**session_kwargs}

    profile_name = os.environ.get("AWS_PROFILE")
    if profile_name:
        session_kwargs["profile_name"] = profile_name

    retry_config = Config(
        region_name=target_region,
        retries={
            "max_attempts": 10,
            "mode": "standard",
        },
    )
    session = boto3.Session(**session_kwargs)

    if assumed_role:
        logger.info(f"  Using role: {assumed_role}", end="")
        sts = session.client("sts")
        response = sts.assume_role(RoleArn=str(assumed_role), RoleSessionName="llm-bedrock")
        logger.info(" ... successful!")
        client_kwargs["aws_access_key_id"] = response["Credentials"]["AccessKeyId"]
        client_kwargs["aws_secret_access_key"] = response["Credentials"]["SecretAccessKey"]
        client_kwargs["aws_session_token"] = response["Credentials"]["SessionToken"]
    else:
        client_kwargs["aws_access_key_id"] = aws_access_key_id
        client_kwargs["aws_secret_access_key"] = aws_secret_access_key
        client_kwargs["aws_session_token"] = aws_session_token

    if runtime:
        service_name = "bedrock-runtime"
    else:
        service_name = "bedrock"

    bedrock_client = session.client(service_name=service_name, config=retry_config, **client_kwargs)

    logger.info("boto3 Bedrock client successfully created!")
    return bedrock_client
