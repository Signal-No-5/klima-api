import logging
from datetime import datetime

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core import db_manager
from app.models.admin import AuditLog


# A simple placeholder function for writing the log
# In a real app, this would save to a database or a log file.
def log_audit_entry(log_data: dict):
    # This example just prints a summary
    print(
        f"AUDIT LOG: UserID: {log_data.get('user_id', 'N/A')} | \
        Method: {log_data['method']} | Path: {log_data['path']} | \
        Status: {log_data['status_code']} | Time: {log_data['duration']:.4f}s"
    )
    # print(json.dumps(log_data, indent=2)) # To see all details


class AuditMiddleware(BaseHTTPMiddleware):
    logger: logging.Logger = logging.getLogger("app.audit")

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Logs actions done in server

        Args:
            request (Request): The request done by API Clients
            call_next (RequestResponseEndpoint): Endpoint to be called after

        Returns:
            Response: The actual response from the endpoint
        """
        # Step 1. Get the start time of the action.
        start_time = datetime.now()

        # Step 2. do the action done
        try:
            response = await call_next(request)
        except Exception as e:
            response = Response("Internal Server Error: {}".format(e), status_code=500)
            # log_error(e)

        # Step 3. Get time elapsed and post-request data
        duration = (datetime.now() - start_time).total_seconds()
        audit_entry = AuditLog(
            method=request.method,
            path=request.url.path,
            host=request.client.host if request.client else "N/A",
            status_code=response.status_code,
            duration=duration,
        )
        async with db_manager.get_db() as sessions:
            for dialect, session in sessions.items():
                try:
                    session.add(audit_entry)
                    session.commit()
                    session.refresh(audit_entry)
                except Exception as e:
                    self.logger.error("Errors adding entry to %s: %s", dialect, e)

        return response
