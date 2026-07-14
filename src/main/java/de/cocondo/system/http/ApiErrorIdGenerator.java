package de.cocondo.system.http;

import java.util.UUID;
import org.springframework.stereotype.Component;

@Component
public class ApiErrorIdGenerator {

    private static final String PREFIX = "err-";

    public String nextErrorId() {
        return PREFIX + UUID.randomUUID();
    }
}
