FROM ubuntu:20.04

WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3.8=3.8.5-1~20.04\
      python3-pip=20.0.2-5ubuntu1.1 \
      python3-venv=3.8.2-0ubuntu2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN pip3 --no-cache-dir install -r requirements.txt

EXPOSE 5000

#ENTRYPOINT ["python3"]
#CMD ["application/capacity_planner_service.py"]
CMD ["gunicorn" , "-w", "3", "--bind", "0.0.0.0:5000", "application.capacity_planner_service:ai_capacity_planner", "--timeout", "120"]


