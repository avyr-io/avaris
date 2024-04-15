import os
from datetime import datetime
from logging import Logger
from typing import List, Optional
from sqlalchemy import and_

from sqlalchemy import update  # Ensure this is imported
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from avaris.api.models import ExecutionResult
from avaris.data.datamanager import DataManager
from avaris.data.models import Base, SQLExecutionResult


class SQLDataManager(DataManager):

    def __init__(self, logger: Optional[Logger] = None, database_url: str = None):
        super().__init__(logger)
        self.database_url = database_url
        self.engine = create_async_engine(self.database_url, echo=False)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            class_=AsyncSession,
        )

    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            self.logger.info("SQL Database initialized")

    async def get_slice_sql(
        self, from_time: datetime, to_time: datetime
    ) -> List[SQLExecutionResult]:
        """
        Fetches task results that were recorded within the specified time range.

        Args:
            from_time (datetime): The start of the time range.
            to_time (datetime): The end of the time range.

        Returns:
            List[SQLExecutionResult]: A list of SQLExecutionResult objects within the time range.
        """
        async with self.SessionLocal() as session:
            try:
                # Adjust the query to filter results based on the timestamp field
                query = select(SQLExecutionResult).filter(
                    SQLExecutionResult.timestamp >= from_time,
                    SQLExecutionResult.timestamp <= to_time,
                )
                result = await session.execute(query)
                return result
            except SQLAlchemyError as e:
                self.logger.error(
                    f"Failed to retrieve task results within time range from the SQL database: {e}"
                )
                return []

    async def get_slice(
        self, from_time: datetime, to_time: datetime
    ) -> List[ExecutionResult]:
        """
        Fetches task results that were recorded within the specified time range
        and converts them to ExecutionResult objects.

        Args:
            from_time (datetime): The start of the time range.
            to_time (datetime): The end of the time range.

        Returns:
            List[ExecutionResult]: A list of ExecutionResult objects within the time range.
        """
        sql_results = await self.get_slice_sql(from_time, to_time)
        execution_results = [
            ExecutionResult(
                name=result.name,
                task=result.task,
                id=result.id,
                timestamp=result.timestamp,
                result=result.result,
            )
            for result in sql_results
        ]
        return execution_results


    async def add_task_result(self, execution_result: ExecutionResult) -> bool:
        async with self.SessionLocal() as session:
            try:
                db_task_result = SQLExecutionResult(
                    id=execution_result.id,
                    name=execution_result.name,
                    task=execution_result.task,
                    result=execution_result.result,
                    timestamp=execution_result.timestamp,
                )
                session.add(db_task_result)
                await session.commit()
                self.logger.info(
                    f"Task result for {execution_result.task} added to the SQL database"
                )
                return True
            except IntegrityError:
                await session.rollback()  # Roll back the failed transaction
                self.logger.info(
                    f"Found existing {execution_result.task}[{execution_result.id}], updating record."
                )
                try:
                    # Update the existing record
                    await session.execute(
                        update(SQLExecutionResult)
                        .where(SQLExecutionResult.id == execution_result.id)
                        .values(
                            name=execution_result.name,
                            task=execution_result.task,
                            result=execution_result.result,
                            timestamp=execution_result.timestamp,
                        )
                    )
                    await session.commit()
                    return True
                except SQLAlchemyError as e:
                    self.logger.error(
                        f"Failed to update task result for {execution_result.task} in the SQL database: {e}"
                    )
                    await session.rollback()  # Ensure to roll back on update failure
                    return False
            except SQLAlchemyError as e:
                self.logger.error(
                    f"Failed to add task result for {execution_result.task} in the SQL database: {e}"
                )
                await session.rollback()  # Ensure to roll back on other SQL errors
                return False


    async def get_filtered_tasks(self, **kwargs):
        async with self.SessionLocal() as session:
            query = select(SQLExecutionResult)

            conditions = []
            for key, value in kwargs.items():
                if hasattr(SQLExecutionResult, key):
                    if value is not None:
                        if isinstance(value, list):
                            if value:  # Only add if list is not empty
                                condition = getattr(SQLExecutionResult,
                                                    key).in_(value)
                                conditions.append(condition)
                        else:
                            # Normal condition for non-list type with a non-None value
                            condition = getattr(SQLExecutionResult, key) == value
                            conditions.append(condition)

                    # Special handling for date ranges
                    if key == "start_date" and value is not None:
                        condition = SQLExecutionResult.timestamp >= value
                        conditions.append(condition)
                    elif key == "end_date" and value is not None:
                        condition = SQLExecutionResult.timestamp <= value
                        conditions.append(condition)

            # Apply filters if any conditions are created
            if conditions:
                query = query.filter(and_(*conditions))

            results = await session.execute(query)
            return results.scalars().all()



    async def get_task_result(self, job_id: str):
        try:
            async with self.SessionLocal() as session:
                query = select(SQLExecutionResult).filter(
                    SQLExecutionResult.id == job_id
                )
                result = await session.execute(query)
                task_result = result.scalars().first()
                return task_result.result if task_result else None
        except SQLAlchemyError as e:
            self.logger.error(
                f"Failed to retrieve task result for {job_id} from the SQL database: {e}"
            )

    async def get_all_tasks(self):
        try:
            async with self.SessionLocal() as session:
                result = await session.execute(select(SQLExecutionResult))
                return result.scalars().all()
        except SQLAlchemyError as e:
            self.logger.error(
                f"Failed to retrieve all tasks from the SQL database: {e}"
            )
            return []

    async def get_all_task_names(self) -> List[str]:
        """
        Fetches a list of unique task names from the database.

        Returns:
            List[str]: A list of unique task names.
        """
        async with self.SessionLocal() as session:
            try:
                query = select(SQLExecutionResult.task.distinct())
                result = await session.execute(query)
                task_names = [row[0] for row in result.fetchall()]
                return task_names
            except SQLAlchemyError as e:
                self.logger.error(
                    f"Failed to retrieve task names from the SQL database: {e}"
                )
                return []
