package com.lsdevlab.smart_accounting_master_data.controller;

import com.lsdevlab.smart_accounting_master_data.dto.request.CreateCustomerRequestDTO;
import com.lsdevlab.smart_accounting_master_data.dto.request.PatchCustomerRequestDTO;
import com.lsdevlab.smart_accounting_master_data.dto.response.CreateCustomerResponseDTO;
import com.lsdevlab.smart_accounting_master_data.dto.response.DeleteCustomerResponseDTO;
import com.lsdevlab.smart_accounting_master_data.dto.response.GetCustomerResponseDTO;
import com.lsdevlab.smart_accounting_master_data.dto.response.PatchCustomerResponseDTO;
import com.lsdevlab.smart_accounting_master_data.exception.CustomerNotFoundException;
import com.lsdevlab.smart_accounting_master_data.service.CustomerService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/api/mater-data/customer")
@RequiredArgsConstructor
public class CustomerController {

    private final CustomerService customerService;

    @GetMapping("/")
    public ResponseEntity<Page<GetCustomerResponseDTO>> getCustomers(Pageable pageable) {
        return ResponseEntity.ok(customerService.getCustomers(pageable).map(GetCustomerResponseDTO::fromEntity));
    }

    @GetMapping("/{id}")
    public ResponseEntity<GetCustomerResponseDTO> getCustomers(UUID id) throws CustomerNotFoundException {
        return ResponseEntity.ok(
                GetCustomerResponseDTO.fromEntity(customerService.getCustomer(id))
        );
    }

    @PostMapping("/")
    public ResponseEntity<CreateCustomerResponseDTO> createCustomer(CreateCustomerRequestDTO createCustomerRequestDTO) {
        return ResponseEntity.status(HttpStatus.CREATED).body(
                CreateCustomerResponseDTO.fromEntity(customerService.createCustomer(createCustomerRequestDTO.toEntity()))
        );
    }

    @PatchMapping("/{id}")
    public ResponseEntity<PatchCustomerResponseDTO> patchCustomer(UUID id, PatchCustomerRequestDTO patchCustomerRequestDTO) throws CustomerNotFoundException {
        return ResponseEntity.ok(
                PatchCustomerResponseDTO.fromEntity(customerService.patchCustomer(id, patchCustomerRequestDTO.toEntity()))
        );
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<DeleteCustomerResponseDTO> deleteCustomer(UUID id) throws CustomerNotFoundException {
        customerService.deleteCustomer(id);
        return ResponseEntity.ok(DeleteCustomerResponseDTO.builder().id(id).build());
    }


}
