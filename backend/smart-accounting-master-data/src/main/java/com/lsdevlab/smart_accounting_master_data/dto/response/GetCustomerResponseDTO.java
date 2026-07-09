package com.lsdevlab.smart_accounting_master_data.dto.response;

import com.lsdevlab.smart_accounting_master_data.model.Customer;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.RequiredArgsConstructor;

import java.time.Instant;
import java.util.UUID;

@RequiredArgsConstructor
@AllArgsConstructor
@Data
@Builder
public class GetCustomerResponseDTO {

    private UUID id;

    @NotNull
    private String name;

    private String description;

    private Instant createdAt;

    private Instant updatedAt;

    public static GetCustomerResponseDTO fromEntity(Customer customer) {
        return GetCustomerResponseDTO.builder()
                .id(customer.getId())
                .name(customer.getName())
                .description(customer.getDescription())
                .createdAt(customer.getCreatedAt())
                .updatedAt(customer.getUpdatedAt())
                .build();
    }

}
