spring:
  application:
    name: __PROJECT_NAME__
  liquibase:
    enabled: false
    change-log: classpath:db/changelog/db.changelog-master.xml

server:
  port: __HTTP_PORT__

management:
  endpoints:
    web:
      exposure:
        include: health,info
