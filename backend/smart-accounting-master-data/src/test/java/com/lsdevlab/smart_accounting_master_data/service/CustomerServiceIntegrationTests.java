package com.lsdevlab.smart_accounting_master_data.service;

import com.lsdevlab.smart_accounting_master_data.exception.CustomerNotFoundException;
import com.lsdevlab.smart_accounting_master_data.model.Customer;
import com.lsdevlab.smart_accounting_master_data.repository.CustomerRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.data.domain.PageRequest;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@Transactional
class CustomerServiceIntegrationTests {

    @Autowired
    private CustomerService customerService;

    @Autowired
    private CustomerRepository customerRepository;


    private Customer createTestCustomer() {
        Customer customer = new Customer();
        customer.setName("Integration Customer");
        return customer;
    }


    @Test
    void createCustomer_shouldPersistCustomer() {
        Customer customer = createTestCustomer();
        // testing creation
        Customer saved = customerService.createCustomer(customer);
        assertNotNull(saved.getId());
        Customer fromDb = customerRepository
                .findById(saved.getId())
                .orElseThrow();

        assertEquals("Integration Customer", fromDb.getName());
    }


    @Test
    void getCustomer_shouldRetrievePersistedCustomer() throws CustomerNotFoundException {
        Customer saved = customerService.createCustomer(createTestCustomer());
        Customer result = customerService.getCustomer(saved.getId());

        assertEquals(saved.getId(), result.getId());
        assertEquals("Integration Customer", result.getName());
    }


    @Test
    void getCustomer_shouldThrowWhenCustomerDoesNotExist() {
        UUID randomId = UUID.randomUUID();

        assertThrows(CustomerNotFoundException.class, () -> customerService.getCustomer(randomId));
    }


    @Test
    void patchCustomer_shouldUpdateExistingCustomer() throws CustomerNotFoundException {
        Customer saved = customerService.createCustomer(createTestCustomer());
        Customer patch = new Customer();
        patch.setName("Updated Customer");
        Customer updated = customerService.patchCustomer(saved.getId(), patch);

        assertEquals("Updated Customer", updated.getName());
        Customer fromDb = customerRepository.findById(saved.getId()).orElseThrow();
        assertEquals("Updated Customer", fromDb.getName());
    }


    @Test
    void deleteCustomer_shouldRemoveCustomer() throws CustomerNotFoundException {
        Customer saved = customerService.createCustomer(createTestCustomer());
        customerService.deleteCustomer(saved.getId());

        assertFalse(customerRepository.existsById(saved.getId()));
    }


    @Test
    void getCustomers_shouldReturnCustomers() {
        customerService.createCustomer(createTestCustomer());
        var result = customerService.getCustomers(PageRequest.of(0, 10));

        assertFalse(result.isEmpty());
    }
}