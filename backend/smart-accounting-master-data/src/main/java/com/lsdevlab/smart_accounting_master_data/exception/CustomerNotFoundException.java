package com.lsdevlab.smart_accounting_master_data.exception;

import java.util.UUID;

public class CustomerNotFoundException extends Exception {

    public CustomerNotFoundException(UUID id) {
        super("No customer found with id" + id);
    }

}
