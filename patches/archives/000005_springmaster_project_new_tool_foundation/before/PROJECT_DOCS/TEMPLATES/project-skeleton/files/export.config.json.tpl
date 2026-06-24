{
  "projectKey": "__PROJECT_NAME__",
  "defaultProfile": "full",
  "profiles": {
    "full": {
      "include": [
        "README.md",
        "pom.xml",
        ".gitignore",
        ".env.example",
        "export.config.json",
        "bin/**",
        "docs/**",
        "PROJECT_DOCS/**",
        "platform/**",
        "src/**",
        "patches/logs/**"
      ],
      "exclude": [
        "target/**",
        "tmp/**",
        "exports/**",
        ".env",
        ".idea/**"
      ]
    }
  }
}
