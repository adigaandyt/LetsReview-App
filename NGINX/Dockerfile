#passing the conf file was causing issues so let's just build the nginx
FROM nginx:1.24-alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY ./conf.d/default.conf /etc/nginx/conf.d/default.conf