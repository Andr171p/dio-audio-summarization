class OAuthError(Exception):
    pass


class AuthenticationFailedError(OAuthError):
    pass


class SaluteSpeechError(Exception):
    pass


class UploadingFileError(SaluteSpeechError):
    pass


class DownloadingFileError(SaluteSpeechError):
    pass


class TaskFailedError(SaluteSpeechError):
    pass
