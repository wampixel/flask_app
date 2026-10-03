from pydantic import BaseModel, ConfigDict

from .pagination import Paginated


class UserData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    last_name: str
    username: str


UsersPage = Paginated[UserData]
