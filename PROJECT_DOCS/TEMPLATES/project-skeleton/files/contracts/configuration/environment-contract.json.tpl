{
  "schema": "springmaster.environment-contract.v1",
  "project": "__PROJECT_NAME__",
  "supportedProfiles": [
    "dev",
    "test",
    "build",
    "prod"
  ],
  "defaultProfile": "dev",
  "sources": {
    "defaults": ".env.example",
    "localOverrides": ".env",
    "shellLoader": "bin/lib/core/env.sh",
    "springRuntime": "src/main/resources/application.yml",
    "documentedTemplate": "PROJECT_DOCS/CONFIG/ENV_TEMPLATE.env"
  },
  "variables": [
    {
      "name": "APP_NAME",
      "type": "string",
      "required": true,
      "secret": false,
      "default": "__PROJECT_NAME__",
      "consumers": [
        "shell",
        "export",
        "runtime"
      ]
    },
    {
      "name": "APP_EXPORT_PROJECT_KEY",
      "type": "string",
      "required": true,
      "secret": false,
      "default": "__PROJECT_NAME__",
      "consumers": [
        "shell",
        "export"
      ]
    },
    {
      "name": "APP_PORT",
      "type": "integer",
      "required": true,
      "secret": false,
      "default": "__HTTP_PORT__",
      "minimum": 1,
      "maximum": 65535,
      "consumers": [
        "shell",
        "runtime"
      ]
    },
    {
      "name": "APP_PROFILE",
      "type": "enum",
      "required": true,
      "secret": false,
      "default": "dev",
      "allowed": [
        "dev",
        "test",
        "build",
        "prod"
      ],
      "consumers": [
        "shell",
        "runtime"
      ]
    },
    {
      "name": "APP_BASE_PACKAGE",
      "type": "java-package",
      "required": true,
      "secret": false,
      "default": "__BASE_PACKAGE__",
      "consumers": [
        "shell",
        "project-new"
      ]
    },
    {
      "name": "APP_CORE_PACKAGE",
      "type": "java-package",
      "required": true,
      "secret": false,
      "default": "de.cocondo.system",
      "consumers": [
        "shell",
        "project-new"
      ]
    },
    {
      "name": "APP_DB_HOST",
      "type": "string",
      "required": true,
      "secret": false,
      "default": "localhost",
      "consumers": [
        "shell",
        "dbtool"
      ]
    },
    {
      "name": "APP_DB_PORT",
      "type": "integer",
      "required": true,
      "secret": false,
      "default": "3306",
      "minimum": 1,
      "maximum": 65535,
      "consumers": [
        "shell",
        "dbtool"
      ]
    },
    {
      "name": "APP_DEV_DB_NAME",
      "type": "database-identifier",
      "required": true,
      "secret": false,
      "default": "__DB_NAME__",
      "consumers": [
        "shell",
        "dbtool"
      ]
    },
    {
      "name": "APP_DEV_DB_USER",
      "type": "string",
      "required": true,
      "secret": false,
      "default": "__DB_NAME__",
      "consumers": [
        "shell",
        "dbtool"
      ]
    },
    {
      "name": "APP_DEV_DB_PASS",
      "type": "string",
      "required": true,
      "secret": true,
      "default": "__DB_NAME__",
      "productionDefaultAllowed": false,
      "consumers": [
        "shell",
        "dbtool"
      ]
    },
    {
      "name": "APP_STAGE_DB_NAME",
      "type": "database-identifier",
      "required": true,
      "secret": false,
      "default": "__STAGE_DB_NAME__",
      "consumers": [
        "shell",
        "dbtool"
      ]
    },
    {
      "name": "APP_STAGE_DB_USER",
      "type": "string",
      "required": true,
      "secret": false,
      "default": "__DB_NAME__",
      "consumers": [
        "shell",
        "dbtool"
      ]
    },
    {
      "name": "APP_STAGE_DB_PASS",
      "type": "string",
      "required": true,
      "secret": true,
      "default": "__DB_NAME__",
      "productionDefaultAllowed": false,
      "consumers": [
        "shell",
        "dbtool"
      ]
    },
    {
      "name": "APP_DB_ADMIN_USER",
      "type": "string",
      "required": true,
      "secret": false,
      "default": "root",
      "consumers": [
        "shell",
        "dbtool"
      ]
    },
    {
      "name": "APP_DB_ADMIN_PASS",
      "type": "string",
      "required": false,
      "secret": true,
      "default": "",
      "productionDefaultAllowed": false,
      "consumers": [
        "shell",
        "dbtool"
      ]
    },
    {
      "name": "APP_CHANGELOG_DIR",
      "type": "relative-path",
      "required": true,
      "secret": false,
      "default": "src/main/resources/db/changelog",
      "consumers": [
        "shell",
        "dbtool"
      ]
    },
    {
      "name": "APP_CHANGELOG_MASTER",
      "type": "relative-path",
      "required": true,
      "secret": false,
      "default": "src/main/resources/db/changelog/db.changelog-master.xml",
      "consumers": [
        "shell",
        "dbtool"
      ]
    },
    {
      "name": "APP_LIQUIBASE_CONTEXTS",
      "type": "string",
      "required": false,
      "secret": false,
      "default": "",
      "consumers": [
        "shell",
        "dbtool"
      ]
    },
    {
      "name": "APP_LIQUIBASE_ENABLED",
      "type": "boolean",
      "required": true,
      "secret": false,
      "default": "false",
      "consumers": [
        "shell",
        "runtime",
        "dbtool"
      ]
    },
    {
      "name": "APP_OPENAPI_PATH",
      "type": "http-path",
      "required": true,
      "secret": false,
      "default": "/api-docs",
      "consumers": [
        "shell",
        "runtime"
      ]
    },
    {
      "name": "APP_EXPORT_CONFIG_FILE",
      "type": "relative-path",
      "required": true,
      "secret": false,
      "default": "export.config.json",
      "consumers": [
        "shell",
        "export"
      ]
    },
    {
      "name": "APP_BUILD_REMOTE_DEPLOY_ENABLED",
      "type": "boolean",
      "required": true,
      "secret": false,
      "default": "false",
      "consumers": [
        "shell",
        "build"
      ]
    },
    {
      "name": "APP_BUILD_CONSOLE_MODE",
      "type": "enum",
      "required": true,
      "secret": false,
      "default": "compact",
      "allowed": [
        "compact",
        "verbose"
      ],
      "consumers": [
        "shell",
        "build"
      ]
    },
    {
      "name": "APP_DIST_DIR",
      "type": "relative-path",
      "required": true,
      "secret": false,
      "default": "target/dist",
      "consumers": [
        "shell",
        "build"
      ]
    },
    {
      "name": "APP_DBTOOL_ALLOW_DESTRUCTIVE",
      "type": "boolean",
      "required": true,
      "secret": false,
      "default": "false",
      "consumers": [
        "shell",
        "dbtool"
      ]
    },
    {
      "name": "LOG_LEVEL",
      "type": "enum",
      "required": true,
      "secret": false,
      "default": "INFO",
      "allowed": [
        "TRACE",
        "DEBUG",
        "INFO",
        "WARN",
        "ERROR"
      ],
      "consumers": [
        "shell",
        "runtime"
      ]
    }
  ],
  "allowedUndeclaredPrefixes": [
    "PATCH_"
  ]
}
