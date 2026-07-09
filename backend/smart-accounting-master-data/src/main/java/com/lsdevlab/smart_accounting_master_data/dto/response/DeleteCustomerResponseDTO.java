package com.lsdevlab.smart_accounting_master_data.dto.response;

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
public class DeleteCustomerResponseDTO {

    private UUID id;
    

}
