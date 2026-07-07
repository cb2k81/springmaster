package de.cocondo.platform.demo.catalog;

public class CatalogItemNotFoundException extends RuntimeException {

    public CatalogItemNotFoundException(String message) {
        super(message);
    }
}
