# CRM Celery Setup Guide

This guide explains how to set up and run Celery with Celery Beat for generating weekly CRM reports.

## Prerequisites

- Python 3.x
- Redis server
- Django project with all dependencies installed

## Installation Steps

### 1. Install Redis

#### On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

#### On macOS:
```bash
brew install redis
brew services start redis
```

#### On Windows:
Download and install Redis from [https://redis.io/download](https://redis.io/download) or use WSL.

### 2. Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

This will install:
- `celery` - Distributed task queue
- `django-celery-beat` - Database-backed periodic task scheduler
- `redis` - Redis Python client

### 3. Run Database Migrations

Apply Django migrations, including Celery Beat migrations:

```bash
python manage.py migrate
```

This will create the necessary database tables for Celery Beat to store scheduled tasks.

### 4. Start Celery Worker

In a separate terminal, start the Celery worker:

```bash
celery -A crm worker -l info
```

The worker will:
- Connect to Redis broker at `redis://localhost:6379/0`
- Process tasks from the queue
- Execute the `generate_crm_report` task when scheduled

### 5. Start Celery Beat

In another separate terminal, start Celery Beat scheduler:

```bash
celery -A crm beat -l info
```

Celery Beat will:
- Schedule the `generate_crm_report` task to run every Monday at 6:00 AM
- Send tasks to the Celery worker for execution

### 6. Verify Setup

#### Check Redis Connection

Test that Redis is running:

```bash
redis-cli ping
```

Should return: `PONG`

#### Check Logs

After the scheduled time (Monday 6:00 AM), check the report log:

```bash
cat /tmp/crm_report_log.txt
```

You should see entries like:
```
2025-02-03 06:00:00 - Report: 10 customers, 25 orders, 15000.50 revenue
```

## Task Details

### generate_crm_report Task

The `generate_crm_report` task:
- Queries the GraphQL endpoint for:
  - Total number of customers
  - Total number of orders
  - Total revenue (sum of all order totalAmount values)
- Logs the report to `/tmp/crm_report_log.txt` with timestamp
- Format: `YYYY-MM-DD HH:MM:SS - Report: X customers, Y orders, Z revenue`

### Schedule

The task runs:
- **Frequency**: Weekly
- **Day**: Monday
- **Time**: 6:00 AM UTC

To modify the schedule, edit `CELERY_BEAT_SCHEDULE` in `alx_backend_graphql_crm/settings.py`.

## Troubleshooting

### Redis Connection Error

If you see connection errors:
1. Verify Redis is running: `redis-cli ping`
2. Check Redis is listening on port 6379: `netstat -an | grep 6379`
3. Verify the broker URL in `crm/celery.py` matches your Redis configuration

### Task Not Executing

1. Ensure both Celery worker and Celery Beat are running
2. Check Celery Beat logs for scheduling information
3. Verify the task is registered: `celery -A crm inspect registered`
4. Check Django migrations are applied: `python manage.py showmigrations django_celery_beat`

### GraphQL Endpoint Error

If the task fails to query GraphQL:
1. Ensure Django development server is running: `python manage.py runserver`
2. Verify GraphQL endpoint is accessible at `http://localhost:8000/graphql`
3. Check the endpoint URL in `crm/tasks.py`

## Production Considerations

For production deployment:
1. Use a process manager like `supervisord` or `systemd` to manage Celery workers
2. Configure Redis persistence and replication
3. Set up monitoring and alerting for failed tasks
4. Use separate Redis databases for different environments
5. Configure proper logging and log rotation
6. Set up task retry policies and error handling

## Additional Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Django Celery Beat Documentation](https://django-celery-beat.readthedocs.io/)
- [Redis Documentation](https://redis.io/documentation)
