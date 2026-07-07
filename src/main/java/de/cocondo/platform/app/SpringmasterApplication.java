package de.cocondo.platform.app;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = {
        "de.cocondo.platform",
        "de.cocondo.system"
})
public class SpringmasterApplication {

    public static void main(String[] args) {
        SpringApplication.run(SpringmasterApplication.class, args);
    }
}
