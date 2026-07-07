package de.cocondo.system.dto;

import java.io.Serial;
import java.util.Set;

import com.fasterxml.jackson.annotation.JsonIgnore;
import de.cocondo.system.entity.metadata.KeyValuePairDTO;
import jakarta.validation.ValidationException;

public abstract class DomainEntityInboundDTO implements DTO {

    @Serial
    private static final long serialVersionUID = 1L;

    private Set<String> tags;
    private Set<KeyValuePairDTO> keyValuePairs;

    public Set<String> getTags() {
        return tags;
    }

    public void setTags(Set<String> tags) {
        this.tags = tags;
    }

    public Set<KeyValuePairDTO> getKeyValuePairs() {
        return keyValuePairs;
    }

    public void setKeyValuePairs(Set<KeyValuePairDTO> keyValuePairs) {
        this.keyValuePairs = keyValuePairs;
    }

    public void validate() {
    }

    @JsonIgnore
    public boolean isValid() {
        try {
            validate();
            return true;
        } catch (ValidationException exception) {
            return false;
        }
    }
}
