package de.cocondo.system.dto;

import java.io.Serial;

public class DomainEntityUpdateDTO extends DomainEntityInboundDTO {

    @Serial
    private static final long serialVersionUID = 1L;

    private String id;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }
}
