package de.cocondo.platform.app;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@SpringBootApplication(scanBasePackages = {
        "de.cocondo.platform",
        "de.cocondo.system"
})
@EntityScan(basePackages = {
        "de.cocondo.platform.demo",
        "de.cocondo.system"
})
@EnableJpaRepositories(basePackages = "de.cocondo.platform.demo")
public class SpringmasterApplication {

    public static void main(String[] args) {
        SpringApplication.run(SpringmasterApplication.class, args);
    }
}
