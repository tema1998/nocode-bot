import logging

from elasticsearch import AsyncElasticsearch


async def create_index_if_doesnt_exist(
    client: AsyncElasticsearch, index_name: str, index: dict
) -> None:

    if not await client.indices.exists(index=index_name):
        response = await client.indices.create(index=index_name, **index)
        if response.get("acknowledged"):
            logging.info(f"Index {index_name} was created successfully.")
        else:
            logging.error("Error of creating index.")
