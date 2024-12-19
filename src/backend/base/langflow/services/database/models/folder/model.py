from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Text, UniqueConstraint
from sqlmodel import Column, Field, Relationship, SQLModel

from langflow.services.database.models.base import (TablePrefixBase,
                                                    get_table_name_with_prefix)
from langflow.services.database.models.flow.model import Flow, FlowRead
from langflow.services.database.models.user.model import User


class FolderBase(TablePrefixBase):
    name: str = Field(index=True)
    description: str | None = Field(default=None, sa_column=Column(Text))


class Folder(FolderBase, table=True):  # type: ignore[call-arg]
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    parent_id: UUID | None = Field(default=None, foreign_key=f"{get_table_name_with_prefix('folder')}.id")

    parent: Optional["Folder"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Folder.id"},
    )
    children: list["Folder"] = Relationship(back_populates="parent")
    user_id: UUID | None = Field(default=None, foreign_key=f"{get_table_name_with_prefix('user')}.id")
    user: User = Relationship(back_populates="folders", sa_relationship_kwargs={
        "primaryjoin": "Folder.user_id == User.id"
    })
    flows: list[Flow] = Relationship(
        back_populates="folder", sa_relationship_kwargs={"cascade": "all, delete, delete-orphan"}
    )

    __table_args__ = (UniqueConstraint("user_id", "name", name="unique_folder_name"),)


class FolderCreate(FolderBase):
    components_list: list[UUID] | None = None
    flows_list: list[UUID] | None = None


class FolderRead(FolderBase):
    id: UUID
    parent_id: UUID | None = Field()


class FolderReadWithFlows(FolderBase):
    id: UUID
    parent_id: UUID | None = Field()
    flows: list[FlowRead] = Field(default=[])


class FolderUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    parent_id: UUID | None = None
    components: list[UUID] = Field(default_factory=list)
    flows: list[UUID] = Field(default_factory=list)
