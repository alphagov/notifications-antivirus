from app import NotifyCelery

notify_celery = NotifyCelery()
notify_celery.send_task(name="scan_file", args=("filename",), queue="virus_scan")
