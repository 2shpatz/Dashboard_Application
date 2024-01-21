FROM python:3.8
ENV TOOLS_DIR ${HOME}/projects/tools
ENV LAB_DIR ${HOME}/projects/lab
ENV PATH $PATH:$LAB_DIR:$TOOLS_DIR:/
ENV DASHBOARD_APPS_DIR /dashboard_apps
RUN mkdir -p ${DASHBOARD_APPS_DIR}
EXPOSE 8050
WORKDIR /
COPY /utils ${DASHBOARD_APPS_DIR}/utils
RUN pip3 install -r ${DASHBOARD_APPS_DIR}/utils/requirements.txt
COPY . ${DASHBOARD_APPS_DIR}

ENTRYPOINT python3 ${DASHBOARD_APPS_DIR}/card_select/index.py
