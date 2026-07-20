package de.cocondo.platform.app.version;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Properties;
import javax.xml.parsers.DocumentBuilderFactory;

import org.junit.jupiter.api.Test;
import org.w3c.dom.Document;

class PlatformVersionPropertiesTest {

    private final Path projectRoot = Path.of(System.getProperty("user.dir")).toAbsolutePath().normalize();

    @Test
    void packagedResourceMatchesCanonicalPlatformEnv() throws Exception {
        Properties canonical = new Properties();
        try (InputStream input = Files.newInputStream(projectRoot.resolve("platform/versions/platform.env"))) {
            canonical.load(input);
        }
        Properties packaged = new Properties();
        try (InputStream input = getClass().getClassLoader().getResourceAsStream(PlatformVersionProperties.RESOURCE)) {
            assertThat(input).isNotNull();
            packaged.load(input);
        }
        assertThat(packaged).containsAllEntriesOf(canonical);
        PlatformVersionProperties versions = new PlatformVersionProperties(
                canonical.stringPropertyNames().stream().collect(
                        java.util.stream.Collectors.toMap(key -> key, canonical::getProperty)
                )
        );
        assertThat(versions.platformVersion()).isEqualTo(canonical.getProperty("PLATFORM_VERSION"));
        assertThat(versions.statePatch()).isEqualTo(canonical.getProperty("PLATFORM_STATE_PATCH"));
    }

    @Test
    void mavenArtifactVersionTracksPlatformVersionAsSnapshot() throws Exception {
        Properties canonical = new Properties();
        try (InputStream input = Files.newInputStream(projectRoot.resolve("platform/versions/platform.env"))) {
            canonical.load(input);
        }
        Document document = DocumentBuilderFactory.newInstance()
                .newDocumentBuilder()
                .parse(projectRoot.resolve("pom.xml").toFile());
        String mavenVersion = document.getDocumentElement()
                .getElementsByTagName("version")
                .item(0)
                .getTextContent()
                .trim();
        assertThat(mavenVersion).isEqualTo(canonical.getProperty("PLATFORM_VERSION") + "-SNAPSHOT");
    }
}
