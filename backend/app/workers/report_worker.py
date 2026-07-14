import time
import logging
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def generate_monthly_report(self, department_id: str):
    """
    Background job to generate heavy PDF/Excel reports.
    """
    logger.info(f"Generating monthly report for department {department_id}...")
    # Simulate PDF generation and file storage upload
    time.sleep(5)
    report_url = f"https://aegon.storage.example.com/reports/{department_id}_monthly.pdf"
    logger.info(f"Report generated successfully: {report_url}")
    return report_url
