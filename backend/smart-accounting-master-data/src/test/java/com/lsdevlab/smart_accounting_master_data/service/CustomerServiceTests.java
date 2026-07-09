package com.lsdevlab.smart_accounting_master_data.service;

import com.lsdevlab.smart_accounting_master_data.exception.CustomerNotFoundException;
import com.lsdevlab.smart_accounting_master_data.model.Customer;
import com.lsdevlab.smart_accounting_master_data.repository.CustomerRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.data.domain.*;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CustomerServiceTests {

    // the class to test
    @InjectMocks
    private CustomerService customerService;

    // the mock to provide to the class to test
    @Mock
    private CustomerRepository customerRepository;

    private UUID customerId;
    private Customer customer;

    @BeforeEach
    void setUp() {
        customerId = UUID.randomUUID();

        customer = new Customer();
        customer.setId(customerId);
        customer.setName("Acme Ltd");
        // populate any other mandatory fields here
    }

    @Test
    void getCustomer_shouldReturnCustomer() throws Exception {
        when(customerRepository.findById(customerId))
                .thenReturn(Optional.of(customer));

        Customer result = customerService.getCustomer(customerId);

        assertEquals(customer, result);
        verify(customerRepository).findById(customerId);
    }

    @Test
    void getCustomer_shouldThrowCustomerNotFoundException() {
        when(customerRepository.findById(customerId))
                .thenReturn(Optional.empty());

        assertThrows(
                CustomerNotFoundException.class,
                () -> customerService.getCustomer(customerId)
        );

        verify(customerRepository).findById(customerId);
    }

    @Test
    void deleteCustomer_shouldDeleteCustomer() throws Exception {
        doNothing().when(customerRepository).deleteById(customerId);

        customerService.deleteCustomer(customerId);

        verify(customerRepository).deleteById(customerId);
    }

    @Test
    void deleteCustomer_shouldThrowCustomerNotFoundException() {
        doThrow(new EmptyResultDataAccessException(1))
                .when(customerRepository)
                .deleteById(customerId);

        assertThrows(
                CustomerNotFoundException.class,
                () -> customerService.deleteCustomer(customerId)
        );

        verify(customerRepository).deleteById(customerId);
    }

    @Test
    void patchCustomer_shouldPatchAndSave() throws Exception {
        Customer patch = new Customer();
        patch.setName("Updated Name");
        when(customerRepository.findById(customerId))
                .thenReturn(Optional.of(customer));
        when(customerRepository.save(any(Customer.class)))
                .thenAnswer(invocation -> invocation.getArgument(0));

        Customer updated = customerService.patchCustomer(customerId, patch);

        assertEquals("Updated Name", updated.getName());
        verify(customerRepository).findById(customerId);
        verify(customerRepository).save(customer);
    }

    @Test
    void patchCustomer_shouldThrowCustomerNotFoundException() {
        Customer patch = new Customer();
        when(customerRepository.findById(customerId))
                .thenReturn(Optional.empty());

        assertThrows(
                CustomerNotFoundException.class,
                () -> customerService.patchCustomer(customerId, patch)
        );

        verify(customerRepository).findById(customerId);
        verify(customerRepository, never()).save(any());
    }
}