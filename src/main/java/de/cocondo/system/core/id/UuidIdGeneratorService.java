package de.cocondo.system.core.id;

import java.util.UUID;

import org.springframework.stereotype.Service;

/**
 * Default technical UUID-based ID generator for shared Core consumers.
 */
@Service
public class UuidIdGeneratorService implements IdGeneratorService {

    @Override
    public String generateId() {
        return UUID.randomUUID().toString();
    }
}
