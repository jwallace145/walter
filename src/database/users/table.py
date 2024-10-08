from dataclasses import dataclass
from typing import List

from src.database.users.models import User
from src.utils.log import Logger
from src.environment import Domain
from src.aws.dynamodb.client import WalterDDBClient

log = Logger(__name__).get_logger()


@dataclass
class UsersTable:
    """
    Users Table
    """

    TABLE_NAME_FORMAT = "Users-{domain}"

    ddb: WalterDDBClient
    domain: Domain

    table: str = None  # set during post init

    def __post_init__(self) -> None:
        self.table = UsersTable._get_table_name(self.domain)
        log.debug(f"Creating UsersTable DDB client with table name '{self.table}'")

    def get_user(self, email: str) -> User:
        log.info(f"Getting user with email '{email}' from table '{self.table}'")
        key = UsersTable._get_user_key(email)
        item = self.ddb.get_item(self.table, key)
        return UsersTable._get_user_from_ddb_item(item)

    def get_users(self) -> List[User]:
        log.info(f"Getting users from table '{self.table}'")
        users = []
        for item in self.ddb.scan_table(self.table):
            users.append(UsersTable._get_user_from_ddb_item(item))
        return users

    @staticmethod
    def _get_table_name(domain: Domain) -> str:
        return UsersTable.TABLE_NAME_FORMAT.format(domain=domain.value)

    @staticmethod
    def _get_user_key(email: str) -> dict:
        return {"email": {"S": email}}

    @staticmethod
    def _get_user_from_ddb_item(item: dict) -> User:
        return User(email=item["email"]["S"], username=item["username"]["S"])
