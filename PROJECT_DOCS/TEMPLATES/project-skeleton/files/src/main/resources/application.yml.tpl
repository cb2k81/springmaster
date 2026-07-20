spring:
  application:
    name: __PROJECT_NAME__
  profiles:
    default: ${APP_PROFILE:dev}

server:
  port: ${APP_PORT:__HTTP_PORT__}

management:
  endpoints:
    web:
      exposure:
        include: health,info

springdoc:
  api-docs:
    path: ${APP_OPENAPI_PATH:/api-docs}
  swagger-ui:
    path: /swagger-ui.html

logging:
  level:
    root: ${LOG_LEVEL:INFO}
