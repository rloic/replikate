from typing import Union


class ServerParameters:
    def __init__(
            self,
            host: str,
            port: int,
            authentication: Union[str, None]
    ):
        self.host = host
        self.port = port
        if authentication not in [None, 'STARTTLS', 'SSL/TLS']:
            raise ValueError('Invalid authentication mode {}'.format(authentication))
        self.authentication = authentication