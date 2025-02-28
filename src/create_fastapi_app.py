from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import ORJSONResponse
from src.core.configs import config


def register_static_docs_routes(app: FastAPI):
    """Register static documentation routes (Swagger UI and ReDoc) for the FastAPI application.

    Args:
        app (FastAPI): The FastAPI application instance to register routes on.
    """

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        """Serve the Swagger UI documentation HTML page.

        Returns:
            HTML: The HTML content of the Swagger UI page.
        """
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        )

    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)  # type: ignore
    async def swagger_ui_redirect():
        """Redirect for OAuth2 in Swagger UI.

        Returns:
            HTML: Redirect HTML for OAuth2 support in Swagger UI.
        """
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        """Serve the ReDoc documentation HTML page.

        Returns:
            HTML: The HTML content of the ReDoc page.
        """
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=app.title + " - ReDoc",
            redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
        )


def create_app(create_custom_static_urls: bool = False) -> FastAPI:
    """Create and configure a FastAPI application instance.

    Args:
        create_custom_static_urls (bool): Whether to create custom static URLs for docs.
                                            If True, custom routes will be registered.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    app = FastAPI(
        title=config.app_name,
        default_response_class=ORJSONResponse,
        docs_url=None if create_custom_static_urls else "/docs",
        redoc_url=None if create_custom_static_urls else "/redoc",
    )
    if create_custom_static_urls:
        register_static_docs_routes(app)
    return app
