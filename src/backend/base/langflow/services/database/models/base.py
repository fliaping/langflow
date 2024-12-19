import os

import orjson
from sqlalchemy.ext.declarative import declared_attr, has_inherited_table
from sqlmodel import SQLModel


def orjson_dumps(v, *, default=None, sort_keys=False, indent_2=True):
    option = orjson.OPT_SORT_KEYS if sort_keys else None
    if indent_2:
        # orjson.dumps returns bytes, to match standard json.dumps we need to decode
        # option
        # To modify how data is serialized, specify option. Each option is an integer constant in orjson.
        # To specify multiple options, mask them together, e.g., option=orjson.OPT_STRICT_INTEGER | orjson.OPT_NAIVE_UTC
        if option is None:
            option = orjson.OPT_INDENT_2
        else:
            option |= orjson.OPT_INDENT_2
    if default is None:
        return orjson.dumps(v, option=option).decode()
    return orjson.dumps(v, default=default, option=option).decode()

def get_table_name_with_prefix(table_name: str) -> str:
    prefix = os.getenv('LANGFLOW_DATABASE_TABLE_PREFIX', '')
    return f"{prefix}{table_name}"


class TablePrefixBase(SQLModel):
    """带表名前缀的 SQLModel 基类，前缀从环境变量获取"""
    
    @declared_attr
    def __tablename__(cls) -> str:
        """
        动态生成表名，自动添加前缀
        支持显式定义的表名和自动生成的表名
        """
        # 如果是继承的表，不生成新表名
        if has_inherited_table(cls):
            return None
        
        # 如果没有显式定义，使用类名作为基础表名
        base_tablename = cls.__name__.lower()
        # 检查是否有显式定义的表名
        if hasattr(cls, '_sa_class_manager'):
            for key, value in cls._sa_class_manager.local_attrs.items():
                if key == '__tablename__':
                    base_tablename = value.value
        
        
        return get_table_name_with_prefix(base_tablename)
    