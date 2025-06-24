"""
Gunicorn configuration for production deployment.
"""
import os
from pathlib import Path

# Server socket
bind = "127.0.0.1:5001"
backlog = 2048

# Worker processes
workers = int(os.getenv('MAX_WORKERS', 4))
worker_class = "gevent"
worker_connections = 1000
max_requests = int(os.getenv('MAX_REQUESTS', 10000))
max_requests_jitter = 1000
preload_app = True
timeout = int(os.getenv('WORKER_TIMEOUT', 120))
keepalive = 2

# Restart workers automatically
max_worker_memory = 200  # MB
worker_tmp_dir = "/dev/shm"  # Use shared memory for better performance

# Logging
log_dir = Path("/var/log/edevlet")
log_dir.mkdir(parents=True, exist_ok=True)

accesslog = str(log_dir / "gunicorn_access.log")
errorlog = str(log_dir / "gunicorn_error.log")
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'edevlet-automation'

# Security
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190

# SSL (if terminating SSL at application level - not recommended for production)
# In production, SSL should be terminated at nginx level
# keyfile = os.getenv('SSL_KEY_PATH')
# certfile = os.getenv('SSL_CERT_PATH')

# Development settings (disable in production)
reload = False
check_config = True

# Hooks for application lifecycle
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("🚀 Starting E-Devlet Automation Server")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("🔄 Reloading E-Devlet Automation Server")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info(f"📥 Worker {worker.pid} interrupted")

def post_worker_init(worker):
    """Called just after a worker has been forked."""
    worker.log.info(f"👷 Worker {worker.pid} initialized")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info(f"🍴 Forking worker {worker.pid}")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info(f"✅ Server ready. Listening on {bind}")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.info(f"💥 Worker {worker.pid} aborted")

# Production tuning
forwarded_allow_ips = "*"  # Trust all IPs since we're behind nginx
proxy_allow_ips = "*"
proxy_protocol = False 