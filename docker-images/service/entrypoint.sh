echo "Starting capacity planner service"

gunicorn --bind 0.0.0.0:5000 --workers=3 application.capacity_planner_service:ai_capacity_planner --timeout=120