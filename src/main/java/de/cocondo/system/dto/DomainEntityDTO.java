package de.cocondo.system.dto;

public interface DomainEntityDTO extends DTO {

    DomainEntityMetadataDTO getMetadata();

    void setMetadata(DomainEntityMetadataDTO metadata);
}
