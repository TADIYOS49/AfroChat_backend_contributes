from typing import (
    Optional,
    Callable,
    Sequence,
    Any,
    Type,
)

from sqlalchemy import Select, UnaryExpression, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.routers.api_v1.Service.schemas import Paginate, Meta, T

ItemsTransformer = Callable[[Sequence[Any]], Sequence[Any]]


async def paginate_response(
    statement: Select,
    db_session: AsyncSession,
    model: Type[T],
    offset: int,
    limit: int,
    sorting_attribute: UnaryExpression[Any] | None = None,
    transformer: Optional[ItemsTransformer] = None,
    to_orm: Optional[bool] = False,
) -> Paginate[T]:
    """
    Paginate and transform the response based on specified criteria.

    This function takes a SQL statement, a database session, a model type, and pagination criteria to retrieve and transform data into a paginated response.

    :param statement: The SQL statement used to query the database.
    :type statement: Select

    :param db_session: An AsyncSession object representing a database session.
    :type db_session: AsyncSession

    :param model: The data model (Type) for the response.
    :type model: Type[T]

    :param offset: The starting index for pagination.
    :type offset: int

    :param limit: The maximum number of items to return.
    :type limit: int

    :param transformer: (Optional) A function to transform the retrieved data.
    :type transformer: Optional[ItemsTransformer]

    :param to_orm: (Optional) A boolean indicating whether the data should be converted to ORM objects.
    :type to_orm: Optional[bool]

    :return: A Paginate object containing paginated data and metadata.
    :rtype: Paginate[T]
    """
    # Get the total count
    count_statement = Select(func.count()).select_from(statement.subquery())
    total_count = await db_session.execute(count_statement)
    total_count = total_count.scalar()

    # Fetch the items
    if sorting_attribute is not None:
        statement = statement.order_by(sorting_attribute)
    items = await db_session.execute(statement.offset(offset).limit(limit))

    if to_orm:
        items = items.scalars().all()
    else:
        items = items.fetchall()

    # Perform transformation if a transformer function is provided
    if transformer:
        items = transformer(items)

    meta_data: dict[str, int] = {
        "offset": offset,
        "limit": limit,
        "total": total_count,
        "returned": len(items),
    }

    # Create a Paginate object with metadata and paginated data
    response = Paginate[model](meta_data=Meta(**meta_data), data=items)

    return response
