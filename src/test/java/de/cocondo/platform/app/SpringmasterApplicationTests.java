package de.cocondo.platform.app;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

@ActiveProfiles("test")
@SpringBootTest
class SpringmasterApplicationTests {

    @Test
    void contextLoads() {
    }

    @Test
    void scansPlatformAndSystemPackages() {
        SpringBootApplication annotation = SpringmasterApplication.class.getAnnotation(SpringBootApplication.class);

        assertThat(annotation.scanBasePackages()).containsExactly("de.cocondo.platform", "de.cocondo.system");
    }
}
