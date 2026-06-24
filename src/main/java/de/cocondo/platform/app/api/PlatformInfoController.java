package de.cocondo.platform.app.api;

import java.time.OffsetDateTime;
import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/platform")
public class PlatformInfoController {

    private final String applicationName;
    private final String platformVersion;

    public PlatformInfoController(
            @Value("${spring.application.name:springmaster}") String applicationName,
            @Value("${springmaster.platform.version:0.1.0-bootstrap}") String platformVersion
    ) {
        this.applicationName = applicationName;
        this.platformVersion = platformVersion;
    }

    @GetMapping("/info")
    public Map<String, Object> info() {
        return Map.of(
                "application", applicationName,
                "platformVersion", platformVersion,
                "status", "BOOTSTRAP",
                "timestamp", OffsetDateTime.now().toString()
        );
    }
}
