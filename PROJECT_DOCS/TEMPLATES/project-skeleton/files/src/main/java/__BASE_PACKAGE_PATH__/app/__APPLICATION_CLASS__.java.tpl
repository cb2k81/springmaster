package __BASE_PACKAGE__.app;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = {
        "__BASE_PACKAGE__",
        "de.cocondo.system"
})
public class __APPLICATION_CLASS__ {

    public static void main(String[] args) {
        SpringApplication.run(__APPLICATION_CLASS__.class, args);
    }
}
