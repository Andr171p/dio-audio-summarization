from modules.iam.domain import UserCredentials
from modules.iam.domain.entities import AnonymousUser

print(
    AnonymousUser.register_by_credentials(
        UserCredentials(username="user", email="andrey.kosov.05@inbox.ru", password="12345")
    )
)