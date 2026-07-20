package de.cocondo.platform.app.api;

import java.time.OffsetDateTime;
import java.util.LinkedHashMap;
import java.util.Map;

import de.cocondo.platform.app.version.PlatformVersionProperties;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/platform")
public class PlatformInfoController {

    private final String applicationName;
    private final PlatformVersionProperties versions;

    public PlatformInfoController(
            @Value("${spring.application.name:springmaster}") String applicationName,
            PlatformVersionProperties versions
    ) {
        this.applicationName = applicationName;
        this.versions = versions;
    }

    @GetMapping("/info")
    public Map<String, Object> info() {
        LinkedHashMap<String, Object> response = new LinkedHashMap<>();
        response.put("application", applicationName);
        response.put("platformVersion", versions.platformVersion());
        response.put("coreVersion", versions.coreVersion());
        response.put("toolingVersion", versions.toolingVersion());
        response.put("templateVersion", versions.templateVersion());
        response.put("demoVersion", versions.demoVersion());
        response.put("updateVersion", versions.updateVersion());
        response.put("statePatch", versions.statePatch());
        response.put("status", "FOUNDATION");
        response.put("timestamp", OffsetDateTime.now().toString());
        return Map.copyOf(response);
    }
}
