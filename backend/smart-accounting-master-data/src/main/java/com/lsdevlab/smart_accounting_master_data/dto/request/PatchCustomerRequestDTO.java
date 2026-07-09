package com.lsdevlab.smart_accounting_master_data.dto.request;

import com.lsdevlab.smart_accounting_master_data.model.Customer;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
@AllArgsConstructor
@Data
public class PatchCustomerRequestDTO {

    private String name;

    private String description;

    public Customer toEntity() {
        return Customer.builder()
                .name(name)
                .description(description)
                .build();
    }

}
