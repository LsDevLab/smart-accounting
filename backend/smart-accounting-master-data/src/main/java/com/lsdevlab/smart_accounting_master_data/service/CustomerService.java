package com.lsdevlab.smart_accounting_master_data.service;

import com.lsdevlab.smart_accounting_master_data.exception.CustomerNotFoundException;
import com.lsdevlab.smart_accounting_master_data.model.Customer;
import com.lsdevlab.smart_accounting_master_data.repository.CustomerRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.dao.EmptyResultDataAccessException;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.UUID;

/**
 * Service layer responsible for managing customer-related business operations.
 *
 * <p>This service provides the application logic for creating, retrieving,
 * updating and deleting {@link Customer} entities. It acts as an abstraction
 * layer between controllers and the persistence layer represented by
 * {@link CustomerRepository}.</p>
 *
 * <p>The service is responsible for enforcing business rules such as:
 * <ul>
 *     <li>Removing externally provided identifiers when creating a new customer.</li>
 *     <li>Throwing {@link CustomerNotFoundException} when a requested customer
 *     does not exist.</li>
 *     <li>Applying partial updates to existing customer entities.</li>
 * </ul>
 *
 * @author LSDevLab
 */
@Service
@RequiredArgsConstructor
public class CustomerService {

    private final CustomerRepository customerRepository;


    /**
     * Retrieves a paginated list of customers.
     *
     * @param pageable pagination and sorting information
     * @return a page containing customers matching the requested pagination criteria
     */
    public Page<Customer> getCustomers(Pageable pageable) {
        return customerRepository.findAll(pageable);
    }


    /**
     * Retrieves a customer by its unique identifier.
     *
     * @param id unique identifier of the customer
     * @return the customer associated with the provided identifier
     * @throws CustomerNotFoundException if no customer exists with the given identifier
     */
    public Customer getCustomer(UUID id) throws CustomerNotFoundException {
        return customerRepository.findById(id)
                .orElseThrow(() -> new CustomerNotFoundException(id));
    }


    /**
     * Creates a new customer.
     *
     * <p>The identifier of the provided entity is cleared before persistence
     * to ensure that the database generates a new identifier.</p>
     *
     * @param customer customer entity to create
     * @return the persisted customer entity
     */
    public Customer createCustomer(Customer customer) {
        customer.setId(null);
        return customerRepository.save(customer);
    }


    /**
     * Deletes an existing customer by its identifier.
     *
     * @param id unique identifier of the customer to delete
     * @throws CustomerNotFoundException if no customer exists with the given identifier
     */
    public void deleteCustomer(UUID id) throws CustomerNotFoundException {
        try {
            customerRepository.deleteById(id);
        } catch (EmptyResultDataAccessException exception) {
            throw new CustomerNotFoundException(id);
        }
    }


    /**
     * Applies a partial update to an existing customer.
     *
     * <p>The existing customer is first retrieved and then updated using
     * the values provided by the input entity. Only fields managed by
     * {@link Customer#patchFromEntity(Customer)} are modified.</p>
     *
     * @param id identifier of the customer to update
     * @param customer entity containing the fields to update
     * @return the updated and persisted customer entity
     * @throws CustomerNotFoundException if no customer exists with the given identifier
     */
    public Customer patchCustomer(UUID id, Customer customer) throws CustomerNotFoundException {
        Customer existingCustomer = getCustomer(id);
        existingCustomer.patchFromEntity(customer);
        return customerRepository.save(existingCustomer);
    }

}