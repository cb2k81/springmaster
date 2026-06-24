package __BASE_PACKAGE__.app.api;

import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/platform")
public class PlatformInfoController {

    private final String applicationName;

    public PlatformInfoController(@Value("${spring.application.name:__PROJECT_NAME__}") String applicationName) {
        this.applicationName = applicationName;
    }

    @GetMapping("/info")
    public Map<String, String> info() {
        return Map.of(
            "application", applicationName,
            "platformVersion", "__PLATFORM_VERSION__",
            "coreVersion", "__CORE_VERSION__",
            "toolingVersion", "__TOOLING_VERSION__"
        );
    }
}
