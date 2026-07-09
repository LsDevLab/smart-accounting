package com.lsdevlab.smart_accounting_master_data.dto.request;

import com.lsdevlab.smart_accounting_master_data.model.Customer;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
@AllArgsConstructor
@Data
@Builder
public class CreateCustomerRequestDTO {

    @NotNull
    private String name;

    private String description;

    public Customer toEntity() {
        return Customer.builder()
                .name(name)
                .description(description)
                .build();
    }
}
