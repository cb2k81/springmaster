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
  error:
    include-exception: false
    include-message: never
    include-stacktrace: never
    include-binding-errors: never

management:
  endpoint:
    health:
      show-details: never
      show-components: never
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
  pattern:
    level: "%5p [correlationId:%X{correlationId:-}]"
  level:
    root: ${LOG_LEVEL:INFO}
