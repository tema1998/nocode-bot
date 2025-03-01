# from bot_service.core.configs import config
# from bot_service.models.document import Document
# from bot_service.repositories.async_pg_repository import PostgresAsyncRepository
# from bot_service.schemas.document import DocumentIn
#
#
# class DocumentService:
#     def __init__(self, db: PostgresAsyncRepository):
#         self.db = db
#
#     async def run(self, document_data: DocumentIn) -> Document:
#         """
#         Run bot
#         """
#
#         pass
#
#
# def get_document_service() -> DocumentService:
#     return DocumentService(db=PostgresAsyncRepository(dsn=config.dsn))
