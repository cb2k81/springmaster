package de.cocondo.platform.app.version;

import java.io.IOException;
import java.io.InputStream;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Objects;
import java.util.Properties;

import org.springframework.stereotype.Component;

/**
 * Loads the packaged Springmaster platform version contract.
 */
@Component
public final class PlatformVersionProperties {

    public static final String RESOURCE = "META-INF/springmaster/platform.env";

    private static final String[] REQUIRED_KEYS = {
            "PLATFORM_NAME",
            "PLATFORM_VERSION",
            "PLATFORM_CORE_VERSION",
            "PLATFORM_TOOLING_VERSION",
            "PLATFORM_TEMPLATE_VERSION",
            "PLATFORM_DEMO_VERSION",
            "PLATFORM_UPDATE_VERSION",
            "PLATFORM_STATE_PATCH",
            "PLATFORM_BASELINE_KIND",
            "PLATFORM_BASE_PACKAGE",
            "PLATFORM_CORE_PACKAGE"
    };

    private final Map<String, String> values;

    public PlatformVersionProperties() {
        this(loadResource());
    }

    PlatformVersionProperties(Map<String, String> values) {
        LinkedHashMap<String, String> normalized = new LinkedHashMap<>();
        for (String key : REQUIRED_KEYS) {
            String value = Objects.requireNonNull(values.get(key), "Missing platform version key: " + key).trim();
            if (value.isEmpty()) {
                throw new IllegalStateException("Empty platform version key: " + key);
            }
            normalized.put(key, value);
        }
        this.values = Map.copyOf(normalized);
    }

    public String platformName() {
        return values.get("PLATFORM_NAME");
    }

    public String platformVersion() {
        return values.get("PLATFORM_VERSION");
    }

    public String coreVersion() {
        return values.get("PLATFORM_CORE_VERSION");
    }

    public String toolingVersion() {
        return values.get("PLATFORM_TOOLING_VERSION");
    }

    public String templateVersion() {
        return values.get("PLATFORM_TEMPLATE_VERSION");
    }

    public String demoVersion() {
        return values.get("PLATFORM_DEMO_VERSION");
    }

    public String updateVersion() {
        return values.get("PLATFORM_UPDATE_VERSION");
    }

    public String statePatch() {
        return values.get("PLATFORM_STATE_PATCH");
    }

    public Map<String, String> asMap() {
        return values;
    }

    private static Map<String, String> loadResource() {
        ClassLoader classLoader = PlatformVersionProperties.class.getClassLoader();
        try (InputStream input = classLoader.getResourceAsStream(RESOURCE)) {
            if (input == null) {
                throw new IllegalStateException("Missing packaged platform version resource: " + RESOURCE);
            }
            Properties properties = new Properties();
            properties.load(input);
            LinkedHashMap<String, String> loaded = new LinkedHashMap<>();
            for (String key : REQUIRED_KEYS) {
                loaded.put(key, properties.getProperty(key));
            }
            return loaded;
        } catch (IOException exception) {
            throw new IllegalStateException("Cannot read packaged platform version resource: " + RESOURCE, exception);
        }
    }
}
