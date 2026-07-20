spring:
  application:
    name: __PROJECT_NAME__
  profiles:
    default: ${APP_PROFILE:dev}
  liquibase:
    enabled: ${APP_LIQUIBASE_ENABLED:false}
    change-log: classpath:db/changelog/db.changelog-master.xml

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
